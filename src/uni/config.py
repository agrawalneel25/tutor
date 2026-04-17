from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUTH_DIR = REPO / "auth_state"
PANOPTO_STATE = AUTH_DIR / "panopto.json"
BLACKBOARD_STATE = AUTH_DIR / "blackboard.json"
SUBJECTS_DIR = REPO / "subjects"
PROMPTS_DIR = REPO / "prompts"

PANOPTO_HOST = "https://imperial.cloud.panopto.eu"
BLACKBOARD_HOST = "https://bb.imperial.ac.uk"

SUBJECTS = ["analysis", "calculus", "linear-algebra"]

AUTH_DIR.mkdir(exist_ok=True)
