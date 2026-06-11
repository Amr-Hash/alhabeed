import os
import re
from urllib.parse import urlparse, urlunparse

import psycopg2
from django.core.management.base import BaseCommand, CommandError


def replace_db_name(database_url: str, new_name: str) -> str:
    parsed = urlparse(database_url)
    return urlunparse(parsed._replace(path=f"/{new_name}"))


def admin_db_candidates(database_url: str) -> list[str]:
    current = urlparse(database_url).path.lstrip("/") or "postgres"
    return [name for name in ("neondb", "postgres", current) if name]


class Command(BaseCommand):
    help = "Rename the Postgres database referenced by DATABASE_URL (Neon/Vercel)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--from",
            dest="from_name",
            default="worldcup",
            help="Current database name (default: worldcup)",
        )
        parser.add_argument(
            "--to",
            dest="to_name",
            default="alhabeed",
            help="New database name (default: alhabeed)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned actions without renaming",
        )

    def handle(self, *args, **options):
        from_name = options["from_name"]
        to_name = options["to_name"]
        dry_run = options["dry_run"]

        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise CommandError("DATABASE_URL is not set.")

        parsed = urlparse(database_url)
        current_name = parsed.path.lstrip("/")
        if current_name != from_name:
            self.stdout.write(
                self.style.WARNING(
                    f"DATABASE_URL points to '{current_name}', not '{from_name}'. "
                    "Proceeding with the name from --from."
                )
            )

        if from_name == to_name:
            raise CommandError("Source and target database names are the same.")

        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", to_name):
            raise CommandError(f"Invalid target database name: {to_name}")

        if dry_run:
            self.stdout.write(f"Would rename '{from_name}' -> '{to_name}'")
            self.stdout.write(f"New DATABASE_URL path: /{to_name}")
            return

        last_error = None
        for admin_db in admin_db_candidates(database_url):
            admin_url = replace_db_name(database_url, admin_db)
            try:
                conn = psycopg2.connect(admin_url)
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s",
                        (from_name,),
                    )
                    if not cursor.fetchone():
                        conn.close()
                        raise CommandError(
                            f"Database '{from_name}' was not found on the server."
                        )

                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s",
                        (to_name,),
                    )
                    if cursor.fetchone():
                        raise CommandError(
                            f"Database '{to_name}' already exists. Choose another name."
                        )

                    cursor.execute(
                        """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s AND pid <> pg_backend_pid()
                        """,
                        (from_name,),
                    )
                    cursor.execute(
                        f'ALTER DATABASE "{from_name}" RENAME TO "{to_name}"'
                    )
                conn.close()
                new_url = replace_db_name(database_url, to_name)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Renamed database '{from_name}' to '{to_name}'."
                    )
                )
                self.stdout.write("")
                self.stdout.write(
                    "Update DATABASE_URL in Vercel to the new connection string:"
                )
                self.stdout.write(new_url)
                return
            except CommandError:
                raise
            except Exception as exc:
                last_error = exc
                continue

        raise CommandError(
            f"Could not rename database. Last error: {last_error}"
        )
