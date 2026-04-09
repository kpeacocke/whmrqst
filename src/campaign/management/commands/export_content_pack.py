import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from campaign.models import (
    CatastrophicEventDef,
    ContentPack,
    CraftingRecipeDef,
    ExpeditionDef,
    HazardDef,
    ItemDef,
    SettlementEventDef,
    SettlementLocationDef,
    SkillDef,
)


class Command(BaseCommand):
    help = "Export seeded content into ContentPack and optional JSON file"

    def add_arguments(self, parser):
        parser.add_argument("--source", default="whq_roleplay_book")
        parser.add_argument("--name", default="Warhammer Base Pack")
        parser.add_argument("--pack-version", default="1.0")
        parser.add_argument("--output", default="")

    def handle(self, *args, **options):
        source = options["source"]
        pack_name = options["name"]
        version = options["pack_version"]
        output = options["output"]

        payload = {
            "source": source,
            "hazards": list(HazardDef.objects.filter(definition__source=source).values("name", "settlement_size", "severity", "definition")),
            "settlement_events": list(SettlementEventDef.objects.filter(definition__source=source).values("name", "weight", "definition")),
            "catastrophic_events": list(CatastrophicEventDef.objects.filter(definition__source=source).values("name", "weight", "definition")),
            "locations": list(
                SettlementLocationDef.objects.filter(definition__source=source).values(
                    "code",
                    "name",
                    "always_available",
                    "village_available",
                    "town_find_target",
                    "city_find_target",
                    "definition",
                )
            ),
            "items": list(ItemDef.objects.filter(definition__source=source).values("name", "category", "base_price", "stock_value", "weight", "definition")),
            "skills": list(SkillDef.objects.filter(definition__source=source).values("name", "archetype", "description", "definition")),
            "expeditions": list(
                ExpeditionDef.objects.filter(definition__source=source).values(
                    "code",
                    "name",
                    "base_reward_min",
                    "base_reward_max",
                    "base_supply_cost",
                    "base_injury_risk",
                    "difficulty",
                    "definition",
                )
            ),
            "crafting_recipes": list(CraftingRecipeDef.objects.filter(definition__source=source).values("code", "name", "definition")),
        }

        if not any(payload[key] for key in payload if key != "source"):
            raise CommandError(f"No content found for source '{source}'.")

        content_pack, _ = ContentPack.objects.update_or_create(
            name=pack_name,
            version=version,
            defaults={"is_active": True, "content": payload},
        )
        self.stdout.write(self.style.SUCCESS(f"Stored content pack {content_pack.name} v{content_pack.version}."))

        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Wrote content pack JSON: {output_path}"))
