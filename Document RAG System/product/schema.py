"""
Internal Product Schema Definitions
"""

from typing import Dict, Any, List

# Standard UNSPSC Segment / Family Mappings
UNSPSC_MAP = {
    "circuit breaker": {"code": "39121601", "title": "Circuit breakers"},
    "contactor": {"code": "39121529", "title": "Motor contactors"},
    "relay": {"code": "39122331", "title": "Electromechanical relays"},
    "sensor": {"code": "41111926", "title": "Proximity sensors"},
    "plc": {"code": "32151705", "title": "Programmable logic controllers PLC"},
    "drive": {"code": "39122001", "title": "Variable frequency drives VFD"},
    "valve": {"code": "40141619", "title": "Solenoid valves"}
}
