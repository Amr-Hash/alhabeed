import os
import subprocess
import sys


def main():
    if not os.environ.get("DATABASE_URL"):
        message = (
            "ERROR: DATABASE_URL not set — migrations were skipped. "
            "On Vercel, link Neon Postgres so DATABASE_URL is available at build time, "
            "not only at runtime."
        )
        if os.environ.get("VERCEL"):
            print(message, file=sys.stderr)
            sys.exit(1)
        print(f"WARNING: {message}")
        return

    subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])
    subprocess.check_call(
        [sys.executable, "manage.py", "purge_demo_data"],
        stderr=subprocess.STDOUT,
    )
    subprocess.check_call(
        [sys.executable, "manage.py", "sync_standing_rule_sets"],
        stderr=subprocess.STDOUT,
    )
    subprocess.check_call(
        [sys.executable, "manage.py", "sync_wc2026_kickoffs"],
        stderr=subprocess.STDOUT,
    )
    subprocess.check_call(
        [sys.executable, "manage.py", "merge_group_stages"],
        stderr=subprocess.STDOUT,
    )


if __name__ == "__main__":
    main()
