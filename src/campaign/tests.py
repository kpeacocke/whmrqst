from unittest.mock import patch

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command

from .models import (
    Campaign,
    CatastrophicEventDef,
    ContentPack,
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
    ShopDef,
    SkillDef,
    StepLog,
)
from .services.crafting import get_hero_carry_capacity, get_hero_carry_weight, resolve_crafting
from .services.economy import process_shop_transaction
from .services.expedition import resolve_expedition
from .services.settlement import resolve_settlement_action
from .services.travel import resolve_travel_hazards


class CampaignFoundationTests(TestCase):
    def test_health_endpoint_returns_ok(self):
        response = Client().get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})

    def test_campaign_party_and_step_log_relationships(self):
        campaign = Campaign.objects.create(name="Southern March", seed="seed-001")
        party = Party.objects.create(campaign=campaign, name="Iron Company", gold=25, supplies=8)
        hero = Hero.objects.create(
            party=party,
            name="Mira",
            archetype=Hero.Archetype.RANGER,
            stats={"wit": 2, "grit": 3},
        )
        step_log = StepLog.objects.create(
            campaign=campaign,
            party=party,
            hero=hero,
            step_type="campaign",
            action_type="found_party",
            rng_seed="seed-001:campaign:1",
            dice_rolled=[{"die": "d6", "result": 4}],
            effects_applied={"gold": 25},
            narrative="Party founded in the southern marches.",
        )

        self.assertEqual(campaign.parties.get(), party)
        self.assertEqual(party.heroes.get(), hero)
        self.assertEqual(campaign.step_logs.get(), step_log)
        self.assertEqual(str(step_log), "campaign:found_party")


class PhaseThreeServiceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(name="Northern Roads", seed="phase3-seed")
        self.party = Party.objects.create(campaign=self.campaign, name="Roadwardens", gold=40, supplies=10, morale=0)
        self.hero = Hero.objects.create(
            party=self.party,
            name="Helga",
            archetype=Hero.Archetype.WARRIOR,
            level=1,
            max_health=10,
            current_health=10,
        )
        call_command("seed_warhammer_content")

    def test_travel_resolution_creates_step_logs(self):
        result = resolve_travel_hazards(self.party, "village")

        self.assertEqual(result["settlement_size"], "village")
        self.assertGreaterEqual(len(result["resolved_hazards"]), 2)
        self.assertTrue(
            StepLog.objects.filter(campaign=self.campaign, step_type="travel", action_type="hazard").exists()
        )
        first_log = StepLog.objects.filter(campaign=self.campaign, step_type="travel", action_type="hazard").first()
        self.assertTrue(any(die.get("die") == "d66" for die in first_log.dice_rolled))

    def test_settlement_action_logs_action_and_event(self):
        outcome = resolve_settlement_action(self.hero, "rest")

        self.assertIn("action_log_id", outcome)
        self.assertIn("settlement_event", outcome)
        self.assertTrue(
            StepLog.objects.filter(campaign=self.campaign, step_type="settlement", action_type="rest").exists()
        )

    def test_training_action_builds_progress_and_levels_up(self):
        self.party.gold = 200
        self.party.save(update_fields=["gold", "updated_at"])

        first = resolve_settlement_action(self.hero, "train")
        second = resolve_settlement_action(self.hero, "train")

        self.hero.refresh_from_db()
        self.party.refresh_from_db()

        self.assertEqual(first["action_effects"]["training_progress_delta"], 1)
        self.assertEqual(second["action_effects"]["hero_level_delta"], 1)
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.stats.get("training_progress"), 0)


class EconomyServiceTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Market Roads", seed="phase4-seed")
        self.party = Party.objects.create(campaign=self.campaign, name="Mercers", gold=800, supplies=8, morale=1)
        call_command("seed_warhammer_content")
        self.item = ItemDef.objects.get(name="WHQ Rope")

    def test_buy_transaction_applies_hardship_multiplier_and_logs(self):
        self.party.hardship_price_multiplier = 4
        self.party.save(update_fields=["hardship_price_multiplier", "updated_at"])

        result = process_shop_transaction(
            party=self.party,
            settlement_size="city",
            transaction_type="buy",
            item_def=self.item,
            quantity=1,
        )

        self.party.refresh_from_db()
        inventory = InventoryItem.objects.get(party=self.party, hero=None, item_def=self.item)
        step = StepLog.objects.filter(campaign=self.campaign, step_type="economy", action_type="buy").latest("id")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["unit_price"], self.item.base_price * 4)
        self.assertEqual(inventory.quantity, 1)
        self.assertTrue(any(die.get("context") == "stock-roll" for die in step.dice_rolled))

    def test_buy_rejected_when_insufficient_gold(self):
        self.party.gold = 1
        self.party.save(update_fields=["gold", "updated_at"])

        result = process_shop_transaction(
            party=self.party,
            settlement_size="city",
            transaction_type="buy",
            item_def=ItemDef.objects.get(name="WHQ Chainmail"),
            quantity=1,
        )

        self.party.refresh_from_db()
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "insufficient_gold")
        self.assertFalse(InventoryItem.objects.filter(party=self.party, item_def__name="WHQ Chainmail").exists())

    def test_sell_transaction_increases_gold_and_reduces_inventory(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item, quantity=3)
        starting_gold = self.party.gold

        result = process_shop_transaction(
            party=self.party,
            settlement_size="town",
            transaction_type="sell",
            item_def=self.item,
            quantity=2,
        )

        self.party.refresh_from_db()
        inventory = InventoryItem.objects.get(party=self.party, hero=None, item_def=self.item)
        self.assertEqual(result["status"], "success")
        self.assertEqual(inventory.quantity, 1)
        self.assertEqual(self.party.gold, starting_gold + max(1, self.item.base_price // 2) * 2)


class GmAccessTests(TestCase):
    def test_seed_command_loads_canonical_whq_counts(self):
        call_command("seed_warhammer_content")

        self.assertEqual(HazardDef.objects.count(), 36)
        self.assertEqual(SettlementEventDef.objects.count(), 36)
        self.assertEqual(CatastrophicEventDef.objects.count(), 8)
        self.assertEqual(SettlementLocationDef.objects.count(), 7)
        self.assertEqual(ItemDef.objects.filter(definition__source="whq_roleplay_book").count(), 10)
        self.assertEqual(ExpeditionDef.objects.filter(definition__source="whq_roleplay_book").count(), 4)
        self.assertEqual(CraftingRecipeDef.objects.filter(definition__source="whq_roleplay_book").count(), 2)

    def test_gm_console_requires_staff_login(self):
        response = self.client.get("/gm/")
        self.assertIn(response.status_code, [302, 301])

    def test_staff_user_can_access_gm_console(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="gm", password="password123", is_staff=True)
        self.client.force_login(user)

        response = self.client.get("/gm/")
        self.assertEqual(response.status_code, 200)

    def test_staff_user_can_filter_gm_console_by_table_roll(self):
        call_command("seed_warhammer_content")
        user_model = get_user_model()
        user = user_model.objects.create_user(username="gm-filter", password="password123", is_staff=True)
        self.client.force_login(user)

        response = self.client.get("/gm/", {"source": "whq_roleplay_book", "settlement_roll": "35"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WHQ 35 Duel")
        self.assertNotContains(response, "WHQ 11 Thrown Out")


class SkillSystemTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Skill March", seed="skill-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Wanderers", gold=500, supplies=10, morale=2
        )
        self.warrior = Hero.objects.create(
            party=self.party,
            name="Grolm",
            archetype=Hero.Archetype.WARRIOR,
            level=1,
            max_health=10,
            current_health=10,
        )
        self.mage = Hero.objects.create(
            party=self.party,
            name="Elara",
            archetype=Hero.Archetype.MAGE,
            level=1,
            max_health=8,
            current_health=8,
        )
        call_command("seed_warhammer_content")

    def test_seed_command_creates_eight_skill_defs(self):
        self.assertEqual(SkillDef.objects.filter(definition__source="whq_roleplay_book").count(), 8)

    def test_seed_command_covers_all_four_archetypes(self):
        archetypes_seeded = set(
            SkillDef.objects.filter(definition__source="whq_roleplay_book")
            .values_list("archetype", flat=True)
        )
        self.assertEqual(archetypes_seeded, {"warrior", "ranger", "mage", "priest"})

    def test_training_level_up_grants_archetype_skill(self):
        self.party.gold = 500
        self.party.save(update_fields=["gold", "updated_at"])

        # two training sessions should level up a level-1 hero (threshold = 2)
        resolve_settlement_action(self.warrior, "train", "town")
        resolve_settlement_action(self.warrior, "train", "town")

        self.warrior.refresh_from_db()
        self.assertEqual(self.warrior.level, 2)
        self.assertEqual(self.warrior.hero_skills.count(), 1)
        learned = self.warrior.hero_skills.first().skill_def
        self.assertEqual(learned.archetype, "warrior")

    def test_special_action_alehouse_increases_morale(self):
        starting_morale = self.party.morale
        result = resolve_settlement_action(self.warrior, "special", "village")

        self.party.refresh_from_db()
        action_effects = result["action_effects"]
        # Village only has alehouse; morale should increase
        self.assertGreaterEqual(self.party.morale, starting_morale)
        self.assertIn("location_visited", action_effects)
        self.assertEqual(action_effects["location_visited"], "alehouse")

    def test_special_action_logs_step(self):
        resolve_settlement_action(self.warrior, "special", "village")
        self.assertTrue(
            StepLog.objects.filter(
                campaign=self.campaign,
                step_type="settlement",
                action_type="special",
            ).exists()
        )

    def test_mage_cannot_access_dwarf_guildmasters(self):
        from .services.location import apply_location_effects, resolve_location_access
        from .services.rng import DeterministicRng

        location = SettlementLocationDef.objects.get(code="dwarf_guildmasters")
        rng = DeterministicRng("test-seed")
        effects, _ = apply_location_effects(self.mage, self.party, location, rng)
        self.assertEqual(effects["rejected"], "wrong_archetype")

    def test_hero_skill_unique_per_hero(self):
        skill = SkillDef.objects.filter(archetype="warrior").first()
        HeroSkill.objects.create(hero=self.warrior, skill_def=skill, source="training")
        with self.assertRaises(Exception):
            HeroSkill.objects.create(hero=self.warrior, skill_def=skill, source="training")


class ExpeditionServiceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(name="Expedition March", seed="expedition-seed")
        self.party = Party.objects.create(campaign=self.campaign, name="Blazeward", gold=20, supplies=10, morale=0)
        self.hero_1 = Hero.objects.create(
            party=self.party,
            name="Rurik",
            archetype=Hero.Archetype.WARRIOR,
            level=2,
            max_health=11,
            current_health=11,
        )
        self.hero_2 = Hero.objects.create(
            party=self.party,
            name="Sera",
            archetype=Hero.Archetype.RANGER,
            level=2,
            max_health=10,
            current_health=10,
        )
        call_command("seed_warhammer_content")
        self.expedition_def = ExpeditionDef.objects.get(code="road_escort")
        self.guaranteed_success_expedition = ExpeditionDef.objects.create(
            code="test_safe_run",
            name="Test Safe Run",
            base_reward_min=50,
            base_reward_max=50,
            base_supply_cost=1,
            base_injury_risk=1,
            difficulty=1,
            definition={
                "source": "test_suite",
                "book_section": "Expeditions",
                "narrative": "A controlled route for deterministic expedition testing.",
                "loot_table": [{"item_name": "WHQ Rope", "weight": 1}],
            },
        )
        self.guaranteed_injury_expedition = ExpeditionDef.objects.create(
            code="test_deadly_run",
            name="Test Deadly Run",
            base_reward_min=10,
            base_reward_max=10,
            base_supply_cost=1,
            base_injury_risk=6,
            difficulty=1,
            definition={
                "source": "test_suite",
                "book_section": "Expeditions",
                "narrative": "A controlled route for deterministic injury testing.",
                "loot_table": [{"item_name": "WHQ Rope", "weight": 1}],
            },
        )

    def test_expedition_resolution_creates_log_and_record(self):
        result = resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

        self.party.refresh_from_db()
        self.assertIn("expedition_id", result)
        self.assertTrue(
            StepLog.objects.filter(campaign=self.campaign, step_type="expedition", action_type="run").exists()
        )
        self.assertTrue(Expedition.objects.filter(id=result["expedition_id"], party=self.party).exists())

    def test_expedition_is_deterministic_for_same_seed_and_state(self):
        first = resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

        # Reset expedition side effects so the next run has the exact same state and sequence.
        Expedition.objects.filter(campaign=self.campaign).delete()
        StepLog.objects.filter(campaign=self.campaign, step_type="expedition", action_type="run").delete()
        self.party.gold = 20
        self.party.supplies = 10
        self.party.morale = 0
        self.party.save(update_fields=["gold", "supplies", "morale", "updated_at"])
        self.hero_1.current_health = 11
        self.hero_1.save(update_fields=["current_health", "updated_at"])
        self.hero_1.alive = True
        self.hero_1.conditions = []
        self.hero_1.stats = {}
        self.hero_1.save(update_fields=["current_health", "alive", "conditions", "stats", "updated_at"])
        self.hero_2.current_health = 10
        self.hero_2.save(update_fields=["current_health", "updated_at"])
        self.hero_2.alive = True
        self.hero_2.conditions = []
        self.hero_2.stats = {}
        self.hero_2.save(update_fields=["current_health", "alive", "conditions", "stats", "updated_at"])

        second = resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

        self.assertEqual(first["success"], second["success"])
        self.assertEqual(first["party_gold_delta"], second["party_gold_delta"])
        self.assertEqual(first["party_supplies_delta"], second["party_supplies_delta"])
        self.assertEqual(first["injuries"], second["injuries"])
        self.assertEqual(first["loot"], second["loot"])

    def test_expedition_view_endpoint_runs_and_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/expedition/",
            {"expedition_def": self.expedition_def.id, "risk_level": Expedition.RiskLevel.STANDARD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expedition.objects.filter(campaign=self.campaign).exists())

    def test_expedition_dead_hero_is_marked_not_alive(self):
        self.hero_1.current_health = 1
        self.hero_1.save(update_fields=["current_health", "updated_at"])

        result = resolve_expedition(self.party, self.guaranteed_injury_expedition, Expedition.RiskLevel.RECKLESS)

        self.hero_1.refresh_from_db()

        self.assertFalse(self.hero_1.alive)
        self.assertIn("dead", self.hero_1.conditions)
        self.assertTrue(any(entry["hero"] == self.hero_1.name for entry in result["deaths"]))

    def test_expedition_injured_hero_gains_condition(self):
        self.hero_1.current_health = 3
        self.hero_1.save(update_fields=["current_health", "updated_at"])

        result = resolve_expedition(self.party, self.guaranteed_injury_expedition, Expedition.RiskLevel.RECKLESS)

        self.hero_1.refresh_from_db()

        self.assertTrue(self.hero_1.alive)
        self.assertIn("injured", self.hero_1.conditions)
        self.assertTrue(any(entry["hero"] == self.hero_1.name for entry in result["conditions_gained"]))

    def test_expedition_success_drops_loot_item(self):
        self.hero_1.level = 10
        self.hero_2.level = 10
        self.hero_1.save(update_fields=["level", "updated_at"])
        self.hero_2.save(update_fields=["level", "updated_at"])

        result = resolve_expedition(self.party, self.guaranteed_success_expedition, Expedition.RiskLevel.STANDARD)

        inventory_item = InventoryItem.objects.get(party=self.party, hero=None, item_def__name="WHQ Rope")

        self.assertTrue(result["success"])
        self.assertEqual(result["loot"], [{"item_name": "WHQ Rope", "quantity": 1}])
        self.assertEqual(inventory_item.quantity, 1)

    def test_expedition_heroes_gain_expedition_progress(self):
        self.hero_1.level = 10
        self.hero_2.level = 10
        self.hero_1.save(update_fields=["level", "updated_at"])
        self.hero_2.save(update_fields=["level", "updated_at"])

        resolve_expedition(self.party, self.guaranteed_success_expedition, Expedition.RiskLevel.STANDARD)

        self.hero_1.refresh_from_db()
        self.hero_2.refresh_from_db()

        self.assertEqual(self.hero_1.stats.get("expedition_progress"), 1)
        self.assertEqual(self.hero_2.stats.get("expedition_progress"), 1)


# ---------------------------------------------------------------------------
# Model __str__ coverage
# ---------------------------------------------------------------------------

class ModelStrTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Str Campaign", seed="str-seed-001")
        self.party = Party.objects.create(campaign=self.campaign, name="Str Party", gold=10, supplies=5, morale=0)
        self.hero = Hero.objects.create(
            party=self.party,
            name="Str Hero",
            archetype=Hero.Archetype.WARRIOR,
            level=1,
            max_health=10,
            current_health=10,
        )

    def test_campaign_str(self):
        self.assertEqual(str(self.campaign), "Str Campaign (str-seed-001)")

    def test_party_str(self):
        self.assertEqual(str(self.party), "Str Party")

    def test_hero_str(self):
        self.assertEqual(str(self.hero), "Str Hero")

    def test_content_pack_str(self):
        cp = ContentPack.objects.create(name="Str Pack", version="2.0")
        self.assertEqual(str(cp), "Str Pack v2.0")

    def test_item_def_str(self):
        item = ItemDef.objects.create(name="Str Sword", category="weapon", base_price=10, stock_value=2)
        self.assertEqual(str(item), "Str Sword")

    def test_skill_def_str(self):
        skill = SkillDef.objects.create(name="Str Skill", archetype="warrior")
        self.assertEqual(str(skill), "Str Skill")

    def test_expedition_def_str(self):
        exp_def = ExpeditionDef.objects.create(code="str-exp-def", name="Str Expedition Def")
        self.assertEqual(str(exp_def), "Str Expedition Def")

    def test_expedition_str(self):
        exp_def = ExpeditionDef.objects.create(code="str-exp", name="Str Expedition")
        exp = Expedition.objects.create(
            campaign=self.campaign,
            party=self.party,
            expedition_def=exp_def,
            risk_level=Expedition.RiskLevel.STANDARD,
        )
        self.assertIn("Str Party", str(exp))
        self.assertIn("Str Expedition", str(exp))

    def test_hazard_def_str(self):
        hazard = HazardDef.objects.create(name="Str Hazard", settlement_size="village", severity=1, definition={})
        self.assertEqual(str(hazard), "Str Hazard")

    def test_settlement_event_def_str(self):
        event = SettlementEventDef.objects.create(name="Str Settlement Event", weight=1, definition={})
        self.assertEqual(str(event), "Str Settlement Event")

    def test_catastrophic_event_def_str(self):
        event = CatastrophicEventDef.objects.create(name="Str Catastrophe", weight=1, definition={})
        self.assertEqual(str(event), "Str Catastrophe")

    def test_shop_def_str(self):
        shop = ShopDef.objects.create(name="Str Shop", settlement_size="town", stock_table={})
        self.assertEqual(str(shop), "Str Shop")

    def test_settlement_location_def_str(self):
        loc = SettlementLocationDef.objects.create(
            code="str-loc", name="Str Location", always_available=False, village_available=False
        )
        self.assertEqual(str(loc), "Str Location")

    def test_hero_skill_str(self):
        skill = SkillDef.objects.create(name="Str Hero Skill", archetype="warrior")
        hs = HeroSkill.objects.create(hero=self.hero, skill_def=skill, source="training")
        self.assertIn("Str Hero", str(hs))
        self.assertIn("Str Hero Skill", str(hs))

    def test_inventory_item_str(self):
        item = ItemDef.objects.create(name="Str Inv Item", category="misc", base_price=5, stock_value=1)
        inv = InventoryItem.objects.create(party=self.party, hero=None, item_def=item, quantity=3)
        self.assertEqual(str(inv), "Str Inv Item x3")


# ---------------------------------------------------------------------------
# RNG edge cases
# ---------------------------------------------------------------------------

class RngEdgeCaseTests(TestCase):
    def test_choice_selects_an_item(self):
        from .services.rng import DeterministicRng

        rng = DeterministicRng("seed")
        result = rng.choice(["a", "b", "c"])
        self.assertIn(result, ["a", "b", "c"])

    def test_weighted_choice_raises_for_zero_total_weight(self):
        from .services.rng import DeterministicRng

        rng = DeterministicRng("seed")
        with self.assertRaises(ValueError):
            rng.weighted_choice([("a", 0)])

    def test_weighted_choice_fallback_uses_last_option(self):
        from .services.rng import DeterministicRng

        rng = DeterministicRng("seed")
        # Patch randint to return a value larger than total weight so the loop
        # finishes without returning, exercising the safety-fallback line.
        with patch.object(rng._random, "randint", return_value=999):
            result = rng.weighted_choice([("only", 1)])
        self.assertEqual(result, "only")


# ---------------------------------------------------------------------------
# Travel edge cases
# ---------------------------------------------------------------------------

class TravelEdgeCaseTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Travel Edge", seed="travel-edge-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Roadwalkers", gold=50, supplies=10, morale=0
        )
        call_command("seed_warhammer_content")

    def test_travel_uses_fallback_hazards_when_no_whq_content(self):
        from .services.travel import resolve_travel_hazards

        HazardDef.objects.filter(definition__source="whq_roleplay_book").delete()
        # Create a non-WHQ hazard with no table_roll so the rollback path is
        # exercised (hazards_by_roll empty -> rng.choice fallback).
        HazardDef.objects.create(
            name="Custom Road Hazard",
            settlement_size="village",
            severity=1,
            definition={"effects": []},
        )
        result = resolve_travel_hazards(self.party, "village")
        self.assertEqual(len(result["resolved_hazards"]), 2)

    def test_travel_raises_when_no_hazards_configured(self):
        from .services.travel import resolve_travel_hazards

        HazardDef.objects.all().delete()
        with self.assertRaises(ValueError):
            resolve_travel_hazards(self.party, "village")


# ---------------------------------------------------------------------------
# Expedition edge cases
# ---------------------------------------------------------------------------

class ExpeditionEdgeCaseTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Expedition Edge", seed="exp-edge-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Edgewalkers", gold=50, supplies=10, morale=0
        )
        call_command("seed_warhammer_content")
        self.expedition_def = ExpeditionDef.objects.get(code="road_escort")

    def test_resolve_expedition_raises_with_no_heroes(self):
        with self.assertRaises(ValueError):
            resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

    def test_resolve_expedition_raises_with_all_dead_heroes(self):
        Hero.objects.create(
            party=self.party,
            name="Deceased",
            archetype=Hero.Archetype.WARRIOR,
            level=1,
            max_health=10,
            current_health=0,
            alive=False,
        )
        with self.assertRaises(ValueError):
            resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

    def test_resolve_expedition_cautious_has_lower_supply_cost(self):
        hero = Hero.objects.create(
            party=self.party, name="Careful", archetype=Hero.Archetype.WARRIOR,
            level=5, max_health=15, current_health=15,
        )
        starting_supplies = self.party.supplies
        result = resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.CAUTIOUS)
        self.party.refresh_from_db()
        self.assertLessEqual(starting_supplies - self.party.supplies, self.expedition_def.base_supply_cost)

    def test_resolve_expedition_empty_loot_table_returns_no_loot(self):
        Hero.objects.create(
            party=self.party, name="NoLoot", archetype=Hero.Archetype.WARRIOR,
            level=20, max_health=50, current_health=50,
        )
        no_loot_def = ExpeditionDef.objects.create(
            code="no-loot-run", name="No Loot Run",
            base_reward_min=10, base_reward_max=10,
            base_supply_cost=1, base_injury_risk=1, difficulty=1,
            definition={"source": "test_suite"},
        )
        result = resolve_expedition(self.party, no_loot_def, Expedition.RiskLevel.STANDARD)
        self.assertEqual(result["loot"], [])

    def test_resolve_expedition_unknown_loot_item_returns_no_loot(self):
        Hero.objects.create(
            party=self.party, name="GhostLoot", archetype=Hero.Archetype.WARRIOR,
            level=20, max_health=50, current_health=50,
        )
        ghost_def = ExpeditionDef.objects.create(
            code="ghost-loot-run", name="Ghost Loot Run",
            base_reward_min=10, base_reward_max=10,
            base_supply_cost=1, base_injury_risk=1, difficulty=1,
            definition={
                "source": "test_suite",
                "loot_table": [{"item_name": "Nonexistent Item XYZ", "weight": 1}],
            },
        )
        result = resolve_expedition(self.party, ghost_def, Expedition.RiskLevel.STANDARD)
        self.assertEqual(result["loot"], [])


# ---------------------------------------------------------------------------
# Economy edge cases
# ---------------------------------------------------------------------------

class EconomyEdgeCaseTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Economy Edge", seed="econ-edge-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Edge Traders", gold=1000, supplies=5, morale=0
        )
        call_command("seed_warhammer_content")
        self.item = ItemDef.objects.get(name="WHQ Rope")

    def test_invalid_transaction_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            process_shop_transaction(
                party=self.party,
                settlement_size="city",
                transaction_type="barter",
                item_def=self.item,
                quantity=1,
            )

    def test_buy_rejected_when_stock_value_exceeds_max_dice_roll(self):
        # stock_value=20 means 3d6 (max 18) can never satisfy it.
        rare_item = ItemDef.objects.create(
            name="Ultra Rare Item", category="test", base_price=10, stock_value=20
        )
        result = process_shop_transaction(
            party=self.party,
            settlement_size="city",
            transaction_type="buy",
            item_def=rare_item,
            quantity=1,
        )
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "insufficient_stock")

    def test_sell_rejected_when_no_inventory(self):
        result = process_shop_transaction(
            party=self.party,
            settlement_size="town",
            transaction_type="sell",
            item_def=self.item,
            quantity=1,
        )
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "insufficient_inventory")

    def test_sell_partial_reduces_inventory_without_deleting_row(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item, quantity=5)
        result = process_shop_transaction(
            party=self.party,
            settlement_size="town",
            transaction_type="sell",
            item_def=self.item,
            quantity=3,
        )
        self.assertEqual(result["status"], "success")
        inv = InventoryItem.objects.get(party=self.party, hero=None, item_def=self.item)
        self.assertEqual(inv.quantity, 2)

    def test_sell_all_items_deletes_inventory_row(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item, quantity=2)
        result = process_shop_transaction(
            party=self.party,
            settlement_size="town",
            transaction_type="sell",
            item_def=self.item,
            quantity=2,
        )
        self.assertEqual(result["status"], "success")
        self.assertFalse(
            InventoryItem.objects.filter(party=self.party, hero=None, item_def=self.item).exists()
        )


# ---------------------------------------------------------------------------
# Location service coverage
# ---------------------------------------------------------------------------

class LocationServiceTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Location Tests", seed="location-test-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Seekers", gold=200, supplies=5, morale=0
        )
        self.warrior = Hero.objects.create(
            party=self.party, name="Bork",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=10, current_health=10,
        )
        self.mage = Hero.objects.create(
            party=self.party, name="Zyla",
            archetype=Hero.Archetype.MAGE, level=1, max_health=8, current_health=8,
        )
        self.ranger = Hero.objects.create(
            party=self.party, name="Thea",
            archetype=Hero.Archetype.RANGER, level=1, max_health=9, current_health=9,
        )
        call_command("seed_warhammer_content")

    def test_resolve_location_access_returns_none_when_no_locations(self):
        from .services.location import resolve_location_access
        from .services.rng import DeterministicRng

        SettlementLocationDef.objects.all().delete()
        rng = DeterministicRng("test")
        location, _dice = resolve_location_access("village", rng)
        self.assertIsNone(location)

    def test_resolve_location_access_town_includes_always_available(self):
        from .services.location import resolve_location_access
        from .services.rng import DeterministicRng

        rng = DeterministicRng("stable-seed")
        location, dice = resolve_location_access("town", rng)
        self.assertIsNotNone(location)

    def test_resolve_location_access_city_rolls_for_optional_locations(self):
        from .services.location import resolve_location_access
        from .services.rng import DeterministicRng

        rng = DeterministicRng("city-seed")
        location, dice = resolve_location_access("city", rng)
        self.assertIsNotNone(location)
        # Dice should have been rolled for non-always-available locations.
        self.assertTrue(any(d.get("context") == "location-find" for d in dice))

    def test_apply_location_temple_with_sufficient_gold(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        temple = SettlementLocationDef.objects.get(code="temple")
        self.party.gold = 100
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, temple, rng)
        self.warrior.refresh_from_db()
        self.assertEqual(self.warrior.temple_reroll_charges, 1)
        self.assertIsNone(effects["rejected"])

    def test_apply_location_temple_without_sufficient_gold(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        temple = SettlementLocationDef.objects.get(code="temple")
        self.party.gold = 10
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, temple, rng)
        self.assertEqual(effects["rejected"], "insufficient_gold")

    def test_apply_location_gambling_house_win(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        gambling = SettlementLocationDef.objects.get(code="gambling_house")
        self.party.gold = 100
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        with patch.object(rng._random, "randint", return_value=5):
            effects, _dice = apply_location_effects(self.warrior, self.party, gambling, rng)
        self.assertGreater(effects["party_gold_delta"], 0)

    def test_apply_location_gambling_house_break_even(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        gambling = SettlementLocationDef.objects.get(code="gambling_house")
        self.party.gold = 100
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        with patch.object(rng._random, "randint", return_value=4):
            effects, _dice = apply_location_effects(self.warrior, self.party, gambling, rng)
        self.assertEqual(effects["party_gold_delta"], 0)

    def test_apply_location_gambling_house_lose(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        gambling = SettlementLocationDef.objects.get(code="gambling_house")
        self.party.gold = 100
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        with patch.object(rng._random, "randint", return_value=2):
            effects, _dice = apply_location_effects(self.warrior, self.party, gambling, rng)
        self.assertLess(effects["party_gold_delta"], 0)

    def test_apply_location_gambling_house_insufficient_gold(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        gambling = SettlementLocationDef.objects.get(code="gambling_house")
        self.party.gold = 0
        self.party.save(update_fields=["gold", "updated_at"])
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, gambling, rng)
        self.assertEqual(effects["rejected"], "insufficient_gold")

    def test_apply_location_alchemist_returns_narrative(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        alchemist = SettlementLocationDef.objects.get(code="alchemist")
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, alchemist, rng)
        self.assertIn("Alchemist", effects["narrative"])

    def test_apply_location_wizards_guild_grants_mage_skill(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        guild = SettlementLocationDef.objects.get(code="wizards_guild")
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.mage, self.party, guild, rng)
        self.assertIsNotNone(effects["skill_learned"])

    def test_apply_location_elf_quarter_grants_ranger_skill(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        elf = SettlementLocationDef.objects.get(code="elf_quarter")
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.ranger, self.party, elf, rng)
        self.assertIsNotNone(effects["skill_learned"])

    def test_apply_location_guild_no_skill_when_all_learned(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        for skill in SkillDef.objects.filter(archetype="warrior"):
            HeroSkill.objects.get_or_create(hero=self.warrior, skill_def=skill, defaults={"source": "test"})
        guild = SettlementLocationDef.objects.get(code="dwarf_guildmasters")
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, guild, rng)
        self.assertIsNone(effects["skill_learned"])

    def test_apply_location_unknown_code_uses_default_narrative(self):
        from .services.location import apply_location_effects
        from .services.rng import DeterministicRng

        unknown = SettlementLocationDef.objects.create(
            code="nowhere", name="Nowhere Special",
            always_available=False, village_available=False,
        )
        rng = DeterministicRng("test")
        effects, _dice = apply_location_effects(self.warrior, self.party, unknown, rng)
        self.assertIn("Nowhere Special", effects["narrative"])


# ---------------------------------------------------------------------------
# Settlement service edge cases
# ---------------------------------------------------------------------------

class SettlementEdgeCaseTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Settlement Edge", seed="settle-edge-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Edge Settlers", gold=0, supplies=5, morale=2
        )
        self.hero = Hero.objects.create(
            party=self.party, name="Penny",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=8, current_health=6,
        )
        call_command("seed_warhammer_content")

    def test_heal_action_restores_health(self):
        result = resolve_settlement_action(self.hero, "heal")
        self.hero.refresh_from_db()
        self.assertGreaterEqual(self.hero.current_health, 6)
        self.assertIn("action_log_id", result)

    def test_train_with_insufficient_gold_shows_narrative(self):
        result = resolve_settlement_action(self.hero, "train")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.level, 1)
        self.assertIn("cannot afford", result["action_effects"]["narrative"])

    def test_special_action_with_no_accessible_location_reduces_morale(self):
        SettlementLocationDef.objects.all().delete()
        starting_morale = self.party.morale
        result = resolve_settlement_action(self.hero, "special", "village")
        self.party.refresh_from_db()
        self.assertEqual(result["action_effects"]["party_morale_delta"], -1)

    def test_catastrophic_event_triggered_after_week_2(self):
        # current_day=20 -> after +1 becomes 21; week=3 (>2) and 21%7==0.
        self.campaign.current_day = 20
        self.campaign.save(update_fields=["current_day", "updated_at"])
        self.party.gold = 50
        self.party.save(update_fields=["gold", "updated_at"])
        result = resolve_settlement_action(self.hero, "rest")
        self.assertIsNotNone(result["catastrophic_event"])

    def test_apply_settlement_rule_flag_none_is_noop(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, None)
        self.hero.refresh_from_db()
        self.assertFalse(self.hero.investment_active)

    def test_apply_settlement_rule_flag_future_income(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "future_income")
        self.hero.refresh_from_db()
        self.assertTrue(self.hero.investment_active)

    def test_apply_settlement_rule_flag_forced_departure(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "forced_departure_or_delay")
        self.party.refresh_from_db()
        self.assertTrue(self.party.forced_departure)

    def test_apply_settlement_rule_flag_may_force_departure(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "may_force_departure")
        self.party.refresh_from_db()
        self.assertTrue(self.party.forced_departure)

    def test_apply_settlement_rule_flag_service_delay(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "service_delay")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.days_unavailable, 7)

    def test_apply_settlement_rule_flag_bed_rest(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "bed_rest")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.days_unavailable, 2)

    def test_apply_settlement_rule_flag_pet_dog(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "pet_dog")
        self.hero.refresh_from_db()
        self.assertTrue(self.hero.has_pet_dog)

    def test_apply_settlement_rule_flag_jail(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "jail")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.days_unavailable, 1)

    def test_apply_settlement_rule_flag_reroll_attack_once(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "reroll_attack_once")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.temple_reroll_charges, 1)

    def test_apply_settlement_rule_flag_possible_disguise(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "possible_disguise_or_exile")
        self.hero.refresh_from_db()
        self.assertTrue(self.hero.in_disguise)

    def test_apply_settlement_rule_flag_recovery_delay(self):
        from .services.settlement import _apply_settlement_rule_flag

        _apply_settlement_rule_flag(self.hero, "recovery_delay")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.days_unavailable, 1)

    def test_apply_catastrophic_state_table_roll_3(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "3")
        self.party.refresh_from_db()
        self.assertTrue(self.party.forced_departure)

    def test_apply_catastrophic_state_table_roll_5(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "5")
        self.party.refresh_from_db()
        self.assertEqual(self.party.hardship_price_multiplier, 4)

    def test_apply_catastrophic_state_table_roll_10(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "10")
        self.party.refresh_from_db()
        self.assertTrue(self.party.disease_risk_active)

    def test_apply_catastrophic_state_table_roll_11(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "11")
        self.party.refresh_from_db()
        self.assertTrue(self.party.forced_departure)

    def test_apply_catastrophic_state_table_roll_12(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "12")
        self.party.refresh_from_db()
        self.assertTrue(self.party.disease_risk_active)

    def test_apply_catastrophic_state_unrecognised_roll_no_change(self):
        from .services.settlement import _apply_catastrophic_state

        _apply_catastrophic_state(self.party, "99")
        self.party.refresh_from_db()
        self.assertFalse(self.party.forced_departure)

    def test_apply_event_effects_party_morale_type(self):
        from .services.settlement import _apply_event_effects
        from .services.rng import DeterministicRng

        rng = DeterministicRng("morale-test")
        effects = _apply_event_effects(
            self.hero,
            [{"type": "party_morale", "min": 1, "max": 1}],
            rng,
            party=self.party,
        )
        self.assertEqual(effects["party_morale_delta"], 1)

    def test_settlement_action_with_no_events_returns_none_event(self):
        SettlementEventDef.objects.all().delete()
        result = resolve_settlement_action(self.hero, "rest")
        self.assertIsNone(result["settlement_event"])

    def test_catastrophic_event_with_no_catastrophic_defs_returns_none(self):
        # Trigger week-3 catastrophic check but with no CatastrophicEventDefs seeded.
        CatastrophicEventDef.objects.all().delete()
        self.campaign.current_day = 20
        self.campaign.save(update_fields=["current_day", "updated_at"])
        result = resolve_settlement_action(self.hero, "rest")
        self.assertIsNone(result["catastrophic_event"])

    def test_level_up_with_all_skills_learned_grants_no_skill(self):
        # Give the hero all warrior skills so _grant_level_up_skill returns None.
        for skill in SkillDef.objects.filter(archetype="warrior"):
            HeroSkill.objects.get_or_create(hero=self.hero, skill_def=skill, defaults={"source": "test"})
        self.party.gold = 500
        self.party.save(update_fields=["gold", "updated_at"])
        resolve_settlement_action(self.hero, "train")
        resolve_settlement_action(self.hero, "train")
        self.hero.refresh_from_db()
        self.assertEqual(self.hero.level, 2)
        # No additional skill should have been granted beyond what already existed.
        self.assertEqual(
            self.hero.hero_skills.count(),
            SkillDef.objects.filter(archetype="warrior").count(),
        )


# ---------------------------------------------------------------------------
# Form instantiation coverage
# ---------------------------------------------------------------------------

class FormTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Form Tests", seed="form-test-seed")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Form Party", gold=50, supplies=5, morale=0
        )

    def test_shop_transaction_form_init_sets_item_queryset(self):
        from .forms import ShopTransactionForm

        form = ShopTransactionForm()
        self.assertIsNotNone(form.fields["item_def"].queryset)

    def test_hero_action_form_init_with_party_filters_heroes(self):
        from .forms import HeroActionForm

        hero = Hero.objects.create(
            party=self.party, name="Form Hero",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=10, current_health=10,
        )
        form = HeroActionForm(party=self.party)
        self.assertIn(hero, form.fields["hero"].queryset)

    def test_hero_action_form_init_without_party_uses_empty_queryset(self):
        from .forms import HeroActionForm

        form = HeroActionForm()
        self.assertEqual(form.fields["hero"].queryset.count(), 0)


# ---------------------------------------------------------------------------
# View coverage
# ---------------------------------------------------------------------------

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="view-staff", password="password123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="view-player", password="password123", is_staff=False
        )
        self.campaign = Campaign.objects.create(name="View Campaign", seed="view-seed-001")
        self.party = Party.objects.create(
            campaign=self.campaign, name="View Party", gold=200, supplies=10, morale=0
        )
        self.hero = Hero.objects.create(
            party=self.party, name="View Hero",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=10, current_health=10,
        )
        call_command("seed_warhammer_content")
        self.expedition_def = ExpeditionDef.objects.get(code="road_escort")
        self.item = ItemDef.objects.get(name="WHQ Rope")

    # --- Dashboard ---

    def test_dashboard_get_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_post_creates_campaign(self):
        response = self.client.post("/", {"name": "New Campaign", "seed": "new-seed-unique"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Campaign.objects.filter(seed="new-seed-unique").exists())

    def test_dashboard_post_invalid_form_rerenders(self):
        response = self.client.post("/", {"name": "", "seed": ""})
        self.assertEqual(response.status_code, 200)

    # --- Campaign detail ---

    def test_campaign_detail_get_renders(self):
        response = self.client.get(f"/campaign/{self.campaign.id}/")
        self.assertEqual(response.status_code, 200)

    def test_campaign_detail_post_create_party(self):
        campaign2 = Campaign.objects.create(name="Empty", seed="empty-view-seed")
        response = self.client.post(
            f"/campaign/{campaign2.id}/",
            {"create_type": "party", "campaign": campaign2.id, "name": "New Party", "gold": "10", "supplies": "5", "morale": "0"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(campaign2.parties.filter(name="New Party").exists())

    def test_campaign_detail_post_create_hero(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/",
            {
                "create_type": "hero",
                "party": self.party.id,
                "name": "New Hero",
                "archetype": "warrior",
                "level": "1",
                "max_health": "10",
                "current_health": "10",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.party.heroes.filter(name="New Hero").exists())

    # --- Expedition view ---

    def test_resolve_expedition_with_no_party_returns_404(self):
        campaign_empty = Campaign.objects.create(name="Empty Expd", seed="empty-expd-seed")
        response = self.client.post(
            f"/campaign/{campaign_empty.id}/expedition/",
            {"expedition_def": self.expedition_def.id, "risk_level": "standard"},
        )
        self.assertEqual(response.status_code, 404)

    def test_resolve_expedition_with_invalid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/expedition/",
            {"expedition_def": "", "risk_level": ""},
        )
        self.assertEqual(response.status_code, 302)

    # --- Travel view ---

    def test_resolve_travel_with_valid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/travel/",
            {"settlement_size": "village"},
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_travel_with_no_party_returns_404(self):
        campaign_empty = Campaign.objects.create(name="Empty Travel", seed="empty-travel-seed")
        response = self.client.post(
            f"/campaign/{campaign_empty.id}/travel/",
            {"settlement_size": "village"},
        )
        self.assertEqual(response.status_code, 404)

    def test_resolve_travel_with_invalid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/travel/",
            {"settlement_size": ""},
        )
        self.assertEqual(response.status_code, 302)

    # --- Hero action view ---

    def test_resolve_hero_action_valid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/action/",
            {"hero": self.hero.id, "action_type": "rest", "settlement_size": "town"},
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_hero_action_with_no_party_returns_404(self):
        campaign_empty = Campaign.objects.create(name="Empty Action", seed="empty-action-seed")
        response = self.client.post(
            f"/campaign/{campaign_empty.id}/action/",
            {"hero": self.hero.id, "action_type": "rest", "settlement_size": "town"},
        )
        self.assertEqual(response.status_code, 404)

    def test_resolve_hero_action_invalid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/action/",
            {"hero": "", "action_type": "rest"},
        )
        self.assertEqual(response.status_code, 302)

    # --- Shop view ---

    def test_resolve_shop_transaction_buy_success_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/shop/",
            {
                "transaction_type": "buy",
                "settlement_size": "city",
                "item_def": self.item.id,
                "quantity": "1",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_shop_transaction_buy_failure_redirects(self):
        self.party.gold = 0
        self.party.save(update_fields=["gold", "updated_at"])
        response = self.client.post(
            f"/campaign/{self.campaign.id}/shop/",
            {
                "transaction_type": "buy",
                "settlement_size": "city",
                "item_def": self.item.id,
                "quantity": "1",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_shop_transaction_with_no_party_returns_404(self):
        campaign_empty = Campaign.objects.create(name="Empty Shop", seed="empty-shop-seed")
        response = self.client.post(
            f"/campaign/{campaign_empty.id}/shop/",
            {
                "transaction_type": "buy",
                "settlement_size": "city",
                "item_def": self.item.id,
                "quantity": "1",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_resolve_shop_transaction_invalid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/shop/",
            {"transaction_type": "", "settlement_size": "", "item_def": "", "quantity": ""},
        )
        self.assertEqual(response.status_code, 302)

    # --- GM console POST forms ---

    def test_gm_console_post_hazard_form_creates_hazard(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            "/gm/",
            {
                "form_kind": "hazard",
                "hazard-name": "New Test Hazard",
                "hazard-settlement_size": "village",
                "hazard-severity": "1",
                "hazard-definition": "{}",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(HazardDef.objects.filter(name="New Test Hazard").exists())

    def test_gm_console_post_settlement_event_form_creates_event(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            "/gm/",
            {
                "form_kind": "settlement",
                "settlement-name": "New Test Event",
                "settlement-weight": "1",
                "settlement-definition": "{}",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SettlementEventDef.objects.filter(name="New Test Event").exists())

    def test_gm_console_post_catastrophic_form_creates_event(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            "/gm/",
            {
                "form_kind": "catastrophic",
                "catastrophic-name": "New Test Catastrophe",
                "catastrophic-weight": "1",
                "catastrophic-definition": "{}",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CatastrophicEventDef.objects.filter(name="New Test Catastrophe").exists())

    def test_gm_console_post_location_form_creates_location(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            "/gm/",
            {
                "form_kind": "location",
                "location-code": "test-new-loc",
                "location-name": "New Test Location",
                "location-always_available": "",
                "location-village_available": "",
                "location-definition": "{}",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SettlementLocationDef.objects.filter(code="test-new-loc").exists())

    def test_gm_console_filter_by_hazard_roll(self):
        self.client.force_login(self.staff_user)
        response = self.client.get("/gm/", {"hazard_roll": "11"})
        self.assertEqual(response.status_code, 200)

    def test_gm_console_filter_by_catastrophic_roll(self):
        self.client.force_login(self.staff_user)
        response = self.client.get("/gm/", {"catastrophic_roll": "3"})
        self.assertEqual(response.status_code, 200)

    # --- Seed view ---

    def test_seed_warhammer_content_view_requires_staff(self):
        response = self.client.post("/gm/seed/")
        self.assertIn(response.status_code, [302, 403])

    def test_seed_warhammer_content_view_runs_and_redirects(self):
        self.client.force_login(self.staff_user)
        response = self.client.post("/gm/seed/")
        self.assertEqual(response.status_code, 302)

    # --- Step log detail ---

    def test_step_log_detail_requires_login(self):
        step = StepLog.objects.create(
            campaign=self.campaign,
            step_type="test",
            action_type="detail",
            rng_seed="seed",
        )
        response = self.client.get(f"/step/{step.id}/")
        self.assertIn(response.status_code, [302, 403])

    def test_step_log_detail_renders_for_logged_in_user(self):
        self.client.force_login(self.regular_user)
        step = StepLog.objects.create(
            campaign=self.campaign,
            step_type="test",
            action_type="detail",
            rng_seed="seed",
        )
        response = self.client.get(f"/step/{step.id}/")
        self.assertEqual(response.status_code, 200)


class EncumbranceTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(name="Enc Campaign", seed="enc-seed-001")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Enc Party", gold=500, supplies=10, morale=0
        )
        self.hero = Hero.objects.create(
            party=self.party, name="Enc Hero",
            archetype=Hero.Archetype.WARRIOR, level=3, max_health=12, current_health=12,
        )
        self.item_def = ItemDef.objects.create(
            name="Heavy Stone", category="utility", base_price=10, stock_value=1, weight=4,
            definition={"source": "test", "narrative": "A heavy stone."},
        )

    def test_item_def_has_weight_field(self):
        self.assertEqual(self.item_def.weight, 4)

    def test_hero_carry_capacity_scales_with_level(self):
        # level=3 → 10 + (3 * 2) = 16
        self.assertEqual(get_hero_carry_capacity(self.hero), 16)
        self.hero.level = 1
        self.assertEqual(get_hero_carry_capacity(self.hero), 12)

    def test_get_hero_carry_weight_with_no_items_returns_zero(self):
        self.assertEqual(get_hero_carry_weight(self.hero), 0)

    def test_get_hero_carry_weight_accumulates_item_weights(self):
        InventoryItem.objects.create(
            party=self.party, hero=self.hero, item_def=self.item_def, quantity=2
        )
        # weight=4, quantity=2 → 8
        self.assertEqual(get_hero_carry_weight(self.hero), 8)

    def test_get_hero_carry_weight_sums_multiple_item_types(self):
        light_item = ItemDef.objects.create(
            name="Candle", category="utility", base_price=1, stock_value=1, weight=1,
            definition={"source": "test", "narrative": "A candle."},
        )
        InventoryItem.objects.create(
            party=self.party, hero=self.hero, item_def=self.item_def, quantity=1
        )
        InventoryItem.objects.create(
            party=self.party, hero=self.hero, item_def=light_item, quantity=3
        )
        # 4*1 + 1*3 = 7
        self.assertEqual(get_hero_carry_weight(self.hero), 7)


class CraftingServiceTests(TestCase):
    def setUp(self):
        call_command("seed_warhammer_content")
        self.campaign = Campaign.objects.create(name="Craft Campaign", seed="craft-seed-001")
        self.party = Party.objects.create(
            campaign=self.campaign, name="Craft Party", gold=500, supplies=10, morale=0
        )
        self.hero = Hero.objects.create(
            party=self.party, name="Craft Hero",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=10, current_health=10,
        )
        self.recipe_kit = CraftingRecipeDef.objects.get(code="whq_exploration_kit")
        self.recipe_draught = CraftingRecipeDef.objects.get(code="whq_enhanced_draught")
        self.item_rope = ItemDef.objects.get(name="WHQ Rope")
        self.item_lantern = ItemDef.objects.get(name="WHQ Lantern")
        self.item_draught = ItemDef.objects.get(name="WHQ Healing Draught")
        self.item_kit = ItemDef.objects.get(name="WHQ Exploration Kit")
        self.item_enhanced = ItemDef.objects.get(name="WHQ Enhanced Draught")

    # --- CraftingRecipeDef __str__ ---

    def test_crafting_recipe_str(self):
        self.assertEqual(str(self.recipe_kit), "WHQ Exploration Kit")

    # --- Happy path crafting ---

    def test_crafting_creates_output_and_consumes_ingredients(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=1)

        result = resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output_item_name"], "WHQ Exploration Kit")
        self.assertEqual(result["output_quantity"], 1)
        self.assertFalse(InventoryItem.objects.filter(party=self.party, item_def=self.item_rope).exists())
        self.assertFalse(InventoryItem.objects.filter(party=self.party, item_def=self.item_lantern).exists())
        self.assertEqual(
            InventoryItem.objects.get(party=self.party, item_def=self.item_kit).quantity, 1
        )

    def test_crafting_step_log_created_on_success(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=1)

        resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        log = StepLog.objects.filter(
            campaign=self.campaign, step_type="crafting", action_type="craft"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.effects_applied["status"], "success")

    def test_crafting_stacks_output_with_existing_inventory(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_kit, quantity=2)

        resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertEqual(
            InventoryItem.objects.get(party=self.party, item_def=self.item_kit).quantity, 3
        )

    def test_crafting_with_hero_arg_logs_hero_on_steplog(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=1)

        resolve_crafting(party=self.party, recipe_def=self.recipe_kit, hero=self.hero)

        log = StepLog.objects.filter(campaign=self.campaign, action_type="craft").first()
        self.assertEqual(log.hero_id, self.hero.id)

    def test_crafting_consumes_excess_ingredient_quantity(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=3)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=5)

        resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertEqual(
            InventoryItem.objects.get(party=self.party, item_def=self.item_rope).quantity, 2
        )
        self.assertEqual(
            InventoryItem.objects.get(party=self.party, item_def=self.item_lantern).quantity, 4
        )

    def test_crafting_double_ingredient_recipe(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_draught, quantity=2)

        result = resolve_crafting(party=self.party, recipe_def=self.recipe_draught)

        self.assertEqual(result["status"], "success")
        self.assertFalse(InventoryItem.objects.filter(party=self.party, item_def=self.item_draught).exists())
        self.assertEqual(
            InventoryItem.objects.get(party=self.party, item_def=self.item_enhanced).quantity, 1
        )

    # --- Rejection paths ---

    def test_crafting_fails_when_ingredient_missing(self):
        # Only rope in inventory, no lantern.
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)

        result = resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "insufficient_ingredients")
        self.assertEqual(result["missing_item"], "WHQ Lantern")
        self.assertEqual(result["available"], 0)

    def test_crafting_fails_when_ingredient_quantity_insufficient(self):
        # Need 2 draughts, only have 1.
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_draught, quantity=1)

        result = resolve_crafting(party=self.party, recipe_def=self.recipe_draught)

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "insufficient_ingredients")
        self.assertEqual(result["available"], 1)
        self.assertEqual(result["required"], 2)

    def test_crafting_rejection_logs_step(self):
        result = resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertEqual(result["status"], "rejected")
        log = StepLog.objects.filter(
            campaign=self.campaign, step_type="crafting", action_type="crafting_rejected"
        ).first()
        self.assertIsNotNone(log)

    def test_crafting_rejection_does_not_alter_inventory(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)

        resolve_crafting(party=self.party, recipe_def=self.recipe_kit)

        self.assertTrue(InventoryItem.objects.filter(party=self.party, item_def=self.item_rope).exists())
        self.assertFalse(InventoryItem.objects.filter(party=self.party, item_def=self.item_kit).exists())

    def test_crafting_partial_ingredient_available_uses_available_count(self):
        # Have 1 of an ingredient that requires 2 — available reported correctly.
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_draught, quantity=1)
        result = resolve_crafting(party=self.party, recipe_def=self.recipe_draught)
        self.assertEqual(result["available"], 1)


class CraftingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        call_command("seed_warhammer_content")
        self.campaign = Campaign.objects.create(name="CV Campaign", seed="cv-seed-001")
        self.party = Party.objects.create(
            campaign=self.campaign, name="CV Party", gold=500, supplies=10, morale=0
        )
        self.hero = Hero.objects.create(
            party=self.party, name="CV Hero",
            archetype=Hero.Archetype.WARRIOR, level=1, max_health=10, current_health=10,
        )
        self.recipe = CraftingRecipeDef.objects.get(code="whq_exploration_kit")
        self.item_rope = ItemDef.objects.get(name="WHQ Rope")
        self.item_lantern = ItemDef.objects.get(name="WHQ Lantern")

    def test_resolve_crafting_with_ingredients_succeeds(self):
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_rope, quantity=1)
        InventoryItem.objects.create(party=self.party, hero=None, item_def=self.item_lantern, quantity=1)

        response = self.client.post(
            f"/campaign/{self.campaign.id}/craft/",
            {"recipe_def": self.recipe.id},
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_crafting_with_no_party_returns_404(self):
        campaign_empty = Campaign.objects.create(name="Empty Craft", seed="empty-craft-seed")
        response = self.client.post(
            f"/campaign/{campaign_empty.id}/craft/",
            {"recipe_def": self.recipe.id},
        )
        self.assertEqual(response.status_code, 404)

    def test_resolve_crafting_with_invalid_form_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/craft/",
            {"recipe_def": ""},
        )
        self.assertEqual(response.status_code, 302)

    def test_resolve_crafting_with_insufficient_ingredients_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/craft/",
            {"recipe_def": self.recipe.id},
        )
        self.assertEqual(response.status_code, 302)

    def test_gm_console_post_crafting_recipe_form_creates_recipe(self):
        User = get_user_model()
        staff = User.objects.create_user(username="gm-craft", password="pw123", is_staff=True)
        self.client.force_login(staff)
        response = self.client.post(
            "/gm/",
            {
                "form_kind": "crafting_recipe",
                "crafting_recipe-code": "test_recipe_unique",
                "crafting_recipe-name": "Test Recipe Unique",
                "crafting_recipe-definition": "{}",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CraftingRecipeDef.objects.filter(code="test_recipe_unique").exists())
