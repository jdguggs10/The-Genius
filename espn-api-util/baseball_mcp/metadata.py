"""
ESPN Fantasy Baseball metadata and constant mappings
Contains position maps, stat maps, and activity type mappings from espn_api.baseball.constant
"""

from typing import Dict

# Position mapping from ESPN slot IDs to human-readable position names
# Based on espn_api.baseball.constant.POSITION_MAP
POSITION_MAP: Dict[int, str] = {
    0: "C",      # Catcher
    1: "1B",     # First Base
    2: "2B",     # Second Base
    3: "3B",     # Third Base
    4: "SS",     # Shortstop
    5: "OF",     # Outfield
    6: "OF",     # Outfield
    7: "OF",     # Outfield
    8: "DH",     # Designated Hitter
    9: "UTIL",   # Utility
    10: "SP",    # Starting Pitcher
    11: "RP",    # Relief Pitcher
    12: "SP",    # Starting Pitcher
    13: "RP",    # Relief Pitcher
    14: "SP",    # Starting Pitcher
    15: "RP",    # Relief Pitcher
    16: "BN",    # Bench
    17: "DL",    # Disabled List/Injured List
    18: "NA",    # Not Available
    19: "BN",    # Bench
    20: "BN",    # Bench
    21: "IL",    # Injured List
}

# Stats mapping from ESPN stat IDs to human-readable stat abbreviations  
# Based on espn_api.baseball.constant.STATS_MAP
STATS_MAP: Dict[int, str] = {
    # Hitting Stats
    0: "AB",      # At Bats
    1: "H",       # Hits
    2: "AVG",     # Batting Average
    3: "R",       # Runs
    4: "HR",      # Home Runs
    5: "RBI",     # Runs Batted In
    6: "SB",      # Stolen Bases
    7: "2B",      # Doubles
    8: "3B",      # Triples
    9: "BB",      # Walks
    10: "HBP",    # Hit By Pitch
    11: "TB",     # Total Bases
    12: "OBP",    # On Base Percentage
    13: "SLG",    # Slugging Percentage
    14: "OPS",    # On Base Plus Slugging
    15: "GO",     # Ground Outs
    16: "AO",     # Air Outs (Fly Outs)
    17: "GO_AO",  # Ground Out to Air Out Ratio
    18: "HBP",    # Hit By Pitch
    19: "SF",     # Sacrifice Flies
    20: "GIDP",   # Grounded Into Double Play
    21: "CS",     # Caught Stealing
    
    # Pitching Stats  
    40: "IP",     # Innings Pitched
    41: "GS",     # Games Started
    42: "W",      # Wins
    43: "L",      # Losses
    44: "SV",     # Saves
    45: "HLD",    # Holds
    46: "K",      # Strikeouts
    47: "ERA",    # Earned Run Average
    48: "WHIP",   # Walks + Hits Per Innings Pitched
    49: "K_9",    # Strikeouts Per 9 Innings
    50: "BB_9",   # Walks Per 9 Innings
    51: "H_9",    # Hits Per 9 Innings
    52: "HR_9",   # Home Runs Per 9 Innings
    53: "BB",     # Walks
    54: "H",      # Hits Allowed
    55: "ER",     # Earned Runs
    56: "HR",     # Home Runs Allowed
    57: "QS",     # Quality Starts
    58: "BS",     # Blown Saves
    59: "CG",     # Complete Games
    60: "SHO",    # Shutouts
    61: "SV_HLD", # Saves + Holds
    62: "IR",     # Inherited Runners
    63: "IRS",    # Inherited Runners Scored
    
    # Misc Stats
    80: "G",      # Games
    81: "GS",     # Games Started
    82: "ELIG",   # Eligibility (for position players)
    83: "FPTS",   # Fantasy Points
    
    # Additional Stats
    90: "FPCT",   # Fielding Percentage
    91: "PO",     # Put Outs
    92: "A",      # Assists  
    93: "E",      # Errors
    94: "DP",     # Double Plays
    95: "SB_ATT", # Stolen Base Attempts
    96: "CS_ATT", # Caught Stealing Attempts
    97: "PB",     # Passed Balls (catchers)
    98: "SB_PCT", # Stolen Base Percentage
    99: "XBH",    # Extra Base Hits
}

# Activity type mapping from friendly names to ESPN message type codes
# Based on espn_api.baseball.constant.ACTIVITY_MAP
ACTIVITY_MAP: Dict[str, list] = {
    "ADD": [180, 181, 182, 183, 184],           # Free agent pickup, waiver claim, etc.
    "DROP": [171, 172, 173, 174, 175],         # Drop player
    "TRADE_ACCEPTED": [244],                    # Trade completed
    "TRADE_PENDING": [239],                     # Trade proposed/pending
    "TRADE_DECLINED": [243],                    # Trade declined
    "WAIVER_MOVED": [180],                      # Waiver claim processed 
    "WAIVER_BUDGET_USED": [183],               # FAAB waiver bid
    "ROSTER_MOVE": [178],                       # General roster move
    "LINEUP_SET": [178],                        # Lineup changes
    "DRAFT_PICK": [224],                        # Draft selection
    "KEEPER_SELECT": [226],                     # Keeper selection
    "LEAGUE_EDIT": [254],                       # League settings change
    "TEAM_EDIT": [253],                         # Team settings change
}

# Reverse mapping for activity types (ESPN code to friendly name)
ACTIVITY_REVERSE_MAP: Dict[int, str] = {}
for friendly_name, codes in ACTIVITY_MAP.items():
    for code in codes:
        ACTIVITY_REVERSE_MAP[code] = friendly_name

def get_positions() -> Dict[int, str]:
    """
    Get mapping of ESPN position slot IDs to position names
    
    Returns:
        Dictionary mapping ESPN slot IDs to human-readable position names
    """
    return POSITION_MAP.copy()

def get_stat_map() -> Dict[int, str]:
    """
    Get mapping of ESPN stat IDs to stat abbreviations
    
    Returns:
        Dictionary mapping ESPN stat IDs to human-readable stat names
    """
    return STATS_MAP.copy()

def get_activity_types() -> Dict[str, list]:
    """
    Get mapping of friendly activity names to ESPN message type codes
    
    Returns:
        Dictionary mapping friendly names to ESPN activity codes
    """
    return ACTIVITY_MAP.copy()

def get_position_name(slot_id: int) -> str:
    """
    Get position name for a given slot ID
    
    Args:
        slot_id: ESPN position slot ID
        
    Returns:
        Human-readable position name
    """
    return POSITION_MAP.get(slot_id, f"Position_{slot_id}")

def get_stat_name(stat_id: int) -> str:
    """
    Get stat name for a given stat ID
    
    Args:
        stat_id: ESPN stat ID
        
    Returns:
        Human-readable stat abbreviation
    """
    return STATS_MAP.get(stat_id, f"stat_{stat_id}")

def get_activity_name(msg_type: int) -> str:
    """
    Get friendly activity name for a given ESPN message type
    
    Args:
        msg_type: ESPN message type code
        
    Returns:
        Friendly activity name
    """
    return ACTIVITY_REVERSE_MAP.get(msg_type, f"UNKNOWN_{msg_type}")