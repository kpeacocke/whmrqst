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
    help = "Import content pack from ContentPack record or JSON file"

    def add_arguments(self, parser):
        parser.add_argument("--name", default="")
        parser.add_argument("--pack-version", default="")
        parser.add_argument("--input", default="")

    def handle(self, *args, **options):
        payload = self._load_payload(options["name"], options["pack_version"], options["input"])

        self._upsert_hazards(payload.get("hazards", []))
        self._upsert_settlement_events(payload.get("settlement_events", []))
        self._upsert_catastrophic_events(payload.get("catastrophic_events", []))
        self._upsert_locations(payload.get("locations", []))
        self._upsert_items(payload.get("items", []))
        self._upsert_skills(payload.get("skills", []))
        self._upsert_expeditions(payload.get("expeditions", []))
        self._upsert_crafting_recipes(payload.get("crafting_recipes", []))

        self.stdout.write(self.style.SUCCESS("Content pack import applied."))

    def _load_payload(self, name, version, input_path):
        if input_path:
            file_path = Path(input_path)
            if not file_path.exists():
                raise CommandError(f"Input file not found: {file_path}")
            return json.loads(file_path.read_text(encoding="utf-8"))

        if not name:
            raise CommandError("Provide --input or --name for stored ContentPack import.")

        queryset = ContentPack.objects.filter(name=name)
        if version:
            queryset = queryset.filter(version=version)
        content_pack = queryset.order_by("-id").first()
        if content_pack is None:
            raise CommandError("No matching ContentPack found.")
        return content_pack.content

    def _upsert_hazards(self, rows):
        for row in rows:
            HazardDef.objects.update_or_create(
                name=row["name"],
                defaults={
                    "settlement_size": row["settlement_size"],
                    "severity": row["severity"],
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_settlement_events(self, rows):
        for row in rows:
            SettlementEventDef.objects.update_or_create(
                name=row["name"],
                defaults={
                    "weight": row["weight"],
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_catastrophic_events(self, rows):
        for row in rows:
            CatastrophicEventDef.objects.update_or_create(
                name=row["name"],
                defaults={
                    "weight": row["weight"],
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_locations(self, rows):
        for row in rows:
            SettlementLocationDef.objects.update_or_create(
                code=row["code"],
                defaults={
                    "name": row["name"],
                    "always_available": row.get("always_available", False),
                    "village_available": row.get("village_available", False),
                    "town_find_target": row.get("town_find_target"),
                    "city_find_target": row.get("city_find_target"),
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_items(self, rows):
        for row in rows:
            ItemDef.objects.update_or_create(
                name=row["name"],
                defaults={
                    "category": row["category"],
                    "base_price": row["base_price"],
                    "stock_value": row["stock_value"],
                    "weight": row.get("weight", 0),
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_skills(self, rows):
        for row in rows:
            SkillDef.objects.update_or_create(
                name=row["name"],
                defaults={
                    "archetype": row["archetype"],
                    "description": row.get("description", ""),
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_expeditions(self, rows):
        for row in rows:
            ExpeditionDef.objects.update_or_create(
                code=row["code"],
                defaults={
                    "name": row["name"],
                    "base_reward_min": row["base_reward_min"],
                    "base_reward_max": row["base_reward_max"],
                    "base_supply_cost": row["base_supply_cost"],
                    "base_injury_risk": row["base_injury_risk"],
                    "difficulty": row["difficulty"],
                    "definition": row.get("definition", {}),
                },
            )

    def _upsert_crafting_recipes(self, rows):
        for row in rows:
            CraftingRecipeDef.objects.update_or_create(
                code=row["code"],
                defaults={
                    "name": row["name"],
                    "definition": row.get("definition", {}),
                },
            )
