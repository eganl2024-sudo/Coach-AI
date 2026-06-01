"""
Create the permanent demo account in Supabase.

Usage:
    python scripts/create_demo_account.py

Requires SUPABASE_URL and SUPABASE_KEY to be set in the environment
(or in a .env file loaded before running). On Streamlit Cloud these
are set automatically from the app secrets.

Safe to run multiple times — skips creation if the account already exists.
"""
import sys
import os
from pathlib import Path

# Reconfigure stdout to UTF-8 on Windows so checkmarks/emoji render safely.
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src/ to path so we can import project modules without installing them.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "PlayerAI2026"
STREAMLIT_CLOUD_URL = "https://mdpapp.streamlit.app"   # update if URL changes


def main():
    # ── 1. Validate environment before touching anything ──────────────────
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")

    if not supabase_url or not supabase_key:
        print(
            "\n[ERROR] Missing Supabase credentials.\n"
            "  SUPABASE_URL and SUPABASE_KEY must be set before running this script.\n\n"
            "  Local usage (PowerShell):\n"
            "    $env:SUPABASE_URL='https://your-project.supabase.co'\n"
            "    $env:SUPABASE_KEY='your-anon-or-service-role-key'\n"
            "    python scripts/create_demo_account.py\n\n"
            "  On Streamlit Cloud:\n"
            "    These are set automatically from your app secrets.\n"
            "    Trigger this script via the Streamlit Cloud shell or\n"
            "    by adding a one-off run to your deployment workflow.\n"
        )
        sys.exit(1)

    # ── 2. Import project modules (requires credentials to be set first) ──
    try:
        import db
        import auth
        import config
    except ImportError as e:
        print(f"\n[ERROR] Failed to import project modules: {e}")
        print("  Make sure you are running this from the project root.")
        sys.exit(1)

    # ── 3. Check if account already exists ────────────────────────────────
    try:
        existing = db.get_user(DEMO_USERNAME)
    except RuntimeError as e:
        print(f"\n[ERROR] Supabase connection error: {e}")
        print(
            "  Ensure SUPABASE_URL and SUPABASE_KEY are correct and "
            "the 'users' table exists."
        )
        sys.exit(1)

    if existing:
        print(f"[INFO] Demo account already exists — skipping creation.")
        print(f"   Re-seeding sandbox from data/demo/ ...")
        auth.bootstrap_user_sandbox(DEMO_USERNAME)
        sandbox_dir = config.PRODUCTION_DATA_DIR / "users" / DEMO_USERNAME
        print(f"✓  Sandbox refreshed at: {sandbox_dir}")
        print(f"\nReady to share: log in at {STREAMLIT_CLOUD_URL}")
        print(f"  Username: {DEMO_USERNAME}")
        print(f"  Password: {DEMO_PASSWORD}")
        return

    # ── 4. Create the account ─────────────────────────────────────────────
    print(f"Creating demo account: username={DEMO_USERNAME} ...")
    pwd_hash, salt = auth.hash_password(DEMO_PASSWORD)

    try:
        db.create_user(DEMO_USERNAME, pwd_hash, salt)
    except RuntimeError as e:
        print(f"\n❌  Failed to create user in Supabase: {e}")
        sys.exit(1)

    # ── 5. Populate sandbox ───────────────────────────────────────────────
    auth.bootstrap_user_sandbox(DEMO_USERNAME)
    sandbox_dir = config.PRODUCTION_DATA_DIR / "users" / DEMO_USERNAME

    # ── 6. Confirm ────────────────────────────────────────────────────────
    print(f"✓  Demo account created: username={DEMO_USERNAME}  password={DEMO_PASSWORD}")
    print(f"✓  Sandbox populated from data/demo/ → {sandbox_dir}")
    print(f"\nReady to share: log in at {STREAMLIT_CLOUD_URL}")
    print(f"  Username: {DEMO_USERNAME}")
    print(f"  Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
