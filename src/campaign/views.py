from typing import Any
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods

from campaign.forms import (
    CampaignCreateForm,
    CatastrophicEventDefForm,
    CraftingForm,
    CraftingRecipeDefForm,
    ExpeditionForm,
    HazardDefForm,
    HeroActionForm,
    HeroCreateForm,
    PartyCreateForm,
    ShopTransactionForm,
    SettlementLocationDefForm,
    SettlementEventDefForm,
    TravelForm,
)
from campaign.models import (
    Campaign,
    CatastrophicEventDef,
    CraftingRecipeDef,
    Expedition,
    ExpeditionDef,
    HazardDef,
    Hero,
    HeroSkill,
    InventoryItem,
    ItemDef,
    Party,
    SettlementEventDef,
    SettlementLocationDef,
    SkillDef,
    StepLog,
)
from campaign.services.crafting import resolve_crafting
from campaign.services.expedition import resolve_expedition
from campaign.services.economy import process_shop_transaction
from campaign.services.crafting import get_hero_carry_capacity, get_hero_carry_weight
from campaign.services.audit import log_campaign_mutation
from campaign.services.settlement import resolve_settlement_action
from campaign.services.travel import resolve_travel_hazards


ROUTE_CAMPAIGN_DETAIL = "campaign:campaign_detail"
ROUTE_GM_CONSOLE = "campaign:gm_console"
ROUTE_DASHBOARD = "campaign:dashboard"
NO_PARTY_MESSAGE = "Campaign has no party yet"
DEFAULT_GM_SOURCE_FILTER = "whq_roleplay_book"
GM_FORM_CONFIG = (
    ("hazard", "hazard_form", HazardDefForm, "hazard"),
    ("settlement", "settlement_event_form", SettlementEventDefForm, "settlement"),
    ("catastrophic", "catastrophic_form", CatastrophicEventDefForm, "catastrophic"),
    ("location", "location_form", SettlementLocationDefForm, "location"),
    (
        "crafting_recipe",
        "crafting_recipe_form",
        CraftingRecipeDefForm,
        "crafting_recipe",
    ),
)


def _build_gm_console_forms(post_data: Any | None = None) -> dict[str, Any]:
    form_kind = post_data.get("form_kind") if post_data is not None else None
    forms: dict[str, Any] = {}
    for expected_kind, context_key, form_class, prefix in GM_FORM_CONFIG:
        if post_data is not None and form_kind == expected_kind:
            forms[context_key] = form_class(post_data, prefix=prefix)
        else:
            forms[context_key] = form_class(prefix=prefix)
    return forms


def _handle_gm_console_post(
    post_data: Any,
) -> tuple[dict[str, Any], HttpResponse | None]:
    forms = _build_gm_console_forms(post_data)
    form_kind = post_data.get("form_kind")

    for form_config in GM_FORM_CONFIG:
        expected_kind = form_config[0]
        context_key = form_config[1]
        if form_kind != expected_kind:
            continue

        form = forms[context_key]
        if form.is_valid():
            form.save()
            return forms, redirect(ROUTE_GM_CONSOLE)
        break

    return forms, None


def _get_gm_console_content(
    source_filter: str,
    hazard_roll_filter: str,
    settlement_roll_filter: str,
    catastrophic_roll_filter: str,
) -> dict[str, Any]:
    hazard_queryset = HazardDef.objects.all()
    settlement_queryset = SettlementEventDef.objects.all()
    catastrophic_queryset = CatastrophicEventDef.objects.all()

    if source_filter:
        hazard_queryset = hazard_queryset.filter(definition__source=source_filter)
        settlement_queryset = settlement_queryset.filter(
            definition__source=source_filter
        )
        catastrophic_queryset = catastrophic_queryset.filter(
            definition__source=source_filter
        )

    if hazard_roll_filter:
        hazard_queryset = hazard_queryset.filter(
            definition__table_roll__icontains=hazard_roll_filter
        )
    if settlement_roll_filter:
        settlement_queryset = settlement_queryset.filter(
            definition__table_roll__icontains=settlement_roll_filter
        )
    if catastrophic_roll_filter:
        catastrophic_queryset = catastrophic_queryset.filter(
            definition__table_roll__icontains=catastrophic_roll_filter
        )

    return {
        "hazards": sorted(
            hazard_queryset,
            key=lambda item: (
                item.definition.get("table_roll", ""),
                item.settlement_size,
                item.name,
            ),
        ),
        "settlement_events": sorted(
            settlement_queryset,
            key=lambda item: (item.definition.get("table_roll", ""), item.name),
        ),
        "catastrophic_events": sorted(
            catastrophic_queryset,
            key=lambda item: (item.definition.get("table_roll", ""), item.name),
        ),
        "settlement_locations": SettlementLocationDef.objects.order_by("code", "name"),
        "crafting_recipes": CraftingRecipeDef.objects.order_by("code"),
    }


def _serialise_campaign(campaign: Campaign) -> dict[str, Any]:
    parties = list(Party.objects.filter(campaign=campaign).order_by("id"))
    heroes = list(Hero.objects.filter(party__campaign=campaign).order_by("id"))
    inventory_items = list(
        InventoryItem.objects.filter(party__campaign=campaign)
        .select_related("item_def", "party", "hero")
        .order_by("id")
    )
    hero_skills = list(
        HeroSkill.objects.filter(hero__party__campaign=campaign)
        .select_related("hero", "skill_def")
        .order_by("id")
    )
    expeditions = list(
        Expedition.objects.filter(campaign=campaign)
        .select_related("party", "expedition_def")
        .order_by("id")
    )
    step_logs = list(
        StepLog.objects.filter(campaign=campaign).order_by("created_at", "id")
    )

    return {
        "version": 1,
        "campaign": {
            "name": campaign.name,
            "seed": campaign.seed,
            "owner": campaign.owner.username if campaign.owner else None,
            "current_day": campaign.current_day,
            "current_week": campaign.current_week,
            "is_active": campaign.is_active,
        },
        "parties": [
            {
                "legacy_id": int(party.pk),
                "name": party.name,
                "current_settlement_size": party.current_settlement_size,
                "current_location_name": party.current_location_name,
                "gold": party.gold,
                "supplies": party.supplies,
                "morale": party.morale,
                "hardship_price_multiplier": party.hardship_price_multiplier,
                "forced_departure": party.forced_departure,
                "disease_risk_active": party.disease_risk_active,
            }
            for party in parties
        ],
        "heroes": [
            {
                "legacy_id": int(hero.pk),
                "party_legacy_id": int(hero.party.pk),
                "name": hero.name,
                "archetype": hero.archetype,
                "level": hero.level,
                "max_health": hero.max_health,
                "current_health": hero.current_health,
                "conditions": hero.conditions,
                "stats": hero.stats,
                "days_unavailable": hero.days_unavailable,
                "is_waiting_outside": hero.is_waiting_outside,
                "in_disguise": hero.in_disguise,
                "has_pet_dog": hero.has_pet_dog,
                "investment_active": hero.investment_active,
                "temple_reroll_charges": hero.temple_reroll_charges,
                "alive": hero.alive,
            }
            for hero in heroes
        ],
        "inventory_items": [
            {
                "party_legacy_id": int(item.party.pk),
                "hero_legacy_id": int(item.hero.pk) if item.hero else None,
                "item_name": item.item_def.name,
                "quantity": item.quantity,
                "item_state": item.item_state,
            }
            for item in inventory_items
        ],
        "hero_skills": [
            {
                "hero_legacy_id": int(hero_skill.hero.pk),
                "skill_name": hero_skill.skill_def.name,
                "source": hero_skill.source,
            }
            for hero_skill in hero_skills
        ],
        "expeditions": [
            {
                "party_legacy_id": int(expedition.party.pk),
                "expedition_code": expedition.expedition_def.code,
                "risk_level": expedition.risk_level,
                "result": expedition.result,
            }
            for expedition in expeditions
        ],
        "step_logs": [
            {
                "party_legacy_id": int(step.party.pk) if step.party else None,
                "hero_legacy_id": int(step.hero.pk) if step.hero else None,
                "step_type": step.step_type,
                "action_type": step.action_type,
                "rng_seed": step.rng_seed,
                "dice_rolled": step.dice_rolled,
                "effects_applied": step.effects_applied,
                "narrative": step.narrative,
            }
            for step in step_logs
        ],
    }


def _build_unique_import_seed(base_seed: str) -> str:
    candidate = f"{base_seed}-import"
    if not Campaign.objects.filter(seed=candidate).exists():
        return candidate

    while True:
        suffix = get_random_string(6).lower()
        candidate = f"{base_seed}-import-{suffix}"
        if not Campaign.objects.filter(seed=candidate).exists():
            return candidate


def _parse_int(value: Any) -> int | None:
    """Safely parse integers from import payload values."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _import_campaign_day(value: Any, fallback: int) -> int:
    parsed = _parse_int(value)
    if parsed is None:
        return fallback
    return max(1, parsed)


def _import_parties(
    payload: dict[str, Any], imported_campaign: Campaign
) -> dict[int, Party]:
    party_map: dict[int, Party] = {}
    for party_data in payload.get("parties", []):
        legacy_party_id = _parse_int(party_data.get("legacy_id"))
        if legacy_party_id is None:
            continue
        party = Party.objects.create(
            campaign=imported_campaign,
            name=str(party_data.get("name", "Imported Party")),
            current_settlement_size=str(
                party_data.get("current_settlement_size", Party.SettlementSize.VILLAGE)
            ),
            current_location_name=str(
                party_data.get("current_location_name", "Village")
            ),
            gold=_parse_int(party_data.get("gold", 0)) or 0,
            supplies=_parse_int(party_data.get("supplies", 0)) or 0,
            morale=_parse_int(party_data.get("morale", 0)) or 0,
            hardship_price_multiplier=_parse_int(
                party_data.get("hardship_price_multiplier", 1)
            )
            or 1,
            forced_departure=bool(party_data.get("forced_departure", False)),
            disease_risk_active=bool(party_data.get("disease_risk_active", False)),
        )
        party_map[legacy_party_id] = party
    return party_map


def _import_heroes(
    payload: dict[str, Any], party_map: dict[int, Party]
) -> dict[int, Hero]:
    hero_map: dict[int, Hero] = {}
    for hero_data in payload.get("heroes", []):
        legacy_party_id = _parse_int(hero_data.get("party_legacy_id"))
        if legacy_party_id is None:
            continue
        party = party_map.get(legacy_party_id)
        if party is None:
            continue
        legacy_hero_id = _parse_int(hero_data.get("legacy_id"))
        if legacy_hero_id is None:
            continue
        hero = Hero.objects.create(
            party=party,
            name=str(hero_data.get("name", "Imported Hero")),
            archetype=str(hero_data.get("archetype", Hero.Archetype.WARRIOR)),
            level=_parse_int(hero_data.get("level", 1)) or 1,
            max_health=_parse_int(hero_data.get("max_health", 10)) or 10,
            current_health=_parse_int(hero_data.get("current_health", 10)) or 10,
            conditions=hero_data.get("conditions", []),
            stats=hero_data.get("stats", {}),
            days_unavailable=_parse_int(hero_data.get("days_unavailable", 0)) or 0,
            is_waiting_outside=bool(hero_data.get("is_waiting_outside", False)),
            in_disguise=bool(hero_data.get("in_disguise", False)),
            has_pet_dog=bool(hero_data.get("has_pet_dog", False)),
            investment_active=bool(hero_data.get("investment_active", False)),
            temple_reroll_charges=_parse_int(hero_data.get("temple_reroll_charges", 0))
            or 0,
            alive=bool(hero_data.get("alive", True)),
        )
        hero_map[legacy_hero_id] = hero
    return hero_map


def _import_inventory_items(
    payload: dict[str, Any], party_map: dict[int, Party], hero_map: dict[int, Hero]
) -> None:
    for inventory_data in payload.get("inventory_items", []):
        legacy_party_id = _parse_int(inventory_data.get("party_legacy_id"))
        if legacy_party_id is None:
            continue
        party = party_map.get(legacy_party_id)
        if party is None:
            continue
        hero_legacy_id = inventory_data.get("hero_legacy_id")
        parsed_hero_id = (
            _parse_int(hero_legacy_id) if hero_legacy_id is not None else None
        )
        if hero_legacy_id is not None and parsed_hero_id is None:
            continue
        hero = hero_map.get(parsed_hero_id) if parsed_hero_id is not None else None
        item_name = str(inventory_data.get("item_name", "")).strip()
        item_def = ItemDef.objects.filter(name=item_name).first()
        if item_def is None:
            continue

        InventoryItem.objects.create(
            party=party,
            hero=hero,
            item_def=item_def,
            quantity=max(1, _parse_int(inventory_data.get("quantity", 1)) or 1),
            item_state=inventory_data.get("item_state", {}),
        )


def _import_hero_skills(payload: dict[str, Any], hero_map: dict[int, Hero]) -> None:
    for hero_skill_data in payload.get("hero_skills", []):
        hero_legacy_id = hero_skill_data.get("hero_legacy_id")
        if hero_legacy_id is None:
            continue
        parsed_hero_id = _parse_int(hero_legacy_id)
        if parsed_hero_id is None:
            continue
        hero = hero_map.get(parsed_hero_id)
        if hero is None:
            continue
        skill_name = str(hero_skill_data.get("skill_name", "")).strip()
        skill_def = SkillDef.objects.filter(name=skill_name).first()
        if skill_def is None:
            continue
        HeroSkill.objects.get_or_create(
            hero=hero,
            skill_def=skill_def,
            defaults={"source": str(hero_skill_data.get("source", "import"))},
        )


def _import_expeditions(
    payload: dict[str, Any],
    imported_campaign: Campaign,
    party_map: dict[int, Party],
) -> None:
    for expedition_data in payload.get("expeditions", []):
        legacy_party_id = expedition_data.get("party_legacy_id")
        if legacy_party_id is None:
            continue
        parsed_party_id = _parse_int(legacy_party_id)
        if parsed_party_id is None:
            continue
        party = party_map.get(parsed_party_id)
        if party is None:
            continue
        expedition_code = str(expedition_data.get("expedition_code", "")).strip()
        expedition_def = ExpeditionDef.objects.filter(code=expedition_code).first()
        if expedition_def is None:
            continue
        Expedition.objects.create(
            campaign=imported_campaign,
            party=party,
            expedition_def=expedition_def,
            risk_level=str(
                expedition_data.get("risk_level", Expedition.RiskLevel.STANDARD)
            ),
            result=expedition_data.get("result", {}),
        )


def _import_step_logs(
    payload: dict[str, Any],
    imported_campaign: Campaign,
    party_map: dict[int, Party],
    hero_map: dict[int, Hero],
) -> None:
    for step_data in payload.get("step_logs", []):
        legacy_party_id = step_data.get("party_legacy_id")
        legacy_hero_id = step_data.get("hero_legacy_id")
        parsed_party_id = (
            _parse_int(legacy_party_id) if legacy_party_id is not None else None
        )
        parsed_hero_id = (
            _parse_int(legacy_hero_id) if legacy_hero_id is not None else None
        )
        StepLog.objects.create(
            campaign=imported_campaign,
            party=party_map.get(parsed_party_id)
            if parsed_party_id is not None
            else None,
            hero=hero_map.get(parsed_hero_id) if parsed_hero_id is not None else None,
            step_type=str(step_data.get("step_type", "import")),
            action_type=str(step_data.get("action_type", "import")),
            rng_seed=str(step_data.get("rng_seed", "imported-seed")),
            dice_rolled=step_data.get("dice_rolled", []),
            effects_applied=step_data.get("effects_applied", {}),
            narrative=str(step_data.get("narrative", "Imported step log.")),
        )


@transaction.atomic
def _import_campaign_payload(
    payload: dict[str, Any], owner: Any | None = None
) -> Campaign:
    parties_payload = payload.get("parties", [])
    heroes_payload = payload.get("heroes", [])
    if not isinstance(parties_payload, list):
        raise ValueError("Campaign parties must be provided as a list.")
    valid_party_ids = {
        _parse_int(party_data.get("legacy_id"))
        for party_data in parties_payload
        if isinstance(party_data, dict)
        and _parse_int(party_data.get("legacy_id")) is not None
    }
    if len(valid_party_ids) > 1:
        raise ValueError("A campaign snapshot can contain at most one party.")
    if not isinstance(heroes_payload, list):
        raise ValueError("Campaign heroes must be provided as a list.")
    importable_hero_count = sum(
        isinstance(hero_data, dict)
        and _parse_int(hero_data.get("legacy_id")) is not None
        and _parse_int(hero_data.get("party_legacy_id")) in valid_party_ids
        for hero_data in heroes_payload
    )
    if importable_hero_count > 4:
        raise ValueError("A party snapshot can contain at most four heroes.")

    campaign_data = payload.get("campaign", {})
    source_name = (
        str(campaign_data.get("name", "Imported Campaign")).strip()
        or "Imported Campaign"
    )
    source_seed = (
        str(campaign_data.get("seed", "imported-seed")).strip() or "imported-seed"
    )
    current_day = _import_campaign_day(campaign_data.get("current_day", 1), 1)
    imported_campaign = Campaign.objects.create(
        name=f"{source_name} (Imported)",
        seed=_build_unique_import_seed(source_seed),
        owner=owner,
        current_day=current_day,
        current_week=((current_day - 1) // 7) + 1,
        is_active=bool(campaign_data.get("is_active", True)),
    )

    party_map = _import_parties(payload, imported_campaign)
    hero_map = _import_heroes(payload, party_map)
    _import_inventory_items(payload, party_map, hero_map)
    _import_hero_skills(payload, hero_map)
    _import_expeditions(payload, imported_campaign, party_map)
    _import_step_logs(payload, imported_campaign, party_map, hero_map)
    log_campaign_mutation(
        imported_campaign,
        "import",
        {
            "parties_imported": len(party_map),
            "heroes_imported": len(hero_map),
            "step_logs_imported": len(payload.get("step_logs", [])),
        },
        f"Campaign {imported_campaign.name} imported from a JSON snapshot.",
    )

    return imported_campaign


def _get_campaign_for_request(request: HttpRequest, campaign_id: int) -> Campaign:
    if request.user.is_authenticated and request.user.is_staff:
        return get_object_or_404(Campaign, id=campaign_id)

    if request.user.is_authenticated:
        return get_object_or_404(
            Campaign.objects.filter(id=campaign_id).filter(
                Q(owner=request.user) | Q(owner__isnull=True)
            )
        )

    return get_object_or_404(
        Campaign.objects.filter(id=campaign_id, owner__isnull=True)
    )


def _get_visible_campaigns(request: HttpRequest):
    campaigns = Campaign.objects.all()
    if request.user.is_staff:
        return campaigns
    if request.user.is_authenticated:
        return campaigns.filter(Q(owner=request.user) | Q(owner__isnull=True))
    return campaigns.filter(owner__isnull=True)


@transaction.atomic
@require_http_methods(["GET", "POST"])
def dashboard(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CampaignCreateForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            if request.user.is_authenticated:
                campaign.owner = request.user
            campaign.save()
            log_campaign_mutation(
                campaign,
                "create",
                {"name": campaign.name},
                f"Campaign {campaign.name} created.",
            )
            return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign.id)
    else:
        form = CampaignCreateForm()

    campaigns = _get_visible_campaigns(request).order_by("-updated_at")[:10]
    return render(
        request, "campaign/dashboard.html", {"form": form, "campaigns": campaigns}
    )


@transaction.atomic
@require_http_methods(["POST"])
def import_campaign(request: HttpRequest) -> HttpResponse:
    raw_payload = request.POST.get("payload", "")
    if not raw_payload and request.body:
        raw_payload = request.body.decode("utf-8")

    if not raw_payload.strip():
        messages.warning(request, "Import payload is empty.")
        return redirect(ROUTE_DASHBOARD)

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        messages.error(request, "Import payload is not valid JSON.")
        return redirect(ROUTE_DASHBOARD)

    if not isinstance(payload, dict):
        messages.error(request, "Import payload must be a JSON object.")
        return redirect(ROUTE_DASHBOARD)

    try:
        imported_campaign = _import_campaign_payload(
            payload, request.user if request.user.is_authenticated else None
        )
    except ValueError as error:
        messages.error(request, str(error))
        return redirect(ROUTE_DASHBOARD)
    messages.success(request, f"Imported campaign: {imported_campaign.name}")
    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=imported_campaign.pk)


@transaction.atomic
@require_http_methods(["GET", "POST"])
def campaign_detail(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()

    party_form = PartyCreateForm(initial={"campaign": campaign_id}, campaign=campaign)
    hero_form = HeroCreateForm(party=party)

    if request.method == "POST":
        create_type = request.POST.get("create_type")
        if create_type == "party":
            party_form = PartyCreateForm(request.POST, campaign=campaign)
            if party_form.is_valid():
                party = party_form.save()
                log_campaign_mutation(
                    campaign,
                    "party_created",
                    {"party_name": party.name},
                    f"Party {party.name} joined the campaign.",
                    party=party,
                )
                return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)
        if create_type == "hero":
            hero_form = HeroCreateForm(request.POST, party=party)
            if hero_form.is_valid():
                created_hero = hero_form.save()
                log_campaign_mutation(
                    campaign,
                    "hero_created",
                    {"hero_name": created_hero.name},
                    f"{created_hero.name} joined {created_hero.party.name}.",
                    party=created_hero.party,
                    hero=created_hero,
                )
                return redirect(
                    ROUTE_CAMPAIGN_DETAIL, campaign_id=created_hero.party.campaign_id
                )

    recent_steps = StepLog.objects.filter(campaign=campaign).order_by("-created_at")[
        :20
    ]
    latest_expedition = (
        Expedition.objects.filter(campaign=campaign).order_by("-created_at").first()
    )
    expedition_form = ExpeditionForm()
    travel_form = TravelForm()
    hero_action_form = HeroActionForm(party=party)
    shop_form = ShopTransactionForm()
    crafting_form = CraftingForm()

    return render(
        request,
        "campaign/campaign_detail.html",
        {
            "campaign": campaign,
            "party": party,
            "latest_expedition": latest_expedition,
            "party_form": party_form,
            "hero_form": hero_form,
            "expedition_form": expedition_form,
            "travel_form": travel_form,
            "hero_action_form": hero_action_form,
            "shop_form": shop_form,
            "crafting_form": crafting_form,
            "recent_steps": recent_steps,
        },
    )


@transaction.atomic
@require_http_methods(["POST"])
def rename_campaign(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    new_name = request.POST.get("name", "").strip()
    if not new_name:
        messages.warning(request, "Campaign name cannot be blank.")
        return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)

    campaign.name = new_name
    campaign.save(update_fields=["name", "updated_at"])
    log_campaign_mutation(
        campaign,
        "rename",
        {"new_name": campaign.name},
        f"Campaign renamed to {campaign.name}.",
    )
    messages.success(request, f"Campaign renamed to {new_name}.")
    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@require_http_methods(["POST"])
def delete_campaign(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    if request.POST.get("confirm_delete") != "yes":
        messages.warning(
            request, "Delete cancelled. Tick the confirmation box before deleting."
        )
        return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)
    deleted_name = campaign.name
    campaign.delete()
    messages.success(request, f"Deleted campaign: {deleted_name}.")
    return redirect(ROUTE_DASHBOARD)


@require_http_methods(["GET"])
def export_campaign(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    payload = _serialise_campaign(campaign)
    response = JsonResponse(payload, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = (
        f'attachment; filename="campaign-{campaign.pk}.json"'
    )
    return response


@require_http_methods(["POST"])
def resolve_expedition_run(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()
    if not party:
        raise Http404(NO_PARTY_MESSAGE)

    form = ExpeditionForm(request.POST)
    if form.is_valid():
        result = resolve_expedition(
            party=party,
            expedition_def=form.cleaned_data["expedition_def"],
            risk_level=form.cleaned_data["risk_level"],
        )
        message_level = messages.SUCCESS if result.get("success") else messages.WARNING
        messages.add_message(
            request, message_level, result.get("narrative", "Expedition resolved.")
        )

    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_travel(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()
    if not party:
        raise Http404(NO_PARTY_MESSAGE)

    form = TravelForm(request.POST)
    if form.is_valid():
        settlement_size = form.cleaned_data["settlement_size"]
        settlement_name = form.cleaned_data.get("settlement_name", "").strip()
        result = resolve_travel_hazards(party, settlement_size, settlement_name or None)
        hazard_count = len(result.get("resolved_hazards", []))
        messages.info(
            request,
            f"Travelled to {settlement_size}. Encountered {hazard_count} hazard(s).",
        )
    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_hero_action(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()
    if not party:
        raise Http404(NO_PARTY_MESSAGE)

    form = HeroActionForm(request.POST, party=party)
    if form.is_valid():
        hero = form.cleaned_data["hero"]
        action_type = form.cleaned_data["action_type"]
        result = resolve_settlement_action(
            hero, action_type, party.current_settlement_size
        )
        narrative = result.get("action_effects", {}).get("narrative", "")
        if narrative:
            messages.success(request, narrative)
    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_shop_transaction(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()
    if not party:
        raise Http404(NO_PARTY_MESSAGE)

    form = ShopTransactionForm(request.POST)
    if form.is_valid():
        result = process_shop_transaction(
            party=party,
            settlement_size=party.current_settlement_size,
            transaction_type=form.cleaned_data["transaction_type"],
            item_def=form.cleaned_data["item_def"],
            quantity=form.cleaned_data["quantity"],
        )
        if result["status"] == "success":
            messages.success(request, result.get("narrative", "Transaction complete."))
        else:
            messages.warning(
                request,
                f"Transaction failed: {result.get('reason', 'unknown reason')}.",
            )

    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_crafting_action(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    party = Party.objects.filter(campaign=campaign).order_by("id").first()
    if not party:
        raise Http404(NO_PARTY_MESSAGE)

    form = CraftingForm(request.POST)
    if form.is_valid():
        result = resolve_crafting(
            party=party,
            recipe_def=form.cleaned_data["recipe_def"],
        )
        if result["status"] == "success":
            messages.success(request, result.get("narrative", "Item crafted."))
        else:
            messages.warning(
                request, f"Crafting failed: {result.get('reason', 'unknown reason')}."
            )
    return redirect(ROUTE_CAMPAIGN_DETAIL, campaign_id=campaign_id)


@staff_member_required
@require_http_methods(["GET", "POST"])
def gm_console(request: HttpRequest) -> HttpResponse:
    source_filter = request.GET.get("source", DEFAULT_GM_SOURCE_FILTER).strip()
    hazard_roll_filter = request.GET.get("hazard_roll", "").strip()
    settlement_roll_filter = request.GET.get("settlement_roll", "").strip()
    catastrophic_roll_filter = request.GET.get("catastrophic_roll", "").strip()

    forms = _build_gm_console_forms()

    if request.method == "POST":
        forms, redirect_response = _handle_gm_console_post(request.POST)
        if redirect_response is not None:
            return redirect_response

    context = {
        **forms,
        **_get_gm_console_content(
            source_filter,
            hazard_roll_filter,
            settlement_roll_filter,
            catastrophic_roll_filter,
        ),
        "source_filter": source_filter,
        "hazard_roll_filter": hazard_roll_filter,
        "settlement_roll_filter": settlement_roll_filter,
        "catastrophic_roll_filter": catastrophic_roll_filter,
    }
    return render(request, "campaign/gm_console.html", context)


@staff_member_required
@require_http_methods(["POST"])
def seed_warhammer_content(request: HttpRequest) -> HttpResponse:
    from django.core.management import call_command

    call_command("seed_warhammer_content")
    messages.success(
        request,
        "Warhammer-inspired content seeded. Safe to run again; existing canonical rows are preserved.",
    )
    return redirect(ROUTE_GM_CONSOLE)


@staff_member_required
@require_http_methods(["GET"])
def step_log_detail(request: HttpRequest, step_id: int) -> HttpResponse:
    step = get_object_or_404(StepLog, id=step_id)
    return render(request, "campaign/step_log_detail.html", {"step": step})


@require_http_methods(["GET"])
def hero_detail(request: HttpRequest, campaign_id: int, hero_id: int) -> HttpResponse:
    campaign = _get_campaign_for_request(request, campaign_id)
    hero = get_object_or_404(
        Hero.objects.filter(party__campaign=campaign)
        .select_related("party")
        .prefetch_related("hero_skills__skill_def", "inventory_items__item_def"),
        pk=hero_id,
    )
    recent_steps = StepLog.objects.filter(hero=hero).order_by("-created_at", "-id")[:20]
    return render(
        request,
        "campaign/hero_detail.html",
        {
            "campaign": campaign,
            "hero": hero,
            "skills": HeroSkill.objects.filter(hero=hero).select_related("skill_def"),
            "inventory": InventoryItem.objects.filter(hero=hero).select_related(
                "item_def"
            ),
            "carry_weight": get_hero_carry_weight(hero),
            "carry_capacity": get_hero_carry_capacity(hero),
            "recent_steps": recent_steps,
        },
    )
