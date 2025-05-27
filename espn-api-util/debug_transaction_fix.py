#!/usr/bin/env python3
"""
Debug script to test ESPN Fantasy Baseball transaction fixes
"""

import sys
import os

# Add the baseball_mcp directory to Python path and change to it
baseball_mcp_dir = os.path.join(os.path.dirname(__file__), 'baseball_mcp')
sys.path.insert(0, baseball_mcp_dir)
os.chdir(baseball_mcp_dir)

from transactions import get_recent_activity
from auth import auth_service

def test_transaction_fixes():
    """Test the transaction fixes with your league"""
    
    print("Testing ESPN Fantasy Baseball Transaction Fixes")
    print("=" * 50)
    
    # Test league ID from your debug report
    league_id = 30201
    # User confirmed: league name says '24 but actual year is 2025
    test_year = 2025
    
    # Set up authentication (you'll need to provide these)
    # These should be your actual ESPN_S2 and SWID cookies
    import os
    import sys
    
    # Check for environment variables first, then prompt
    espn_s2 = os.getenv('ESPN_S2', '').strip()
    swid = os.getenv('SWID', '').strip()
    
    # For testing, use hardcoded values if available
    if not espn_s2:
        test_espn_s2 = "AEAsSsgCoPXC%2FWJT3dVK0SwkXYwd3Qr02cWh8uSNT53BuzjiGaSkGmeMTBb2ewG32YhGXRmWRODi6yS3FB3cg29FKk0gv57WcUVvYBWg7B0ChDTnk9ATqag0DzEVlgdEBm9wKv%2F93gMSU5T1V6aJ5PAb7%2BnIblVIO666PSDVGoanJCePQ7llHbK9XiOA3pyClzNU3vt%2F6N7ofcq5TbLyhUsYELsJnMnl7PAsy0GmD682Fbyyw6M6JpGuaaTQ6tiJotChn5NX2%2Fmi7UduIW%2BxQIF3ZxqE4AKl9eWZkaew9OjmdaUkwdfja1MGfNmi1jzAVNI%3D"
        test_swid = "{BFA3386F-9501-4F4A-88C7-C56D6BB86C11}"
        if len(sys.argv) > 1 and sys.argv[1] == "--use-test-cookie":
            espn_s2 = test_espn_s2
            swid = test_swid
            print(f"✓ Using test ESPN_S2 cookie (length: {len(espn_s2)})")
            print(f"✓ Using test SWID cookie (length: {len(swid)})")
        else:
            try:
                espn_s2 = input("Enter your ESPN_S2 cookie (or press Enter to skip): ").strip()
            except EOFError:
                espn_s2 = ""
                print("⚠ No ESPN_S2 provided")
    else:
        print(f"✓ Using ESPN_S2 from environment (length: {len(espn_s2)})")
        
    if not swid and "--use-test-cookie" not in sys.argv:
        try:
            swid = input("Enter your SWID cookie (or press Enter to skip): ").strip()
        except EOFError:
            swid = ""
            print("⚠ No SWID provided")
    elif swid:
        print(f"✓ Using SWID from environment (length: {len(swid)})")
    
    if espn_s2:
        # Try with just ESPN_S2 first, SWID might not be required for some leagues
        auth_result = auth_service.store_credentials("test_session", espn_s2, swid if swid else "")
        print(f"✓ Authentication configured (ESPN_S2: Yes, SWID: {'Yes' if swid else 'No'})")
        print(f"  Auth result: {auth_result.get('status', 'unknown')}")
    else:
        print("⚠ No authentication provided - may only work for public leagues")
    
    print(f"\nTesting recent activity for league {league_id} (year {test_year})...")
    
    try:
        # Test basic recent activity with specific year
        activities = get_recent_activity(league_id, limit=10, year=test_year, session_id="test_session")
        
        print(f"\nResults: {len(activities)} activities returned")
        
        if activities:
            print("\nFirst few activities:")
            for i, activity in enumerate(activities[:3]):
                print(f"\nActivity {i+1}:")
                print(f"  Type: {activity.get('type', 'UNKNOWN')}")
                print(f"  Date: {activity.get('date', 'UNKNOWN')}")
                print(f"  Raw Timestamp: {activity.get('raw_timestamp', 'UNKNOWN')}")
                print(f"  Has Team: {activity.get('team') is not None}")
                print(f"  Has Error: {'error' in activity}")
                
                if 'error' in activity:
                    print(f"  Error: {activity['error']}")
                    
                if activity.get('team'):
                    team = activity['team']
                    print(f"  Team: {team.get('team_name', 'Unknown')} (ID: {team.get('team_id', 'Unknown')})")
        else:
            print("❌ No activities returned")
            
    except Exception as e:
        print(f"❌ Error testing transactions: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed. Check the stderr output for detailed debugging logs.")

if __name__ == "__main__":
    test_transaction_fixes() 