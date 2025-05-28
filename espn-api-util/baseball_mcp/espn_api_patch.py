"""
ESPN API Authentication Patch
Monkey patch to fix the authentication bug in espn_api library without modifying the installed package
"""

import sys
from espn_api.requests.espn_requests import EspnFantasyRequests, ESPNAccessDenied

def patched_checkRequestStatus(self, status: int, extend: str = "", params: dict = None, headers: dict = None) -> dict:
    """Patched version of checkRequestStatus that properly handles None cookies"""
    if status == 401:
        # If the current LEAGUE_ENDPOINT was using the /leagueHistory/ endpoint, switch to "/seasons/" endpoint
        if "/leagueHistory/" in self.LEAGUE_ENDPOINT:
            base_endpoint = self.LEAGUE_ENDPOINT.split("/leagueHistory/")[0]
            self.LEAGUE_ENDPOINT = f"{base_endpoint}/seasons/{self.year}/segments/0/leagues/{self.league_id}"
        else:
            # If the current LEAGUE_ENDPOINT was using /seasons, switch to the "/leagueHistory/" endpoint
            base_endpoint = self.LEAGUE_ENDPOINT.split(f"/seasons/")[0]
            self.LEAGUE_ENDPOINT = f"{base_endpoint}/leagueHistory/{self.league_id}?seasonId={self.year}"

        #try the alternate endpoint
        import requests
        r = requests.get(self.LEAGUE_ENDPOINT + extend, params=params, headers=headers, cookies=self.cookies)
        
        if r.status_code == 200:
            # Return the updated response if alternate works
            return r.json()
            
        # If all endpoints failed, raise the corresponding error
        # PATCH: Handle None cookies properly
        cookies_info = ""
        if self.cookies:
            cookies_info = f"espn_s2={self.cookies.get('espn_s2')} and swid={self.cookies.get('SWID')}"
        else:
            cookies_info = "no authentication provided"
        raise ESPNAccessDenied(f"League {self.league_id} cannot be accessed with {cookies_info}")

    elif status == 404:
        from espn_api.requests.espn_requests import ESPNInvalidLeague
        raise ESPNInvalidLeague(f"League {self.league_id} does not exist")

    elif status != 200:
        from espn_api.requests.espn_requests import ESPNUnknownError
        raise ESPNUnknownError(f"ESPN returned an HTTP {status}")
    
    # If no issues with the status code, return None
    return None

def apply_espn_api_patch():
    """Apply the authentication patch to the ESPN API"""
    try:
        # Monkey patch the checkRequestStatus method
        EspnFantasyRequests.checkRequestStatus = patched_checkRequestStatus
        print("✓ ESPN API authentication patch applied successfully", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Failed to apply ESPN API patch: {str(e)}", file=sys.stderr)

def log_error(message: str):
    """Add stderr logging for Claude Desktop to see"""
    print(message, file=sys.stderr) 