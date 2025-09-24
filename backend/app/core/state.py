from typing import Any, Dict

USERS: Dict[str, Dict[str, Any]] = {}
DUCKS: Dict[str, Dict[str, Any]] = {}
TOKENS: Dict[str, str] = {}

PALETTE = {
    "public": [
        {"id": "violet",  "name": "Violet",   "hex": "#8A2BE2"},
        {"id": "blue",    "name": "Bleu",     "hex": "#3B82F6"},
    ],
    "locked": [
        {"id": "gold",    "name": "Or",       "hex": "#FFC93A"},
        {"id": "crimson", "name": "Cramoisi", "hex": "#EF4444"},
    ]
}