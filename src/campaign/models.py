from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimeStampedModel):
    name = models.CharField(max_length=120)
    seed = models.CharField(max_length=120, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_campaigns",
    )
    current_day = models.PositiveIntegerField(default=1)
    current_week = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.seed})"


class Party(TimeStampedModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="parties")
    name = models.CharField(max_length=120)
    gold = models.PositiveIntegerField(default=0)
    supplies = models.PositiveIntegerField(default=0)
    morale = models.IntegerField(default=0)
    hardship_price_multiplier = models.PositiveSmallIntegerField(default=1)
    forced_departure = models.BooleanField(default=False)
    disease_risk_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Hero(TimeStampedModel):
    class Archetype(models.TextChoices):
        WARRIOR = "warrior", "Warrior"
        RANGER = "ranger", "Ranger"
        MAGE = "mage", "Mage"
        PRIEST = "priest", "Priest"

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="heroes")
    name = models.CharField(max_length=120)
    archetype = models.CharField(max_length=30, choices=Archetype.choices)
    level = models.PositiveIntegerField(default=1)
    max_health = models.PositiveIntegerField(default=10)
    current_health = models.PositiveIntegerField(default=10)
    conditions = models.JSONField(default=list, blank=True)
    stats = models.JSONField(default=dict, blank=True)
    days_unavailable = models.PositiveIntegerField(default=0)
    is_waiting_outside = models.BooleanField(default=False)
    in_disguise = models.BooleanField(default=False)
    has_pet_dog = models.BooleanField(default=False)
    investment_active = models.BooleanField(default=False)
    temple_reroll_charges = models.PositiveSmallIntegerField(default=0)
    alive = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ContentPack(TimeStampedModel):
    name = models.CharField(max_length=120)
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)
    content = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} v{self.version}"


class ItemDef(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=50)
    base_price = models.PositiveIntegerField(default=0)
    stock_value = models.PositiveIntegerField(default=1)
    weight = models.PositiveSmallIntegerField(default=0)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class CraftingRecipeDef(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120, unique=True)
    definition = models.JSONField(default=dict, blank=True)
    # definition shape:
    # {
    #   "source": "whq_roleplay_book",
    #   "book_section": "Crafting",
    #   "narrative": "...",
    #   "ingredients": [{"item_name": "WHQ Rope", "quantity": 1}, ...],
    #   "output_item_name": "WHQ Exploration Kit",
    #   "output_quantity": 1
    # }

    def __str__(self):
        return self.name


class SkillDef(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    archetype = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class ExpeditionDef(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120, unique=True)
    base_reward_min = models.PositiveIntegerField(default=25)
    base_reward_max = models.PositiveIntegerField(default=120)
    base_supply_cost = models.PositiveSmallIntegerField(default=1)
    base_injury_risk = models.PositiveSmallIntegerField(default=2)
    difficulty = models.PositiveSmallIntegerField(default=1)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Expedition(TimeStampedModel):
    class RiskLevel(models.TextChoices):
        CAUTIOUS = "cautious", "Cautious"
        STANDARD = "standard", "Standard"
        RECKLESS = "reckless", "Reckless"

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="expeditions")
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="expeditions")
    expedition_def = models.ForeignKey(ExpeditionDef, on_delete=models.PROTECT, related_name="expeditions")
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.STANDARD)
    result = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.party.name}: {self.expedition_def.name} ({self.risk_level})"


class HazardDef(TimeStampedModel):
    class SettlementSize(models.TextChoices):
        VILLAGE = "village", "Village"
        TOWN = "town", "Town"
        CITY = "city", "City"

    name = models.CharField(max_length=120, unique=True)
    settlement_size = models.CharField(max_length=20, choices=SettlementSize.choices)
    severity = models.PositiveSmallIntegerField(default=1)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class SettlementEventDef(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    weight = models.PositiveIntegerField(default=1)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class CatastrophicEventDef(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    weight = models.PositiveIntegerField(default=1)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class ShopDef(TimeStampedModel):
    class SettlementSize(models.TextChoices):
        VILLAGE = "village", "Village"
        TOWN = "town", "Town"
        CITY = "city", "City"

    name = models.CharField(max_length=120, unique=True)
    settlement_size = models.CharField(max_length=20, choices=SettlementSize.choices)
    stock_table = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class SettlementLocationDef(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120, unique=True)
    always_available = models.BooleanField(default=False)
    village_available = models.BooleanField(default=False)
    town_find_target = models.PositiveSmallIntegerField(null=True, blank=True)
    city_find_target = models.PositiveSmallIntegerField(null=True, blank=True)
    definition = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class HeroSkill(TimeStampedModel):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="hero_skills")
    skill_def = models.ForeignKey(SkillDef, on_delete=models.PROTECT, related_name="hero_skills")
    source = models.CharField(max_length=60, default="training")

    class Meta:
        unique_together = ("hero", "skill_def")

    def __str__(self):
        return f"{self.hero.name} – {self.skill_def.name}"


class InventoryItem(TimeStampedModel):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="inventory_items")
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="inventory_items", null=True, blank=True)
    item_def = models.ForeignKey(ItemDef, on_delete=models.PROTECT, related_name="inventory_items")
    quantity = models.PositiveIntegerField(default=1)
    item_state = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.item_def.name} x{self.quantity}"


class StepLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="step_logs")
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, related_name="step_logs", null=True, blank=True)
    hero = models.ForeignKey(Hero, on_delete=models.SET_NULL, related_name="step_logs", null=True, blank=True)
    step_type = models.CharField(max_length=50)
    action_type = models.CharField(max_length=50)
    rng_seed = models.CharField(max_length=200)
    dice_rolled = models.JSONField(default=list, blank=True)
    effects_applied = models.JSONField(default=dict, blank=True)
    narrative = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["campaign", "created_at"], name="step_camp_created_idx"),
            models.Index(
                fields=["campaign", "step_type", "action_type"],
                name="step_camp_type_action_idx",
            ),
        ]

    def __str__(self):
        return f"{self.step_type}:{self.action_type}"
