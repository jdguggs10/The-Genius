import unittest
from unittest.mock import patch, Mock, MagicMock

from baseball_mcp.utils import activity_to_dict, ACTIVITY_MAP # Assuming ACTIVITY_MAP is in utils or accessible
# If ACTIVITY_MAP is in metadata, the import would be: from baseball_mcp.metadata import ACTIVITY_MAP

# For mocking, we need to patch where the functions are LOOKED UP, not where they are defined.
# So, if activity_to_dict calls team_to_dict and player_to_dict from its own module (utils.py),
# we patch 'baseball_mcp.utils.team_to_dict' and 'baseball_mcp.utils.player_to_dict'.

# Mocking ACTIVITY_MAP if it's complex or to ensure test stability
# If ACTIVITY_MAP is simple and stable, direct import is fine.
# For this test, let's assume it's imported and used as is.
# If it's in metadata.py: from baseball_mcp.metadata import ACTIVITY_MAP
# For now, let's define a simple one for testing if not easily importable or to override
TEST_ACTIVITY_MAP = {
    'ADD': [2, 178],      # FA ADD, WAIVER ADD
    'DROP': [3, 179],     # FA DROP, WAIVER DROP
    'TRADE_ACCEPTED': [172, 244],
    'WAIVER_MOVED': [180], # WAIVER ADD (distinct from general ADD for testing if needed)
}

# This is the map defined within activity_to_dict in the previous step.
# We don't need to redefine it here unless we want to test its modification.
# from baseball_mcp.utils import SPECULATIVE_ACTION_TYPE_MAP (if it's made global)
# For now, assume activity_to_dict uses its internal one.


# Helper classes for creating mock objects
class MockPlayer:
    def __init__(self, player_id, name="Mock Player"):
        self.playerId = player_id
        self.player_id = player_id # some parts of code might use this
        self.name = name
        # Add other attributes if player_to_dict mock expects them or if real player_to_dict is used

class MockTeam:
    def __init__(self, team_id, team_name="Mock Team"):
        self.team_id = team_id
        self.team_name = team_name
        # Add other attributes as needed

class MockAction:
    def __init__(self, action_type=None, team_id=None, player=None, player_id=None, 
                 from_team_id=None, to_team_id=None, source=None, bid_amount=None):
        # For action_item.type
        if action_type is not None:
            self.type = action_type 
        
        # For action_item.teamId
        if team_id is not None:
            self.teamId = team_id
        
        # For action_item.player (object)
        if player is not None:
            self.player = player
        
        # For action_item.playerId
        if player_id is not None:
            self.playerId = player_id

        # For trade-related fields
        if from_team_id is not None: self.fromTeamId = from_team_id
        if to_team_id is not None: self.toTeamId = to_team_id
        
        # For waiver related fields
        if source is not None: self.source = source
        if bid_amount is not None: self.bidAmount = bid_amount # Matching 'bidAmount' from patch

        # Attributes like playerAdded/playerDropped can be added dynamically via Mock
        # e.g., action_mock.playerAdded = MockPlayer(101)

class MockActivity:
    def __init__(self, date="2023-01-01T12:00:00Z", msg_type=None, team=None, 
                 player=None, players_in=None, players_out=None, 
                 trade_partner=None, actions=None, source=None, bid_amount=None):
        self.date = date
        if msg_type is not None:
            self.msg_type = msg_type
        if team is not None:
            self.team = team # Should be a MockTeam instance or None
        if player is not None:
            self.player = player # Should be a MockPlayer instance or None
        if players_in is not None:
            self.players_in = players_in # List of MockPlayer instances
        if players_out is not None:
            self.players_out = players_out # List of MockPlayer instances
        if trade_partner is not None:
            self.trade_partner = trade_partner # MockTeam instance
        if actions is not None:
            self.actions = actions # List of MockAction instances or mock objects
        if source is not None: # For primary attribute source
            self.source = source
        if bid_amount is not None: # For primary attribute bid_amount
            self.bid_amount = bid_amount


@patch('baseball_mcp.utils.ACTIVITY_MAP', TEST_ACTIVITY_MAP) # Patch the map used by the function
class TestActivityToDict(unittest.TestCase):

    def _mock_player_to_dict_simple(self, player_obj):
        if not player_obj: return None
        # Simulate placeholder for non-MockPlayer objects if they sneak in
        if not isinstance(player_obj, (MockPlayer, Mock)):
             return {"player_id": "unknown_player_obj", "name": "Unknown Player Object Type"}
        return {"player_id": getattr(player_obj, 'playerId', getattr(player_obj, 'player_id', None)), 
                "name": getattr(player_obj, 'name', "Default Mock Name")}

    def _mock_team_to_dict_simple(self, team_obj):
        if not team_obj: return None
        if not isinstance(team_obj, (MockTeam, Mock)):
            return {"team_id": "unknown_team_obj", "team_name": "Unknown Team Object Type"}
        return {"team_id": team_obj.team_id, "team_name": team_obj.team_name}

    def setUp(self):
        # Patch the helper functions within the utils module for all tests in this class
        self.patcher_player_to_dict = patch('baseball_mcp.utils.player_to_dict', side_effect=self._mock_player_to_dict_simple)
        self.patcher_team_to_dict = patch('baseball_mcp.utils.team_to_dict', side_effect=self._mock_team_to_dict_simple)
        
        self.mock_player_to_dict = self.patcher_player_to_dict.start()
        self.mock_team_to_dict = self.patcher_team_to_dict.start()

    def tearDown(self):
        self.patcher_player_to_dict.stop()
        self.patcher_team_to_dict.stop()

    # --- Test Scenarios ---

    def test_scenario_a_legacy_path_add(self, mock_activity_map_ignored): # mock_activity_map_ignored due to class decorator
        mock_team_obj = MockTeam(1, "Team Alpha")
        mock_player_obj = MockPlayer(101, "Player One")
        activity = MockActivity(msg_type=2, team=mock_team_obj, player=mock_player_obj) # msg_type 2 is ADD in TEST_ACTIVITY_MAP

        result = activity_to_dict(activity)

        self.assertEqual(result["type"], "ADD")
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 1)
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 101)
        self.mock_team_to_dict.assert_called_once_with(mock_team_obj)
        self.mock_player_to_dict.assert_called_once_with(mock_player_obj)
        # Check that actions were not parsed if not needed (tricky to check directly, but type wasn't UNKNOWN)

    def test_scenario_b_fallback_type_from_action_type_playeradded(self, mock_activity_map_ignored):
        # msg_type is None, type should come from action.type
        mock_action_player = MockPlayer(202, "Player Two")
        action1 = MockAction(action_type="PLAYERADDED", player=mock_action_player, team_id=5) # SPECULATIVE_ACTION_TYPE_MAP maps PLAYERADDED to ADD
        activity = MockActivity(msg_type=None, team=None, actions=[action1])
        
        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "ADD")
        self.assertIsNotNone(result["added_player"]) # Should be populated by fallback
        self.assertEqual(result["added_player"]["player_id"], 202)
        self.assertIsNotNone(result["team"]) # Team from action
        self.assertEqual(result["team"]["team_id"], 5)
        self.assertEqual(result["team"]["team_name"], "Team 5 (from action)")


    def test_scenario_b_fallback_type_from_action_attribute_playeradded(self, mock_activity_map_ignored):
        # msg_type is None, type should come from action attribute (playerAdded)
        mock_main_team = MockTeam(1, "Team Main") # activity.team is present
        mock_added_player_in_action = MockPlayer(303, "Player Three")
        
        action1 = MockAction(team_id=1) # Action is for team 1
        # Dynamically add 'playerAdded' attribute to the mock action object
        action1.playerAdded = mock_added_player_in_action 
        
        activity = MockActivity(msg_type=999, team=mock_main_team, actions=[action1]) # 999 is UNKNOWN

        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "ADD") # Inferred from action1.playerAdded
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 1) # From primary activity.team
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 303)


    def test_scenario_b_fallback_type_trade_from_action(self, mock_activity_map_ignored):
        action1 = MockAction(action_type="PLAYERMOVED", team_id=10) # PLAYERMOVED maps to TRADE_ACCEPTED
        activity = MockActivity(msg_type=None, team=None, actions=[action1])
        
        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "TRADE_ACCEPTED")
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 10)

    def test_scenario_b_unknown_type_from_actions(self, mock_activity_map_ignored):
        action1 = MockAction(action_type="SOME_WEIRD_ACTION_TYPE") # Not in SPECULATIVE_ACTION_TYPE_MAP
        activity = MockActivity(msg_type=999, team=None, actions=[action1]) # msg_type 999 is UNKNOWN
        
        result = activity_to_dict(activity)
        self.assertTrue(result["type"].startswith("UNKNOWN_"))
        self.assertEqual(result["type"], "UNKNOWN_999") # Falls back to original msg_type for UNKNOWN naming

    def test_scenario_c_fallback_team_from_action(self, mock_activity_map_ignored):
        action1 = MockAction(team_id=7, action_type="PLAYERADDED") # Action provides teamId
        mock_action_player = MockPlayer(101)
        action1.player = mock_action_player # Player info also from action
        activity = MockActivity(msg_type=None, team=None, actions=[action1])

        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "ADD") # Type from action
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 7)
        self.assertEqual(result["team"]["team_name"], "Team 7 (from action)")
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 101)

    def test_scenario_d_fallback_player_add_from_action_player_obj(self, mock_activity_map_ignored):
        # Type is ADD (from msg_type), activity.player is None, player info from action.player
        mock_team_obj = MockTeam(1)
        mock_action_player = MockPlayer(404, "Player Four From Action")
        action1 = MockAction(action_type="PLAYERADDED", player=mock_action_player) # Action confirms ADD and provides player
        
        activity = MockActivity(msg_type=2, team=mock_team_obj, player=None, actions=[action1]) # msg_type 2 is ADD

        result = activity_to_dict(activity)

        self.assertEqual(result["type"], "ADD")
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 404)
        self.assertEqual(result["added_player"]["name"], "Player Four From Action")

    def test_scenario_d_fallback_player_add_from_action_player_id(self, mock_activity_map_ignored):
        # Type is ADD (inferred from action), activity.player is None, player info (ID only) from action.playerId
        action1 = MockAction(action_type="PLAYERADDED", player_id=505) # Action implies ADD and provides playerId
        mock_team_action = MockAction(team_id=3) # Action also provides team
        
        activity = MockActivity(msg_type=None, team=None, player=None, actions=[action1, mock_team_action])

        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "ADD")
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 505)
        self.assertEqual(result["added_player"]["name"], "Player (from action)") # Placeholder name
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 3)

    def test_scenario_d_fallback_trade_players_from_actions(self, mock_activity_map_ignored):
        # Type is TRADE_ACCEPTED (from msg_type). activity.players_in/out are None.
        # Players derived from actions.
        mock_main_team = MockTeam(1, "Team Main") # Perspective team
        
        player_in_obj = MockPlayer(701, "Player In")
        player_out_obj = MockPlayer(702, "Player Out")

        action_player_in = MockAction(action_type="PLAYERMOVED", player=player_in_obj, to_team_id=1, from_team_id=2)
        action_player_out = MockAction(action_type="PLAYERMOVED", player=player_out_obj, to_team_id=2, from_team_id=1)
        
        # msg_type 172 is TRADE_ACCEPTED in TEST_ACTIVITY_MAP
        activity = MockActivity(msg_type=172, team=mock_main_team, players_in=None, players_out=None, 
                                actions=[action_player_in, action_player_out])

        result = activity_to_dict(activity)
        
        self.assertEqual(result["type"], "TRADE_ACCEPTED")
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 1)

        self.assertIsNotNone(result.get("players_in"))
        self.assertEqual(len(result["players_in"]), 1)
        self.assertEqual(result["players_in"][0]["player_id"], 701)
        
        self.assertIsNotNone(result.get("players_out"))
        self.assertEqual(len(result["players_out"]), 1)
        self.assertEqual(result["players_out"][0]["player_id"], 702)

    def test_scenario_e_mixed_type_from_msg_team_from_action(self, mock_activity_map_ignored):
        # msg_type 2 is ADD. activity.team is None. Team info from action.
        mock_player_obj = MockPlayer(101, "Player One")
        action_with_team = MockAction(team_id=15)
        
        activity = MockActivity(msg_type=2, team=None, player=mock_player_obj, actions=[action_with_team])

        result = activity_to_dict(activity)

        self.assertEqual(result["type"], "ADD") # From msg_type
        self.assertIsNotNone(result["team"])
        self.assertEqual(result["team"]["team_id"], 15) # From action
        self.assertEqual(result["team"]["team_name"], "Team 15 (from action)")
        self.assertIsNotNone(result["added_player"])
        self.assertEqual(result["added_player"]["player_id"], 101) # From primary attribute

    def test_scenario_f_empty_actions_unknown_msg_type(self, mock_activity_map_ignored):
        activity = MockActivity(msg_type=999, actions=None) # Unknown msg_type, no actions
        result = activity_to_dict(activity)
        self.assertEqual(result["type"], "UNKNOWN_999")
        self.assertIsNone(result["team"])
        self.assertNotIn("added_player", result) # Or assertIsNone if key is always present

        activity_empty_actions = MockActivity(msg_type=888, actions=[]) # Unknown msg_type, empty actions list
        result_empty = activity_to_dict(activity_empty_actions)
        self.assertEqual(result_empty["type"], "UNKNOWN_888")
        self.assertIsNone(result_empty["team"])

    def test_scenario_f_unparseable_actions(self, mock_activity_map_ignored):
        # Actions list with something that's not an object or dict, or has no useful info
        activity = MockActivity(msg_type=777, actions=["just_a_string", None, MockAction()])
        result = activity_to_dict(activity)
        self.assertEqual(result["type"], "UNKNOWN_777") # No type derived from these actions
        self.assertIsNone(result["team"]) # No team info from these actions

    def test_scenario_g_error_handling_player_to_dict_exception(self, mock_activity_map_ignored):
        # Let player_to_dict raise an error when processing player from primary attribute
        self.mock_player_to_dict.side_effect = Exception("Player serialization failed!")
        
        mock_team_obj = MockTeam(1)
        mock_player_obj = MockPlayer(101) # This player will cause the error
        activity = MockActivity(msg_type=2, team=mock_team_obj, player=mock_player_obj) # ADD

        result = activity_to_dict(activity)

        self.assertTrue(result["error"].startswith("Error serializing activity: Player serialization failed!"))
        self.assertEqual(result["type"], "ERROR_PROCESSING_2") # Uses original msg_type
        self.assertEqual(result["date"], activity.date) # Date should still be there

    def test_scenario_g_error_handling_action_player_processing_exception(self, mock_activity_map_ignored):
        # Let player_to_dict raise an error when processing player from an action
        mock_action_player = MockPlayer(202, "Player Two")
        action1 = MockAction(action_type="PLAYERADDED", player=mock_action_player)
        activity_with_action_player = MockActivity(msg_type=None, actions=[action1])

        # Configure side_effect to fail only for this specific player or generally
        self.mock_player_to_dict.side_effect = Exception("Action Player failed!")

        result = activity_to_dict(activity_with_action_player)
        
        self.assertTrue(result["error"].startswith("Error serializing activity: Action Player failed!"))
        self.assertEqual(result["type"], "ERROR_PROCESSING_NO_TYPE") # original_msg_type was None
        self.assertEqual(result["date"], activity_with_action_player.date)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
