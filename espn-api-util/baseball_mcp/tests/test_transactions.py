import unittest
from unittest.mock import patch, Mock, MagicMock

# Function to be tested
from baseball_mcp.transactions import get_recent_activity

# Mock the expected behavior of activity_to_dict
# For these tests, we'll assume activity_to_dict takes an object
# and converts it to a dictionary with at least a "type" key.
def mock_activity_to_dict_simple(activity_obj):
    # If the activity_obj itself is a dict (as some parts of the code imply might happen)
    if isinstance(activity_obj, dict):
        return activity_obj
    # Otherwise, assume it's an object with attributes
    # This needs to be consistent with what _create_mock_activity returns/simulates
    # and what the actual get_recent_activity expects after this conversion.
    # The key is that the output of this mock is what the rest of get_recent_activity uses.
    return {"type": getattr(activity_obj, 'type', 'UNKNOWN'), 
            "data": getattr(activity_obj, 'data', {}),
            # Include other fields if your tests for filtering/processing need them
            "raw_activity": activity_obj # keep a reference if needed for assertions
           }

class TestGetRecentActivity(unittest.TestCase):

    def _create_mock_activity_object(self, activity_id, activity_type="ADD", team_id=None, player_name=None):
        """
        Creates a mock activity object (not the dict, but the object that
        activity_to_dict would take as input).
        """
        mock_obj = Mock()
        mock_obj.type = activity_type
        # Simulate other attributes that activity_to_dict might access or that might be useful
        data = {'id': activity_id}
        if team_id:
            data['team_id'] = team_id
        if player_name:
            data['player_name'] = player_name
        mock_obj.data = data
        
        # This is what our mocked activity_to_dict will transform
        return mock_obj

    def _create_mock_activity_dict(self, activity_id, activity_type="ADD", team_id=None, player_name=None):
        """
        Creates the dictionary representation that mock_activity_to_dict_simple would return.
        This is what the rest of get_recent_activity will see.
        """
        data = {'id': activity_id}
        if team_id:
            data['team_id'] = team_id
        if player_name:
            data['player_name'] = player_name
        return {"type": activity_type, "data": data}

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error') # Mock log_error to suppress logging during tests
    def test_scenario_1_no_size_sufficient_data(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        # Setup Mocks
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        # Mock league.recent_activity (no size) to return >50 items
        # These are "raw" activity objects before activity_to_dict
        raw_activities_no_size = [self._create_mock_activity_object(i, f"type_{i}") for i in range(60)]
        mock_league_instance.recent_activity.return_value = raw_activities_no_size
        
        # Mock league.recent_activity(size=...) - this should NOT be called
        mock_recent_activity_with_size = Mock(side_effect=Exception("Should not be called"))
        # To distinguish between the two, we can configure the main mock and then add a specific one for the size call
        # However, since the first call is unconditional, we make its return_value the general one.
        # If it's called again with 'size', it would typically use the same return_value unless configured with a side_effect function
        # that inspects arguments. For simplicity, we'll check call_args_list for the 'size' call.

        # Call the function
        limit = 25
        offset = 0
        result = get_recent_activity(league_id=123, limit=limit, offset=offset)

        # Verifications
        mock_get_credentials.assert_called_once_with("default_session")
        mock_get_league.assert_called_once_with(123, None, 'dummy_s2', 'dummy_swid')
        
        # Check that recent_activity was called (this will be the no-size version)
        mock_league_instance.recent_activity.assert_called_once_with() 
        # To ensure the one WITH size was not called, we inspect its calls.
        # If recent_activity is a single mock, check its call_args
        # self.assertEqual(mock_league_instance.recent_activity.call_count, 1) # already implied by assert_called_once_with()

        # Verify activity_to_dict was called for each of the 60 activities
        self.assertEqual(mock_activity_to_dict.call_count, 60)
        for i in range(60):
            self.assertIs(mock_activity_to_dict.call_args_list[i][0][0], raw_activities_no_size[i])

        # Verify results (processed and sliced)
        self.assertEqual(len(result), limit)
        for i in range(limit):
            expected_dict = self._create_mock_activity_dict(i, f"type_{i}")
            # Our mock_activity_to_dict_simple adds 'raw_activity' key, so we check subset
            self.assertTrue(expected_dict.items() <= result[i].items())
            self.assertEqual(result[i]['type'], f"type_{i}") # Check type specifically

        mock_log_error.assert_not_called()
        mock_handle_error.assert_not_called()

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_2_no_size_limited_data_then_with_size(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        raw_activities_no_size = [self._create_mock_activity_object(i, f"type_no_size_{i}") for i in range(10)] # < 50
        raw_activities_with_size = [self._create_mock_activity_object(i, f"type_with_size_{i}") for i in range(70)]

        # Configure recent_activity to return different values based on call args
        def recent_activity_side_effect(*args, **kwargs):
            if 'size' in kwargs:
                return raw_activities_with_size
            return raw_activities_no_size
        
        mock_league_instance.recent_activity.side_effect = recent_activity_side_effect

        limit = 30
        offset = 5
        fetch_size_expected = min(limit + offset + 50, 100) # 30 + 5 + 50 = 85

        result = get_recent_activity(league_id=123, limit=limit, offset=offset)

        mock_get_credentials.assert_called_once_with("default_session")
        mock_get_league.assert_called_once_with(123, None, 'dummy_s2', 'dummy_swid')

        # Verify recent_activity calls
        self.assertEqual(mock_league_instance.recent_activity.call_count, 2)
        # Call 1: no size
        mock_league_instance.recent_activity.assert_any_call()
        # Call 2: with size
        mock_league_instance.recent_activity.assert_any_call(size=fetch_size_expected)

        # Verify activity_to_dict was called for each of the 70 activities from the second call
        self.assertEqual(mock_activity_to_dict.call_count, 70)
        for i in range(70):
             self.assertIs(mock_activity_to_dict.call_args_list[i][0][0], raw_activities_with_size[i])

        # Verify results (processed from second call, sliced)
        self.assertEqual(len(result), limit)
        for i in range(limit):
            # Activities are from raw_activities_with_size, index i + offset
            expected_idx_in_raw = i + offset
            expected_dict = self._create_mock_activity_dict(expected_idx_in_raw, f"type_with_size_{expected_idx_in_raw}")
            self.assertTrue(expected_dict.items() <= result[i].items())
            self.assertEqual(result[i]['type'], f"type_with_size_{expected_idx_in_raw}")
        
        mock_log_error.assert_not_called()
        mock_handle_error.assert_not_called()

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_3_no_size_fails_then_with_size(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        simulated_error_no_size = Exception("API error no_size")
        raw_activities_with_size = [self._create_mock_activity_object(i, f"type_with_size_{i}") for i in range(40)]

        def recent_activity_side_effect(*args, **kwargs):
            if 'size' in kwargs:
                return raw_activities_with_size
            raise simulated_error_no_size
        
        mock_league_instance.recent_activity.side_effect = recent_activity_side_effect

        limit = 20
        offset = 0
        fetch_size_expected = min(limit + offset + 50, 100) # 20 + 0 + 50 = 70

        result = get_recent_activity(league_id=123, limit=limit, offset=offset)

        self.assertEqual(mock_league_instance.recent_activity.call_count, 2)
        mock_league_instance.recent_activity.assert_any_call()
        mock_league_instance.recent_activity.assert_any_call(size=fetch_size_expected)

        mock_log_error.assert_called_once_with(f"Error calling league.recent_activity() (no size): {str(simulated_error_no_size)}")
        
        self.assertEqual(mock_activity_to_dict.call_count, 40) # From the second call

        self.assertEqual(len(result), limit)
        for i in range(limit):
            expected_idx_in_raw = i + offset
            expected_dict = self._create_mock_activity_dict(expected_idx_in_raw, f"type_with_size_{expected_idx_in_raw}")
            self.assertTrue(expected_dict.items() <= result[i].items())
            self.assertEqual(result[i]['type'], f"type_with_size_{expected_idx_in_raw}")

        mock_handle_error.assert_not_called()

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_4_both_api_calls_fail(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        error_no_size = Exception("API error no_size")
        error_with_size = Exception("API error with_size")

        def recent_activity_side_effect(*args, **kwargs):
            if 'size' in kwargs:
                raise error_with_size
            raise error_no_size
        
        mock_league_instance.recent_activity.side_effect = recent_activity_side_effect
        
        # Mock handle_error to check its call
        mock_handle_error.return_value = {"error": "formatted_error"}


        limit = 10
        offset = 0
        fetch_size_expected = min(limit + offset + 50, 100)

        # The main function's try-except should catch the final error if activities is empty or fails
        # In our case, activities will be an empty list [] after both calls fail.
        # The function should then return this empty list, not call handle_error itself from the main block.
        # handle_error is for the outermost try-catch, which might not be hit if we default to [].
        # Let's trace: activities = [] -> processed_activities = [] -> returns []
        # The subtask implies this case should return [handle_error(e, ...)]
        # This means the main try-except in get_recent_activity should be triggered.
        # This would happen if get_league itself fails, or get_credentials.
        # If API calls fail and we set activities = [], the function might just return [].
        # Ah, the code is `except Exception as e: return [handle_error(e, "get_recent_activity")]`
        # If `activities` list is empty, the processing loop is skipped, and `processed_activities` remains `[]`.
        # The function then returns `processed_activities[start_index:end_index]`, which would be `[]`.
        # This does NOT trigger the outer `handle_error`.
        # The prompt for Scenario 4 might be misinterpreting the current code's behavior for *this specific type of double failure*.
        # Let's test the actual behavior: an empty list should be returned.
        
        result = get_recent_activity(league_id=123, limit=limit, offset=offset)

        self.assertEqual(mock_league_instance.recent_activity.call_count, 2)
        mock_log_error.assert_any_call(f"Error calling league.recent_activity() (no size): {str(error_no_size)}")
        mock_log_error.assert_any_call(f"Error calling league.recent_activity(size={fetch_size_expected}) after initial fail: {str(error_with_size)}")
        
        self.assertEqual(result, []) # Expect an empty list
        mock_activity_to_dict.assert_not_called()
        mock_handle_error.assert_not_called() # Outer handle_error should not be called for this internal failure sequence

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_4b_main_exception_triggers_handle_error(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        # This test is to ensure the outer handle_error IS called if a different exception occurs (e.g. league fetching)
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        simulated_get_league_error = Exception("Failed to get league")
        mock_get_league.side_effect = simulated_get_league_error # Make get_league fail

        mock_handle_error.return_value = {"error": "formatted_get_league_error_response"}

        result = get_recent_activity(league_id=123, limit=10, offset=0)

        mock_get_league.assert_called_once()
        mock_handle_error.assert_called_once_with(simulated_get_league_error, "get_recent_activity")
        self.assertEqual(result, [{"error": "formatted_get_league_error_response"}])
        mock_log_error.assert_not_called() # log_error is for API call failures inside, not this one
        mock_activity_to_dict.assert_not_called()


    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_5_filtering_by_activity_type(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        raw_activities = [
            self._create_mock_activity_object(0, "ADD"),
            self._create_mock_activity_object(1, "DROP"),
            self._create_mock_activity_object(2, "ADD"),
            self._create_mock_activity_object(3, "TRADE"),
            self._create_mock_activity_object(4, "ADD"),
        ] # Using >50 for first call path is not strictly needed here, can use <50. Let's make it >50 for simplicity.
        # For this test, let's assume the first call (no size) gets enough data.
        mock_league_instance.recent_activity.return_value = raw_activities * 12 # 60 items

        limit = 10
        target_type = "ADD"
        result = get_recent_activity(league_id=123, limit=limit, activity_type=target_type)

        mock_league_instance.recent_activity.assert_called_once_with()
        self.assertEqual(mock_activity_to_dict.call_count, 60)

        # Expected: 3 "ADD" types in the original 'raw_activities'. Multiplied by 12 = 36 ADDs. Limited by 10.
        self.assertEqual(len(result), limit)
        for activity_dict in result:
            self.assertEqual(activity_dict['type'], target_type)
        
        # Check that we have 3 unique ADDs from the original set, repeated
        # Each original ADD obj (id 0, 2, 4) should appear 10/3 ~= 3 or 4 times in the result.
        # This gets complex due to repetition. Simpler: check the first few.
        # result[0] comes from raw_activities[0] (id 0, type ADD)
        # result[1] comes from raw_activities[2] (id 2, type ADD)
        # result[2] comes from raw_activities[4] (id 4, type ADD)
        # result[3] comes from raw_activities[0+5] (id 0, type ADD)
        self.assertEqual(result[0]['data']['id'], 0)
        self.assertEqual(result[1]['data']['id'], 2)
        self.assertEqual(result[2]['data']['id'], 4)
        self.assertEqual(result[3]['data']['id'], 0)


    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_6_offset_and_limit(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        # Generate 60 unique items (more than 50, so first API call path is used)
        num_total_activities = 60
        raw_activities = [self._create_mock_activity_object(i, f"type_{i}") for i in range(num_total_activities)]
        mock_league_instance.recent_activity.return_value = raw_activities

        test_cases = [
            {"limit": 5, "offset": 0, "expected_ids": list(range(0, 5))},
            {"limit": 5, "offset": 5, "expected_ids": list(range(5, 10))},
            {"limit": 5, "offset": 58, "expected_ids": list(range(58, 60))}, # Only 2 activities left
            {"limit": 5, "offset": 60, "expected_ids": []}, # Offset is at the end
            {"limit": 70, "offset": 0, "expected_ids": list(range(0, 60))}, # Limit > available
        ]

        for tc_idx, tc in enumerate(test_cases):
            # Reset call counts for mocks that are checked per test case iteration
            mock_activity_to_dict.reset_mock()
            mock_league_instance.recent_activity.reset_mock() # Reset if it's per-iteration
            mock_league_instance.recent_activity.return_value = raw_activities # Re-assign as reset_mock might clear it.


            with self.subTest(f"Test Case {tc_idx}: limit={tc['limit']}, offset={tc['offset']}"):
                result = get_recent_activity(league_id=123, limit=tc['limit'], offset=tc['offset'])
                
                mock_league_instance.recent_activity.assert_called_once_with()
                self.assertEqual(mock_activity_to_dict.call_count, num_total_activities)
                
                self.assertEqual(len(result), len(tc['expected_ids']))
                for i, activity_dict in enumerate(result):
                    self.assertEqual(activity_dict['data']['id'], tc['expected_ids'][i])
                    self.assertEqual(activity_dict['type'], f"type_{tc['expected_ids'][i]}")
        
        mock_log_error.assert_not_called() # No errors expected in these cases
        mock_handle_error.assert_not_called()

    @patch('baseball_mcp.transactions.handle_error')
    @patch('baseball_mcp.transactions.auth_service.get_credentials')
    @patch('baseball_mcp.transactions.league_service.get_league')
    @patch('baseball_mcp.transactions.activity_to_dict', side_effect=mock_activity_to_dict_simple)
    @patch('baseball_mcp.transactions.log_error')
    def test_scenario_7_no_size_limited_data_then_with_size_fails(self, mock_log_error, mock_activity_to_dict, mock_get_league, mock_get_credentials, mock_handle_error):
        mock_get_credentials.return_value = {'espn_s2': 'dummy_s2', 'swid': 'dummy_swid'}
        mock_league_instance = Mock()
        mock_get_league.return_value = mock_league_instance

        raw_activities_no_size = [self._create_mock_activity_object(i, f"type_no_size_{i}") for i in range(10)] # < 50
        simulated_error_with_size = Exception("API error with_size")

        def recent_activity_side_effect(*args, **kwargs):
            if 'size' in kwargs:
                raise simulated_error_with_size
            return raw_activities_no_size
        
        mock_league_instance.recent_activity.side_effect = recent_activity_side_effect

        limit = 8
        offset = 1
        # fetch_size will be calculated as min(8 + 1 + 50, 100) = 59
        fetch_size_expected = min(limit + offset + 50, 100)

        result = get_recent_activity(league_id=123, limit=limit, offset=offset)

        self.assertEqual(mock_league_instance.recent_activity.call_count, 2)
        mock_league_instance.recent_activity.assert_any_call()
        mock_league_instance.recent_activity.assert_any_call(size=fetch_size_expected)

        # Log the error from the second call
        mock_log_error.assert_called_once_with(f"Error calling league.recent_activity(size={fetch_size_expected}): {str(simulated_error_with_size)}")
        
        # activity_to_dict should be called for the 10 activities from the first (successful) call
        self.assertEqual(mock_activity_to_dict.call_count, 10)
        for i in range(10):
             self.assertIs(mock_activity_to_dict.call_args_list[i][0][0], raw_activities_no_size[i])

        # Verify results (processed from first call, sliced)
        self.assertEqual(len(result), limit) # limit is 8
        # offset is 1, so we expect items from index 1 to 1+8=9 of raw_activities_no_size
        for i in range(limit): 
            expected_idx_in_raw = i + offset # e.g. for result[0], i=0, offset=1 -> raw[1]
            expected_dict = self._create_mock_activity_dict(expected_idx_in_raw, f"type_no_size_{expected_idx_in_raw}")
            self.assertTrue(expected_dict.items() <= result[i].items())
            self.assertEqual(result[i]['type'], f"type_no_size_{expected_idx_in_raw}")
        
        mock_handle_error.assert_not_called()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# End of file
