# src/users/management/commands/seed_demo_users.py
#
# Create (or refresh) the three local demo accounts — one per role — so every
# machine has an identical, disposable set of logins for development.
#
# - IDEMPOTENT: safe to re-run. Existing accounts have their names, role, flags
#               and password reset to the canonical values below.
# - NO SECRETS HERE: --password is required and has no default. This file is
#               committed to a public repository; the password itself lives only
#               in the git-ignored passwords.txt.
# - DEV ONLY:   refuses to run when settings.DEBUG is False unless --force is
#               given. Shared-password accounts must never exist in production.
#
# Examples:
#   python src/manage.py seed_demo_users --password='...' --dry-run
#   python src/manage.py seed_demo_users --password='...'
#
# Notes:
# - Creating the non-staff accounts may trigger the scaffold's invite email,
#   leaving files in tmp_emails/. Harmless: the password is set directly here,
#   so the invite links are never needed.
# - This does NOT replace BUILD_PLAN Step 17, which exists to prove the invite
#   flow itself works end to end with a fresh user.

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

DEMO_USERS = [
    {
        "email": "admin@persian.local",
        "first_name": "Demo",
        "last_name": "Admin",
        "role": User.Roles.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "teacher@persian.local",
        "first_name": "Demo",
        "last_name": "Teacher",
        "role": User.Roles.TEACHER,
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "student@persian.local",
        "first_name": "Demo",
        "last_name": "Student",
        "role": User.Roles.STUDENT,
        "is_staff": False,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = (
        "Create or refresh the three local demo accounts (admin, teacher, student).\n"
        "Development only. --password is required and is never stored in this file.\n\n"
        "Examples:\n"
        "  python src/manage.py seed_demo_users --password='...' --dry-run\n"
        "  python src/manage.py seed_demo_users --password='...'\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            dest="password",
            required=True,
            help="Password applied to all three demo accounts. Required; no default.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing to the database.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Permit running when DEBUG is False. Intended for tests, not production.",
        )

    def handle(self, *args, **options):
        password: str = options["password"]
        dry_run: bool = options["dry_run"]
        force: bool = options["force"]

        if not settings.DEBUG and not force:
            raise CommandError(
                "Refusing to run with DEBUG=False. These are shared-password demo "
                "accounts and must never exist in production. Use --force only if "
                "you are certain (for example, in a test settings module)."
            )

        self.stdout.write(self.style.NOTICE("== seed_demo_users starting =="))
        self.stdout.write(f"Options: password=***, dry_run={dry_run}, debug={settings.DEBUG}")

        created = 0
        updated = 0

        for spec in DEMO_USERS:
            email = spec["email"]
            label = f"{email} ({spec['role']})"

            user = User.objects.filter(email=email).first()

            if dry_run:
                verb = "would update" if user else "would create"
                self.stdout.write(self.style.SUCCESS(f"{verb}: {label}"))
                continue

            if user is None:
                user = User.objects.create_user(email=email, password=password)
                created += 1
                action = "created"
            else:
                user.set_password(password)
                updated += 1
                action = "updated"

            # Applied on both paths so a re-run repairs drifted flags or roles.
            user.first_name = spec["first_name"]
            user.last_name = spec["last_name"]
            user.role = spec["role"]
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            user.is_active = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f"{action}: {label}"))

        self.stdout.write(
            self.style.NOTICE(f"created={created} updated={updated} dry_run={dry_run}")
        )
        self.stdout.write(self.style.SUCCESS("Done."))
