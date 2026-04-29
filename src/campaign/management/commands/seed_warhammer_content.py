from django.core.management.base import BaseCommand

from campaign.models import (
    CatastrophicEventDef,
    CraftingRecipeDef,
    ExpeditionDef,
    HazardDef,
    ItemDef,
    SettlementEventDef,
    SettlementLocationDef,
    SkillDef,
)


WHQ_SOURCE = "whq_roleplay_book"
SPECIAL_LOCATIONS_SECTION = "Special Locations"
UNEVENTFUL_DAY_NARRATIVE = "Nothing of note happens today."
ITEM_HEALING_DRAUGHT = "WHQ Healing Draught"
ITEM_ROPE = "WHQ Rope"
ITEM_LANTERN = "WHQ Lantern"
ITEM_EXPLORATION_KIT = "WHQ Exploration Kit"
ITEM_ENHANCED_DRAUGHT = "WHQ Enhanced Draught"


class Command(BaseCommand):
    help = "Seed WHQ Roleplay Book travel hazards, settlement events, and catastrophic events"

    def handle(self, *args, **options):
        self._clear_previous_whq_seed()
        self._seed_hazards()
        self._seed_settlement_events()
        self._seed_catastrophic_events()
        self._seed_special_locations()
        self._seed_items()
        self._seed_skills()
        self._seed_expeditions()
        self._seed_crafting_recipes()
        self.stdout.write(self.style.SUCCESS("Warhammer-inspired content tables seeded."))

    def _clear_previous_whq_seed(self):
        HazardDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        SettlementEventDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        CatastrophicEventDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        SettlementLocationDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        CraftingRecipeDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        ItemDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        SkillDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        ExpeditionDef.objects.filter(definition__source=WHQ_SOURCE).delete()
        HazardDef.objects.filter(name__startswith="WHQ ").delete()
        SettlementEventDef.objects.filter(name__startswith="WHQ ").delete()
        CatastrophicEventDef.objects.filter(name__startswith="WHQ ").delete()
        ItemDef.objects.filter(name__startswith="WHQ ").delete()

        HazardDef.objects.filter(name__in=[
            "Brigand Toll",
            "Rotting Provisions",
            "Washed-Out Ford",
            "Beastmen Ambush",
            "Road Tariff",
            "Night Storm",
            "Chaos Cult Pursuit",
            "Witch-Hunter Inspection",
            "Refugee Surge",
        ]).delete()
        SettlementEventDef.objects.filter(name__in=[
            "Fortune Teller's Warning",
            "Pickpocket in the Market",
            "Shrine Blessing",
        ]).delete()
        CatastrophicEventDef.objects.filter(name__in=[
            "Plague Outbreak",
            "Witch-Hunt Panic",
            "Militia Levy",
        ]).delete()

    def _seed_items(self):
        items = [
            ("WHQ Sword", "weapon", 75, 3, 5, "Common steel sidearm."),
            ("WHQ Bow", "weapon", 85, 4, 4, "Reliable hunting bow."),
            ("WHQ Shield", "armour", 65, 2, 6, "Wood and iron shield."),
            ("WHQ Chainmail", "armour", 250, 6, 8, "Heavy defensive hauberk."),
            ("WHQ Provisions", "supply", 10, 1, 2, "One week of supplies."),
            (ITEM_HEALING_DRAUGHT, "consumable", 120, 5, 1, "Restorative tonic sold in settlements."),
            (ITEM_ROPE, "utility", 15, 1, 2, "Adventuring rope and knots."),
            (ITEM_LANTERN, "utility", 20, 2, 2, "Lantern with a flask of oil."),
            (ITEM_EXPLORATION_KIT, "utility", 50, 3, 3, "Rope and lantern packed into a prepared explorer's kit."),
            (ITEM_ENHANCED_DRAUGHT, "consumable", 200, 8, 1, "Two healing draughts concentrated into a single, more potent vial."),
        ]

        for name, category, base_price, stock_value, weight, narrative in items:
            ItemDef.objects.create(
                name=name,
                category=category,
                base_price=base_price,
                stock_value=stock_value,
                weight=weight,
                definition={
                    "source": WHQ_SOURCE,
                    "book_section": "Settlement Equipment",
                    "narrative": narrative,
                },
            )

    def _seed_special_locations(self):
        locations = [
            {
                "code": "alehouse",
                "name": "Alehouse",
                "always_available": True,
                "village_available": True,
                "town_find_target": None,
                "city_find_target": None,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "Always available in villages, towns, and cities.",
                },
            },
            {
                "code": "alchemist",
                "name": "Alchemist's Laboratory",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "Transmutes one unused item into gold for a fee.",
                },
            },
            {
                "code": "dwarf_guildmasters",
                "name": "Dwarf Guildmasters",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "Dwarf-only access to lock tools, firebombs, and runesmith services.",
                },
            },
            {
                "code": "elf_quarter",
                "name": "Elf Quarter",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "Elf-only access to elven gear, waybread, and master craftsmen.",
                },
            },
            {
                "code": "gambling_house",
                "name": "Gambling House",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "May be visited repeatedly; wagers up to 200 gold per day.",
                },
            },
            {
                "code": "temple",
                "name": "Temple",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "50 gold donation grants one roll on temple blessings.",
                },
            },
            {
                "code": "wizards_guild",
                "name": "Wizard's Guild",
                "always_available": False,
                "village_available": False,
                "town_find_target": 7,
                "city_find_target": 7,
                "definition": {
                    "source": WHQ_SOURCE,
                    "book_section": SPECIAL_LOCATIONS_SECTION,
                    "narrative": "Wizard-only consultations, potions, and staff recharging.",
                },
            },
        ]

        for item in locations:
            SettlementLocationDef.objects.create(**item)

    def _seed_skills(self):
        skills = [
            # Warrior skills
            ("WHQ Combat Master", "warrior", "Reroll one failed attack roll per combat phase."),
            ("WHQ Battle Fury", "warrior", "May make one extra attack when charging."),
            # Ranger skills
            ("WHQ Tracking", "ranger", "Party reduces travel hazard count by one per journey."),
            ("WHQ Ambush", "ranger", "Party strikes first on surprise hazard encounters."),
            # Mage skills
            ("WHQ Spell Focus", "mage", "One additional power token per settlement visit."),
            ("WHQ Arcane Resistance", "mage", "Negates one magic-based settlement event penalty per week."),
            # Priest skills
            ("WHQ Divine Blessing", "priest", "Once per settlement phase, heal one hero for 1d3 health."),
            ("WHQ Healing Touch", "priest", "Rest action heals +1 additional health for the party."),
        ]

        for name, archetype, description in skills:
            SkillDef.objects.create(
                name=name,
                archetype=archetype,
                description=description,
                definition={"source": WHQ_SOURCE, "book_section": "Skills"},
            )

    def _seed_expeditions(self):
        loot_tables = {
            "ruins_delve": [
                {"item_name": ITEM_ROPE, "weight": 4},
                {"item_name": ITEM_LANTERN, "weight": 3},
                {"item_name": ITEM_HEALING_DRAUGHT, "weight": 3},
            ],
            "road_escort": [
                {"item_name": ITEM_ROPE, "weight": 3},
                {"item_name": ITEM_HEALING_DRAUGHT, "weight": 2},
                {"item_name": "WHQ Provisions", "weight": 5},
            ],
            "beast_hunt": [
                {"item_name": ITEM_HEALING_DRAUGHT, "weight": 4},
                {"item_name": "WHQ Bow", "weight": 3},
                {"item_name": ITEM_ROPE, "weight": 3},
            ],
            "relic_recovery": [
                {"item_name": ITEM_HEALING_DRAUGHT, "weight": 3},
                {"item_name": "WHQ Chainmail", "weight": 2},
                {"item_name": "WHQ Sword", "weight": 3},
                {"item_name": ITEM_LANTERN, "weight": 2},
            ],
        }
        expeditions = [
            ("ruins_delve", "Ruins Delve", 40, 120, 2, 2, 4, "Recover artefacts from dangerous ruins."),
            ("road_escort", "Road Escort", 25, 90, 1, 2, 3, "Escort merchants through contested roads."),
            ("beast_hunt", "Beast Hunt", 55, 160, 2, 3, 5, "Track and kill a marauding beast."),
            ("relic_recovery", "Relic Recovery", 65, 180, 3, 3, 6, "Retrieve a sacred relic from hostile ground."),
        ]
        for code, name, reward_min, reward_max, supply_cost, injury_risk, difficulty, narrative in expeditions:
            ExpeditionDef.objects.create(
                code=code,
                name=name,
                base_reward_min=reward_min,
                base_reward_max=reward_max,
                base_supply_cost=supply_cost,
                base_injury_risk=injury_risk,
                difficulty=difficulty,
                definition={
                    "source": WHQ_SOURCE,
                    "book_section": "Expeditions",
                    "narrative": narrative,
                    "loot_table": loot_tables[code],
                },
            )

    def _seed_crafting_recipes(self):
        recipes = [
            (
                "whq_exploration_kit",
                ITEM_EXPLORATION_KIT,
                [
                    {"item_name": ITEM_ROPE, "quantity": 1},
                    {"item_name": ITEM_LANTERN, "quantity": 1},
                ],
                ITEM_EXPLORATION_KIT,
                1,
                "Bind a rope and lantern into a prepared explorer's kit for extended expeditions.",
            ),
            (
                "whq_enhanced_draught",
                ITEM_ENHANCED_DRAUGHT,
                [
                    {"item_name": ITEM_HEALING_DRAUGHT, "quantity": 2},
                ],
                ITEM_ENHANCED_DRAUGHT,
                1,
                "Reduce two healing draughts into a single, more potent restoration vial.",
            ),
        ]
        for code, name, ingredients, output_item_name, output_quantity, narrative in recipes:
            CraftingRecipeDef.objects.create(
                code=code,
                name=name,
                definition={
                    "source": WHQ_SOURCE,
                    "book_section": "Crafting",
                    "narrative": narrative,
                    "ingredients": ingredients,
                    "output_item_name": output_item_name,
                    "output_quantity": output_quantity,
                },
            )

    def _seed_hazards(self):
        # Derived from WHQ Roleplay Book "Hazards Table" (D66), grouped into
        # travel tiers to fit the current settlement-size data model.
        table = {
            HazardDef.SettlementSize.VILLAGE: [
                ("WHQ 11 Massacre", {"weight": 1, "table_roll": "11", "narrative": "A massacre site hardens the party against a hated foe.", "effects": [{"type": "morale_change", "min": 1, "max": 2}]}),
                ("WHQ 12 Fire", {"weight": 1, "table_roll": "12", "narrative": "Campfire disaster threatens coin and gear.", "effects": [{"type": "gold_loss", "min": 1, "max": 6}]}),
                ("WHQ 13 Chapel", {"weight": 1, "table_roll": "13", "narrative": "Offerings at a roadside chapel steady the spirit.", "effects": [{"type": "morale_change", "min": 1, "max": 2}]}),
                ("WHQ 14 Quake", {"weight": 1, "table_roll": "14", "narrative": "A vast chasm blocks the route and forces delays.", "effects": [{"type": "extra_hazards", "min": 1, "max": 2}]}),
                ("WHQ 15 Stranger", {"weight": 1, "table_roll": "15", "narrative": "A shortcut guide may help or leave the party lost.", "effects": [{"type": "extra_hazards", "min": 0, "max": 1}, {"type": "gold_loss", "min": -4, "max": 2}]}),
                ("WHQ 16 Pedlar", {"weight": 1, "table_roll": "16", "narrative": "A roadside pedlar sells dubious wares.", "effects": [{"type": "gold_loss", "min": 1, "max": 4}]}),
                ("WHQ 21 Tornado", {"weight": 1, "table_roll": "21", "narrative": "A tornado scatters gear, wounds travellers, and delays the road.", "effects": [{"type": "injury_random_hero", "min": 1, "max": 3}, {"type": "gold_loss", "min": 2, "max": 8}, {"type": "extra_hazards", "min": 0, "max": 1}]}),
                ("WHQ 22 Uneventful Week", {"weight": 1, "table_roll": "22", "narrative": "The week passes without incident.", "effects": []}),
                ("WHQ 23 Plague Town", {"weight": 1, "table_roll": "23", "narrative": "The route ends in a plague town with lingering weakness.", "effects": [{"type": "injury_random_hero", "min": 1, "max": 2}, {"type": "morale_change", "min": -2, "max": -1}]}),
                ("WHQ 24 Uneventful Week", {"weight": 1, "table_roll": "24", "narrative": "No notable danger this week.", "effects": []}),
                ("WHQ 25 Prisoner", {"weight": 1, "table_roll": "25", "narrative": "Mercenary escort and prisoner crisis costs time or blood.", "effects": [{"type": "gold_loss", "min": -3, "max": 4}, {"type": "extra_hazards", "min": 0, "max": 1}]}),
                ("WHQ 26 Guests", {"weight": 1, "table_roll": "26", "narrative": "Festival hospitality trades time for coin.", "effects": [{"type": "gold_loss", "min": 1, "max": 4}]})
            ],
            HazardDef.SettlementSize.TOWN: [
                ("WHQ 31 Witch's Cave", {"weight": 1, "table_roll": "31", "narrative": "A cave witch bargains in potions with unpredictable effects.", "effects": [{"type": "gold_loss", "min": 1, "max": 6}, {"type": "injury_random_hero", "min": 0, "max": 2}]}),
                ("WHQ 32 Famine", {"weight": 1, "table_roll": "32", "narrative": "Famine-struck villages plead for charity.", "effects": [{"type": "gold_loss", "min": 1, "max": 6}, {"type": "morale_change", "min": 1, "max": 2}]}),
                ("WHQ 33 Uneventful Week", {"weight": 1, "table_roll": "33", "narrative": "A plain week on the road.", "effects": []}),
                ("WHQ 34 Bad Map", {"weight": 1, "table_roll": "34", "narrative": "A bad map leads to an undersupplied hamlet.", "effects": [{"type": "morale_change", "min": -1, "max": 0}]}),
                ("WHQ 35 Pool of Dreams", {"weight": 1, "table_roll": "35", "narrative": "A prophetic pool grants glimpses that ward against harm.", "effects": [{"type": "morale_change", "min": 1, "max": 2}]}),
                ("WHQ 36 Lightning", {"weight": 1, "table_roll": "36", "narrative": "Lightning shreds armour and scorches supplies.", "effects": [{"type": "supplies_loss", "min": 1, "max": 3}, {"type": "injury_random_hero", "min": 1, "max": 2}]}),
                ("WHQ 41 Lost", {"weight": 1, "table_roll": "41", "narrative": "The party is lost and reaches an unplanned village.", "effects": [{"type": "extra_hazards", "min": 1, "max": 2}]}),
                ("WHQ 42 Flooded Crossing", {"weight": 1, "table_roll": "42", "narrative": "Floodwaters force paid passage across a blockage.", "effects": [{"type": "gold_loss", "min": 2, "max": 4}]}),
                ("WHQ 43 Waylaid", {"weight": 1, "table_roll": "43", "narrative": "Storm recovery aid delays the road by a week.", "effects": [{"type": "extra_hazards", "min": 1, "max": 1}]}),
                ("WHQ 44 Uneventful Week", {"weight": 1, "table_roll": "44", "narrative": "The route remains quiet.", "effects": []}),
                ("WHQ 45 Which Road", {"weight": 1, "table_roll": "45", "narrative": "A fork in the road may end the journey early.", "effects": [{"type": "morale_change", "min": -1, "max": 1}]}),
                ("WHQ 46 Ambush", {"weight": 1, "table_roll": "46", "narrative": "Forest goblin riders ambush the party.", "effects": [{"type": "gold_loss", "min": -3, "max": 8}, {"type": "injury_random_hero", "min": 1, "max": 2}]})
            ],
            HazardDef.SettlementSize.CITY: [
                ("WHQ 51 Uneventful Week", {"weight": 1, "table_roll": "51", "narrative": "A calm march toward the city.", "effects": []}),
                ("WHQ 52 Blizzard", {"weight": 1, "table_roll": "52", "narrative": "A blizzard forces refuge in a nearby village.", "effects": [{"type": "supplies_loss", "min": 1, "max": 4}, {"type": "extra_hazards", "min": 1, "max": 1}]}),
                ("WHQ 53 Double Back", {"weight": 1, "table_roll": "53", "narrative": "The party circles back to the dungeon exit.", "effects": [{"type": "extra_hazards", "min": 2, "max": 3}, {"type": "morale_change", "min": -2, "max": -1}]}),
                ("WHQ 54 Rockfall", {"weight": 1, "table_roll": "54", "narrative": "A ravine rockfall demands paid labour to clear.", "effects": [{"type": "gold_loss", "min": 2, "max": 6}]}),
                ("WHQ 55 Wagon Train", {"weight": 1, "table_roll": "55", "narrative": "A paid wagon convoy can shave time off travel.", "effects": [{"type": "gold_loss", "min": 1, "max": 3}, {"type": "extra_hazards", "min": -1, "max": 0}]}),
                ("WHQ 56 Uneventful Week", {"weight": 1, "table_roll": "56", "narrative": "A steady week on the high road.", "effects": []}),
                ("WHQ 61 Militia", {"weight": 1, "table_roll": "61", "narrative": "Local militia extorts passage payment or delays the route.", "effects": [{"type": "gold_loss", "min": 2, "max": 4}, {"type": "extra_hazards", "min": 0, "max": 1}]}),
                ("WHQ 62 Brigands", {"weight": 1, "table_roll": "62", "narrative": "Brigands demand payment on the settlement outskirts.", "effects": [{"type": "gold_loss", "min": 2, "max": 8}, {"type": "injury_random_hero", "min": 0, "max": 2}]}),
                ("WHQ 63 Travelling Minstrel", {"weight": 1, "table_roll": "63", "narrative": "A minstrel joins the road and influences settlement reception.", "effects": [{"type": "morale_change", "min": -1, "max": 2}]}),
                ("WHQ 64 Fall", {"weight": 1, "table_roll": "64", "narrative": "A bad fall slows travel and needs healing on arrival.", "effects": [{"type": "injury_random_hero", "min": 1, "max": 3}, {"type": "extra_hazards", "min": 1, "max": 2}]}),
                ("WHQ 65 Glorious Weather", {"weight": 1, "table_roll": "65", "narrative": "Fine weather tempts the party to linger on the road.", "effects": [{"type": "morale_change", "min": 1, "max": 2}, {"type": "extra_hazards", "min": 1, "max": 1}]}),
                ("WHQ 66 Storm", {"weight": 1, "table_roll": "66", "narrative": "A violent storm ruins treasured equipment.", "effects": [{"type": "supplies_loss", "min": 1, "max": 4}, {"type": "morale_change", "min": -2, "max": -1}]})
            ],
        }

        for settlement_size, hazards in table.items():
            for index, (name, definition) in enumerate(hazards, start=1):
                HazardDef.objects.create(
                    name=name,
                    settlement_size=settlement_size,
                    severity=index,
                    definition={
                        "source": WHQ_SOURCE,
                        "book_section": "Hazards Table",
                        **definition,
                    },
                )

    def _seed_settlement_events(self):
        # Full D66 coverage from the WHQ Roleplay Book Settlement Events table.
        events = [
            ("WHQ 11 Thrown Out", 1, {"table_roll": "11", "narrative": "Wild behaviour gets the warrior expelled from town.", "effects": [{"type": "party_gold", "min": -6, "max": -1}, {"type": "party_morale", "min": -2, "max": -1}]}),
            ("WHQ 12 Pickpocket", 1, {"table_roll": "12", "narrative": "A thief cuts the purse strings in a crowded street.", "effects": [{"type": "party_gold", "min": -6, "max": -1}]}),
            ("WHQ 13 Uneventful Day", 1, {"table_roll": "13", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 14 Good Deed", 1, {"table_roll": "14", "narrative": "A supposed rescue becomes a blunt street robbery.", "effects": [{"type": "party_gold", "min": -6, "max": -1}]}),
            ("WHQ 15 Investment", 1, {"table_roll": "15", "narrative": "A merchant sells a share in a risky trading venture.", "effects": [{"type": "party_gold", "min": -5, "max": -1}], "rule_flag": "future_income"}),
            ("WHQ 16 Steam Bath", 1, {"table_roll": "16", "narrative": "A steam bath leaves the warrior feeling hardier.", "effects": [{"type": "hero_health", "min": 1, "max": 2}]}),
            ("WHQ 21 Fight", 1, {"table_roll": "21", "narrative": "A market dispute escalates into a profitable or costly brawl.", "effects": [{"type": "party_gold", "min": -6, "max": 6}]}),
            ("WHQ 22 Uneventful Day", 1, {"table_roll": "22", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 23 Fooled", 1, {"table_roll": "23", "narrative": "A purchase is revealed as a fake and discarded.", "effects": [{"type": "party_gold", "min": -4, "max": -1}]}),
            ("WHQ 24 Circus", 1, {"table_roll": "24", "narrative": "A travelling circus and fortune teller lighten the purse.", "effects": [{"type": "party_gold", "min": -6, "max": -2}]}),
            ("WHQ 25 Reward", 1, {"table_roll": "25", "narrative": "A murderer hunt can end in reward, bribe, or disappointment.", "effects": [{"type": "party_gold", "min": -5, "max": 5}]}),
            ("WHQ 26 Betrothed", 1, {"table_roll": "26", "narrative": "A mistaken identity lands the warrior in a forced betrothal.", "effects": [{"type": "party_morale", "min": -2, "max": -1}], "rule_flag": "forced_departure_or_delay"}),
            ("WHQ 31 Drugged", 1, {"table_roll": "31", "narrative": "A strange drink leaves the warrior weakened or merely hungover.", "effects": [{"type": "hero_health", "min": -2, "max": 0}]}),
            ("WHQ 32 Uneventful Day", 1, {"table_roll": "32", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 33 Honest Day's Work", 1, {"table_roll": "33", "narrative": "Hard labour at the docks earns a modest wage.", "effects": [{"type": "party_gold", "min": 2, "max": 2}]}),
            ("WHQ 34 Riotous Living", 1, {"table_roll": "34", "narrative": "Comfort and extravagance burn through coin.", "effects": [{"type": "party_gold", "min": -5, "max": -5}]}),
            ("WHQ 35 Duel", 1, {"table_roll": "35", "narrative": "A tavern insult leads to a dawn duel with serious stakes.", "effects": [{"type": "hero_health", "min": -3, "max": -1}, {"type": "party_gold", "min": -2, "max": 10}], "rule_flag": "may_force_departure"}),
            ("WHQ 36 Uneventful Day", 1, {"table_roll": "36", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 41 Gambling", 1, {"table_roll": "41", "narrative": "A shady dice game swings wildly between loss and gain.", "effects": [{"type": "party_gold", "min": -6, "max": 18}]}),
            ("WHQ 42 Uneventful Day", 1, {"table_roll": "42", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 43 Join the Watch", 1, {"table_roll": "43", "narrative": "The watch pressgangs the warrior for a week of service.", "effects": [{"type": "party_gold", "min": -4, "max": 2}], "rule_flag": "service_delay"}),
            ("WHQ 44 Illness", 1, {"table_roll": "44", "narrative": "Illness forces bed rest, medicine costs, and lost time.", "effects": [{"type": "party_gold", "min": -2, "max": -2}, {"type": "hero_health", "min": -2, "max": -1}], "rule_flag": "bed_rest"}),
            ("WHQ 45 Pet Dog", 1, {"table_roll": "45", "narrative": "A stray dog adopts the warrior and becomes an expensive companion.", "effects": [{"type": "party_gold", "min": -1, "max": -1}, {"type": "party_morale", "min": 1, "max": 2}], "rule_flag": "pet_dog"}),
            ("WHQ 46 Runaway Bull", 1, {"table_roll": "46", "narrative": "A runaway bull brings chaos, injury, and possible applause.", "effects": [{"type": "hero_health", "min": -2, "max": -1}, {"type": "party_gold", "min": -10, "max": 15}]}),
            ("WHQ 51 Crime", 1, {"table_roll": "51", "narrative": "The warrior is jailed on a false murder charge until bailed out.", "effects": [{"type": "party_gold", "min": -3, "max": -1}, {"type": "party_morale", "min": -2, "max": -1}], "rule_flag": "jail"}),
            ("WHQ 52 Uneventful Day", 1, {"table_roll": "52", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 53 Counterfeit", 1, {"table_roll": "53", "narrative": "Counterfeit coin is discovered and confiscated.", "effects": [{"type": "party_gold", "min": -6, "max": -1}], "rule_flag": "may_force_departure"}),
            ("WHQ 54 Beggars", 1, {"table_roll": "54", "narrative": "Beggars strip coin from the compassionate or desperate.", "effects": [{"type": "party_gold", "min": -6, "max": 2}, {"type": "party_morale", "min": 0, "max": 2}]}),
            ("WHQ 55 Debt", 1, {"table_roll": "55", "narrative": "An old debt collector arrives with ruinous interest.", "effects": [{"type": "party_gold", "min": -6, "max": -2}]}),
            ("WHQ 56 Uneventful Day", 1, {"table_roll": "56", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 61 Temple Donation", 1, {"table_roll": "61", "narrative": "A donation buys divine favour for the next fight.", "effects": [{"type": "party_gold", "min": -5, "max": -1}, {"type": "party_morale", "min": 1, "max": 2}], "rule_flag": "reroll_attack_once"}),
            ("WHQ 62 Uneventful Day", 1, {"table_roll": "62", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 63 Hunting", 1, {"table_roll": "63", "narrative": "A ridiculous night hunt wastes the day to no effect.", "effects": []}),
            ("WHQ 64 Witchcraft", 1, {"table_roll": "64", "narrative": "An angry mob accuses the warrior of witchcraft.", "effects": [{"type": "party_gold", "min": 0, "max": 5}, {"type": "party_morale", "min": -2, "max": 1}], "rule_flag": "possible_disguise_or_exile"}),
            ("WHQ 65 Uneventful Day", 1, {"table_roll": "65", "narrative": UNEVENTFUL_DAY_NARRATIVE, "effects": []}),
            ("WHQ 66 Accident", 1, {"table_roll": "66", "narrative": "A wagon accident sends the warrior to the infirmary for days.", "effects": [{"type": "hero_health", "min": -2, "max": -1}], "rule_flag": "recovery_delay"}),
        ]

        for name, weight, definition in events:
            SettlementEventDef.objects.create(
                name=name,
                weight=weight,
                definition={
                    "source": WHQ_SOURCE,
                    "book_section": "Settlement Events",
                    **definition,
                },
            )

    def _seed_catastrophic_events(self):
        # Derived directly from WHQ Roleplay Book "Catastrophic Events Table"
        # (2D6). Weights mirror 2D6 probability distribution.
        events = [
            (
                "WHQ Catastrophic 2 Settle Down",
                1,
                {
                    "table_roll": "2",
                    "narrative": "A warrior settles down and leaves the adventuring life.",
                    "effects": [
                        {"type": "party_morale", "min": -4, "max": -2},
                    ],
                },
            ),
            (
                "WHQ Catastrophic 3 Flood",
                2,
                {
                    "table_roll": "3",
                    "narrative": "Flooding shuts down trade and forces immediate departure.",
                    "effects": [{"type": "party_morale", "min": -3, "max": -1}],
                },
            ),
            (
                "WHQ Catastrophic 4 Attack",
                3,
                {
                    "table_roll": "4",
                    "narrative": "Greenskin assault pressgangs the party into brutal defence.",
                    "effects": [
                        {"type": "hero_health", "min": -3, "max": -1},
                        {"type": "party_morale", "min": -2, "max": 1},
                        {"type": "extra_hazards", "min": 0, "max": 2},
                    ],
                },
            ),
            (
                "WHQ Catastrophic 5 Hardship",
                4,
                {
                    "table_roll": "5",
                    "narrative": "Hardship grips the settlement and prices soar.",
                    "effects": [{"type": "party_gold", "min": -12, "max": -6}],
                },
            ),
            (
                "WHQ Catastrophic 6-9 No Event",
                20,
                {
                    "table_roll": "6-9",
                    "narrative": "No catastrophic event this week.",
                    "effects": [],
                },
            ),
            (
                "WHQ Catastrophic 10 Disease",
                3,
                {
                    "table_roll": "10",
                    "narrative": "Disease sweeps the settlement; staying risks lethal infection.",
                    "effects": [
                        {"type": "hero_health", "min": -4, "max": -2},
                        {"type": "party_morale", "min": -3, "max": -1},
                    ],
                },
            ),
            (
                "WHQ Catastrophic 11 Fire",
                2,
                {
                    "table_roll": "11",
                    "narrative": "Fire devastates the settlement and the party is blamed.",
                    "effects": [
                        {"type": "party_gold", "min": -10, "max": -4},
                        {"type": "party_morale", "min": -3, "max": -1},
                    ],
                },
            ),
            (
                "WHQ Catastrophic 12 Plague",
                1,
                {
                    "table_roll": "12",
                    "narrative": "Plague strikes a warrior unless costly treatment is paid.",
                    "effects": [
                        {"type": "hero_health", "min": -4, "max": -2},
                        {"type": "party_gold", "min": -12, "max": -4},
                    ],
                },
            ),
        ]

        for name, weight, definition in events:
            CatastrophicEventDef.objects.create(
                name=name,
                weight=weight,
                definition={
                    "source": WHQ_SOURCE,
                    "book_section": "Catastrophic Events",
                    **definition,
                },
            )
