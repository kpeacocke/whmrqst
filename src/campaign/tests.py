from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command

from .models import (
    Campaign,
    CatastrophicEventDef,
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
        self.assertEqual(ItemDef.objects.filter(definition__source="whq_roleplay_book").count(), 8)
        self.assertEqual(ExpeditionDef.objects.filter(definition__source="whq_roleplay_book").count(), 4)

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
        self.hero_2.current_health = 10
        self.hero_2.save(update_fields=["current_health", "updated_at"])

        second = resolve_expedition(self.party, self.expedition_def, Expedition.RiskLevel.STANDARD)

        self.assertEqual(first["success"], second["success"])
        self.assertEqual(first["party_gold_delta"], second["party_gold_delta"])
        self.assertEqual(first["party_supplies_delta"], second["party_supplies_delta"])

    def test_expedition_view_endpoint_runs_and_redirects(self):
        response = self.client.post(
            f"/campaign/{self.campaign.id}/expedition/",
            {"expedition_def": self.expedition_def.id, "risk_level": Expedition.RiskLevel.STANDARD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expedition.objects.filter(campaign=self.campaign).exists())
