from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from campaign.forms import (
    CampaignCreateForm,
    CatastrophicEventDefForm,
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
    Expedition,
    HazardDef,
    SettlementEventDef,
    SettlementLocationDef,
    StepLog,
)
from campaign.services.expedition import resolve_expedition
from campaign.services.economy import process_shop_transaction
from campaign.services.settlement import resolve_settlement_action
from campaign.services.travel import resolve_travel_hazards


@require_http_methods(["GET", "POST"])
def dashboard(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CampaignCreateForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            return redirect("campaign:campaign_detail", campaign_id=campaign.id)
    else:
        form = CampaignCreateForm()

    campaigns = Campaign.objects.order_by("-updated_at")[:10]
    return render(request, "campaign/dashboard.html", {"form": form, "campaigns": campaigns})


@require_http_methods(["GET", "POST"])
def campaign_detail(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    party = campaign.parties.order_by("id").first()

    party_form = PartyCreateForm(initial={"campaign": campaign.id})
    hero_form = HeroCreateForm()

    if request.method == "POST":
        create_type = request.POST.get("create_type")
        if create_type == "party":
            party_form = PartyCreateForm(request.POST)
            if party_form.is_valid():
                party_form.save()
                return redirect("campaign:campaign_detail", campaign_id=campaign.id)
        if create_type == "hero":
            hero_form = HeroCreateForm(request.POST)
            if hero_form.is_valid():
                created_hero = hero_form.save()
                return redirect("campaign:campaign_detail", campaign_id=created_hero.party.campaign_id)

    recent_steps = campaign.step_logs.order_by("-created_at")[:20]
    latest_expedition = campaign.expeditions.order_by("-created_at").first()
    expedition_form = ExpeditionForm()
    travel_form = TravelForm()
    hero_action_form = HeroActionForm(party=party)
    shop_form = ShopTransactionForm()

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
            "recent_steps": recent_steps,
        },
    )


@require_http_methods(["POST"])
def resolve_expedition_run(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    party = campaign.parties.order_by("id").first()
    if not party:
        raise Http404("Campaign has no party yet")

    form = ExpeditionForm(request.POST)
    if form.is_valid():
        result = resolve_expedition(
            party=party,
            expedition_def=form.cleaned_data["expedition_def"],
            risk_level=form.cleaned_data["risk_level"],
        )
        message_level = messages.SUCCESS if result.get("success") else messages.WARNING
        messages.add_message(request, message_level, result.get("narrative", "Expedition resolved."))

    return redirect("campaign:campaign_detail", campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_travel(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    party = campaign.parties.order_by("id").first()
    if not party:
        raise Http404("Campaign has no party yet")

    form = TravelForm(request.POST)
    if form.is_valid():
        settlement_size = form.cleaned_data["settlement_size"]
        result = resolve_travel_hazards(party, settlement_size)
        hazard_count = len(result.get("resolved_hazards", []))
        messages.info(request, f"Travelled to {settlement_size}. Encountered {hazard_count} hazard(s).")
    return redirect("campaign:campaign_detail", campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_hero_action(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    party = campaign.parties.order_by("id").first()
    if not party:
        raise Http404("Campaign has no party yet")

    form = HeroActionForm(request.POST, party=party)
    if form.is_valid():
        hero = form.cleaned_data["hero"]
        action_type = form.cleaned_data["action_type"]
        settlement_size = form.cleaned_data.get("settlement_size") or "town"
        result = resolve_settlement_action(hero, action_type, settlement_size)
        narrative = result.get("action_effects", {}).get("narrative", "")
        if narrative:
            messages.success(request, narrative)
    return redirect("campaign:campaign_detail", campaign_id=campaign_id)


@require_http_methods(["POST"])
def resolve_shop_transaction(request: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    party = campaign.parties.order_by("id").first()
    if not party:
        raise Http404("Campaign has no party yet")

    form = ShopTransactionForm(request.POST)
    if form.is_valid():
        result = process_shop_transaction(
            party=party,
            settlement_size=form.cleaned_data["settlement_size"],
            transaction_type=form.cleaned_data["transaction_type"],
            item_def=form.cleaned_data["item_def"],
            quantity=form.cleaned_data["quantity"],
        )
        if result["status"] == "success":
            messages.success(request, result.get("narrative", "Transaction complete."))
        else:
            messages.warning(request, f"Transaction failed: {result.get('reason', 'unknown reason')}.")

    return redirect("campaign:campaign_detail", campaign_id=campaign_id)


@staff_member_required
@require_http_methods(["GET", "POST"])
def gm_console(request: HttpRequest) -> HttpResponse:
    source_filter = request.GET.get("source", "whq_roleplay_book").strip()
    hazard_roll_filter = request.GET.get("hazard_roll", "").strip()
    settlement_roll_filter = request.GET.get("settlement_roll", "").strip()
    catastrophic_roll_filter = request.GET.get("catastrophic_roll", "").strip()

    hazard_form = HazardDefForm(prefix="hazard")
    settlement_event_form = SettlementEventDefForm(prefix="settlement")
    catastrophic_form = CatastrophicEventDefForm(prefix="catastrophic")
    location_form = SettlementLocationDefForm(prefix="location")

    if request.method == "POST":
        form_kind = request.POST.get("form_kind")
        if form_kind == "hazard":
            hazard_form = HazardDefForm(request.POST, prefix="hazard")
            if hazard_form.is_valid():
                hazard_form.save()
                return redirect("campaign:gm_console")
        elif form_kind == "settlement":
            settlement_event_form = SettlementEventDefForm(request.POST, prefix="settlement")
            if settlement_event_form.is_valid():
                settlement_event_form.save()
                return redirect("campaign:gm_console")
        elif form_kind == "catastrophic":
            catastrophic_form = CatastrophicEventDefForm(request.POST, prefix="catastrophic")
            if catastrophic_form.is_valid():
                catastrophic_form.save()
                return redirect("campaign:gm_console")
        elif form_kind == "location":
            location_form = SettlementLocationDefForm(request.POST, prefix="location")
            if location_form.is_valid():
                location_form.save()
                return redirect("campaign:gm_console")

    hazard_queryset = HazardDef.objects.all()
    settlement_queryset = SettlementEventDef.objects.all()
    catastrophic_queryset = CatastrophicEventDef.objects.all()

    if source_filter:
        hazard_queryset = hazard_queryset.filter(definition__source=source_filter)
        settlement_queryset = settlement_queryset.filter(definition__source=source_filter)
        catastrophic_queryset = catastrophic_queryset.filter(definition__source=source_filter)

    if hazard_roll_filter:
        hazard_queryset = hazard_queryset.filter(definition__table_roll__icontains=hazard_roll_filter)
    if settlement_roll_filter:
        settlement_queryset = settlement_queryset.filter(definition__table_roll__icontains=settlement_roll_filter)
    if catastrophic_roll_filter:
        catastrophic_queryset = catastrophic_queryset.filter(definition__table_roll__icontains=catastrophic_roll_filter)

    hazards = sorted(
        hazard_queryset,
        key=lambda item: (item.definition.get("table_roll", ""), item.settlement_size, item.name),
    )
    settlement_events = sorted(
        settlement_queryset,
        key=lambda item: (item.definition.get("table_roll", ""), item.name),
    )
    catastrophic_events = sorted(
        catastrophic_queryset,
        key=lambda item: (item.definition.get("table_roll", ""), item.name),
    )

    context = {
        "hazard_form": hazard_form,
        "settlement_event_form": settlement_event_form,
        "catastrophic_form": catastrophic_form,
        "location_form": location_form,
        "hazards": hazards,
        "settlement_events": settlement_events,
        "catastrophic_events": catastrophic_events,
        "settlement_locations": SettlementLocationDef.objects.order_by("code", "name"),
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
    return redirect("campaign:gm_console")


@login_required
def step_log_detail(request: HttpRequest, step_id: int) -> HttpResponse:
    step = get_object_or_404(StepLog, id=step_id)
    return render(request, "campaign/step_log_detail.html", {"step": step})
