from django.test import TestCase
from GameData.models import Game, FactionType, Faction, SubFaction, UnitType
# Create your tests here.

# self.assertTrue(func)
# self.assertEqual(func,'output')

class GameDataTests(TestCase):
    """testing the entire model in here because it's structure is simple"""
    @classmethod
    def setUpTestData(cls):
        cls.game_entry_1=Game(game_system_name="Warhammer 40k")
        cls.game_entry_1.save()
        cls.faction_type_1=FactionType(system=cls.game_entry_1,faction_name="Xenos")
        cls.faction_type_1.save()
        cls.faction_1=Faction(faction_type=cls.faction_type_1,faction_name="Eldar")
        cls.faction_1.save()
        cls.faction_2=Faction(faction_type=cls.faction_type_1,faction_name="Ynnari")
        cls.faction_2.save()
        cls.subfaction_1=SubFaction(faction=cls.faction_1,faction_name="Ulthwe")
        cls.subfaction_1.save()
        cls.subfaction_2=SubFaction(faction=cls.faction_1,faction_name="second subfaction")
        cls.subfaction_2.save()
        cls.unit_1=UnitType(system=cls.game_entry_1,unit_type="Wraithguard")
        cls.unit_1.save()
        cls.unit_1.faction.add(cls.faction_1)
        cls.unit_2=UnitType(system=cls.game_entry_1,unit_type="Eldrad Ulthran")
        cls.unit_2.save()
        cls.unit_2.faction.add(cls.faction_1)
        cls.unit_2.sub_faction.add(cls.subfaction_1)
        cls.unit_3=UnitType(system=cls.game_entry_1,unit_type="test unit")
        cls.unit_3.save()
        cls.unit_3.faction.add(cls.faction_1,cls.faction_2)
        cls.unit_4=UnitType(system=cls.game_entry_1,unit_type="test unit 2")
        cls.unit_4.save()
        cls.unit_4.sub_faction.add(cls.subfaction_1,cls.subfaction_2)

    def test_factiontype_string_returns(self):

        self.assertEqual(self.faction_type_1.simple_string(),"Xenos")
        self.assertEqual(str(self.faction_type_1),"Xenos (Warhammer 40k)")

    def test_faction_string_returns(self):

        self.assertEqual(self.faction_1.simple_string(),"Eldar")
        self.assertEqual(str(self.faction_1),"Eldar (Xenos)")

    def test_subfaction_string_returns(self):

        self.assertEqual(self.subfaction_1.simple_string(),"Ulthwe")
        self.assertEqual(str(self.subfaction_1),"Ulthwe [Eldar]")

    def test_unittype_functionality_returns(self):
        """string returns and specific faction check"""

        # check basic strings
        self.assertEqual(self.unit_1.simple_string(),"Wraithguard")
        self.assertEqual(str(self.unit_1),"Wraithguard (Eldar)")
        # check unit 1 is eldar
        self.assertEqual(self.unit_1.get_specific_faction()[0],self.faction_1)
        # check unit 2 is Ulthwe
        self.assertEqual(self.unit_2.get_specific_faction()[0],self.subfaction_1)
        # confirm string output for unit 2
        self.assertEqual(str(self.unit_2),"Eldrad Ulthran (Ulthwe)")
        # check a unit with multipule factions
        self.assertEqual(str(self.unit_3.get_specific_faction()),str(self.unit_3.faction.all()))
        self.assertEqual(str(self.unit_3),"test unit (Eldar) (Ynnari)")
        # check a unit with multipule subfactions
        self.assertEqual(str(self.unit_4.get_specific_faction()),str(self.unit_4.sub_faction.all()))
        self.assertEqual(str(self.unit_4),"test unit 2 (Ulthwe) (second subfaction)")
