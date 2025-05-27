#!/usr/bin/env python3
"""
Debug script to deeply inspect ESPN Fantasy Baseball activity objects
"""

import sys
import os
import json

# Add the baseball_mcp directory to Python path and change to it
baseball_mcp_dir = os.path.join(os.path.dirname(__file__), 'baseball_mcp')
sys.path.insert(0, baseball_mcp_dir)
os.chdir(baseball_mcp_dir)

from transactions import get_recent_activity
from auth import auth_service

def inspect_raw_activity():
    """Inspect raw activity objects to understand their structure"""
    
    print("ESPN Fantasy Baseball Activity Inspector")
    print("=" * 50)
    
    # Test league ID from your debug report
    league_id = 30201
    test_year = 2025
    
    # Set up authentication
    test_espn_s2 = "AEAsSsgCoPXC%2FWJT3dVK0SwkXYwd3Qr02cWh8uSNT53BuzjiGaSkGmeMTBb2ewG32YhGXRmWRODi6yS3FB3cg29FKk0gv57WcUVvYBWg7B0ChDTnk9ATqag0DzEVlgdEBm9wKv%2F93gMSU5T1V6aJ5PAb7%2BnIblVIO666PSDVGoanJCePQ7llHbK9XiOA3pyClzNU3vt%2F6N7ofcq5TbLyhUsYELsJnMnl7PAsy0GmD682Fbyyw6M6JpGuaaTQ6tiJotChn5NX2%2Fmi7UduIW%2BxQIF3ZxqE4AKl9eWZkaew9OjmdaUkwdfja1MGfNmi1jzAVNI%3D"
    test_swid = "{BFA3386F-9501-4F4A-88C7-C56D6BB86C11}"
    
    auth_result = auth_service.store_credentials("test_session", test_espn_s2, test_swid)
    print(f"✓ Authentication configured: {auth_result.get('status', 'unknown')}")
    
    # Get raw league object for inspection
    from utils import league_service
    credentials = auth_service.get_credentials("test_session")
    league = league_service.get_league(league_id, test_year, 
                                     credentials.get('espn_s2'), 
                                     credentials.get('swid'))
    
    print(f"\nInspecting raw activities from league {league_id}...")
    
    try:
        # Get raw activities directly
        raw_activities = league.recent_activity(size=5)  # Just get a few for detailed inspection
        
        print(f"Retrieved {len(raw_activities)} raw activities\n")
        
        for i, activity in enumerate(raw_activities[:3]):
            print(f"=== Raw Activity {i+1} ===")
            print(f"Activity Object Type: {type(activity)}")
            
            # List all attributes
            print("Available attributes:")
            attrs = [attr for attr in dir(activity) if not attr.startswith('_')]
            for attr in sorted(attrs):
                try:
                    value = getattr(activity, attr)
                    if not callable(value):
                        print(f"  {attr}: {value} (type: {type(value)})")
                except Exception as e:
                    print(f"  {attr}: <error accessing: {e}>")
            
            # Special focus on key attributes
            print(f"\nKey Properties:")
            for key_attr in ['msg_type', 'date', 'team', 'actions', 'player', 'players_in', 'players_out']:
                if hasattr(activity, key_attr):
                    value = getattr(activity, key_attr)
                    print(f"  {key_attr}: {value}")
                    
                    # If it's actions, dive deeper
                    if key_attr == 'actions' and value:
                        print(f"    Actions count: {len(value)}")
                        for j, action in enumerate(value[:2]):  # Just first 2 actions
                            print(f"    Action {j}:")
                            if hasattr(action, '__dict__'):
                                for k, v in action.__dict__.items():
                                    print(f"      {k}: {v}")
                            else:
                                print(f"      Raw action: {action}")
                else:
                    print(f"  {key_attr}: <not found>")
            
            print("\n" + "-" * 40 + "\n")
        
    except Exception as e:
        print(f"❌ Error inspecting activities: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("Inspection completed.")

if __name__ == "__main__":
    inspect_raw_activity() 