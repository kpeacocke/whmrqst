from django.contrib import admin

from .models import (
    Campaign,
    CatastrophicEventDef,
    ContentPack,
    Expedition,
    ExpeditionDef,
    HazardDef,
    Hero,
    HeroSkill,
    InventoryItem,
    ItemDef,
    Party,
    SettlementLocationDef,
    SettlementEventDef,
    ShopDef,
    SkillDef,
    StepLog,
)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "seed", "current_day", "current_week", "is_active")
    search_fields = ("name", "seed")


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "campaign",
        "gold",
        "supplies",
        "morale",
        "hardship_price_multiplier",
        "forced_departure",
    )
    search_fields = ("name",)


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "party",
        "archetype",
        "level",
        "current_health",
        "max_health",
        "days_unavailable",
        "in_disguise",
    )
    list_filter = ("archetype",)
    search_fields = ("name",)


@admin.register(ContentPack)
class ContentPackAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active", "updated_at")
    search_fields = ("name", "version")


@admin.register(HazardDef)
class HazardDefAdmin(admin.ModelAdmin):
    list_display = ("name", "settlement_size", "severity", "updated_at")
    list_filter = ("settlement_size",)
    search_fields = ("name",)


@admin.register(SettlementEventDef)
class SettlementEventDefAdmin(admin.ModelAdmin):
    list_display = ("name", "weight", "updated_at")
    search_fields = ("name",)


@admin.register(CatastrophicEventDef)
class CatastrophicEventDefAdmin(admin.ModelAdmin):
    list_display = ("name", "weight", "updated_at")
    search_fields = ("name",)


@admin.register(ItemDef)
class ItemDefAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "stock_value")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(ShopDef)
class ShopDefAdmin(admin.ModelAdmin):
    list_display = ("name", "settlement_size", "updated_at")
    list_filter = ("settlement_size",)
    search_fields = ("name",)


@admin.register(SettlementLocationDef)
class SettlementLocationDefAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "always_available", "village_available", "town_find_target", "city_find_target")
    search_fields = ("name", "code")


@admin.register(SkillDef)
class SkillDefAdmin(admin.ModelAdmin):
    list_display = ("name", "archetype", "updated_at")
    list_filter = ("archetype",)
    search_fields = ("name",)


@admin.register(ExpeditionDef)
class ExpeditionDefAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "difficulty", "base_reward_min", "base_reward_max")
    search_fields = ("name", "code")


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ("campaign", "party", "expedition_def", "risk_level", "created_at")
    list_filter = ("risk_level",)
    search_fields = ("campaign__name", "party__name", "expedition_def__name")


@admin.register(HeroSkill)
class HeroSkillAdmin(admin.ModelAdmin):
    list_display = ("hero", "skill_def", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("hero__name", "skill_def__name")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("item_def", "party", "hero", "quantity", "updated_at")
    search_fields = ("item_def__name", "party__name", "hero__name")


@admin.register(StepLog)
class StepLogAdmin(admin.ModelAdmin):
    list_display = ("campaign", "party", "hero", "step_type", "action_type", "created_at")
    search_fields = ("campaign__name", "party__name", "hero__name", "step_type", "action_type")
    list_filter = ("step_type", "action_type")
    ordering = ("-created_at",)
