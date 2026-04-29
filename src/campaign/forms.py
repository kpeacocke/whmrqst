from django import forms
from django.db import models

from campaign.models import (
    Campaign,
    CatastrophicEventDef,
    CraftingRecipeDef,
    Expedition,
    ExpeditionDef,
    HazardDef,
    Hero,
    ItemDef,
    Party,
    SettlementEventDef,
    SettlementLocationDef,
)


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "seed"]


class PartyCreateForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ["campaign", "name", "gold", "supplies", "morale"]


class HeroCreateForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ["party", "name", "archetype", "level", "max_health", "current_health"]


class TravelForm(forms.Form):
    settlement_size = forms.ChoiceField(choices=HazardDef.SettlementSize.choices)


class ExpeditionForm(forms.Form):
    expedition_def = forms.ModelChoiceField(queryset=ExpeditionDef.objects.none())
    risk_level = forms.ChoiceField(choices=Expedition.RiskLevel.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expedition_field = self.fields["expedition_def"]
        if isinstance(expedition_field, forms.ModelChoiceField):
            expedition_field.queryset = ExpeditionDef.objects.order_by("name")


class ShopTransactionForm(forms.Form):
    class TransactionType(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    transaction_type = forms.ChoiceField(choices=TransactionType.choices)
    settlement_size = forms.ChoiceField(choices=HazardDef.SettlementSize.choices)
    item_def = forms.ModelChoiceField(queryset=ItemDef.objects.none())
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        item_field = self.fields["item_def"]
        if isinstance(item_field, forms.ModelChoiceField):
            item_field.queryset = ItemDef.objects.order_by("name")


class HeroActionForm(forms.Form):
    hero = forms.ModelChoiceField(queryset=Hero.objects.none())
    action_type = forms.ChoiceField(
        choices=[
            ("rest", "Rest"),
            ("heal", "Heal"),
            ("train", "Train"),
            ("special", "Visit Special Location"),
        ]
    )
    settlement_size = forms.ChoiceField(
        choices=HazardDef.SettlementSize.choices,
        required=False,
        initial="town",
    )

    def __init__(self, *args, **kwargs):
        party = kwargs.pop("party", None)
        super().__init__(*args, **kwargs)
        if party is not None:
            hero_field = self.fields["hero"]
            if isinstance(hero_field, forms.ModelChoiceField):
                hero_field.queryset = Hero.objects.filter(party=party).order_by("name")


class HazardDefForm(forms.ModelForm):
    class Meta:
        model = HazardDef
        fields = ["name", "settlement_size", "severity", "definition"]


class SettlementEventDefForm(forms.ModelForm):
    class Meta:
        model = SettlementEventDef
        fields = ["name", "weight", "definition"]


class CatastrophicEventDefForm(forms.ModelForm):
    class Meta:
        model = CatastrophicEventDef
        fields = ["name", "weight", "definition"]


class SettlementLocationDefForm(forms.ModelForm):
    class Meta:
        model = SettlementLocationDef
        fields = [
            "code",
            "name",
            "always_available",
            "village_available",
            "town_find_target",
            "city_find_target",
            "definition",
        ]


class CraftingForm(forms.Form):
    recipe_def = forms.ModelChoiceField(queryset=CraftingRecipeDef.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        recipe_field = self.fields["recipe_def"]
        if isinstance(recipe_field, forms.ModelChoiceField):
            recipe_field.queryset = CraftingRecipeDef.objects.order_by("name")


class CraftingRecipeDefForm(forms.ModelForm):
    class Meta:
        model = CraftingRecipeDef
        fields = ["code", "name", "definition"]
