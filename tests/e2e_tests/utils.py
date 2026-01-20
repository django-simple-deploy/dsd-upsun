"""Helper functions specific to Upsun."""

import re, time

import pytest

from tests.e2e_tests.utils.it_helper_functions import make_sp_call


def check_logged_in():
    """Check that user is currently logged in to Upsun through CLI."""
    print("\nVerifying logged in to Upsun CLI...")
    auth_info_output = make_sp_call(
        "upsun auth:info --no-interaction", capture_output=True
    )

    # Check that we can find a user ID in the output.
    # Checking for this line (sample data)
    # | id                    | 87vr8ehb-rg9e-shg8-9hse-r8oghseo89hr |
    re_user_id = r"\n\| id\s*\| ([\w\-]*)\s*\|"
    stdout = auth_info_output.stdout.decode()
    m = re.search(re_user_id, stdout)
    if not m:
        exit_msg = "Please run `upsun login` and then run e2e tests."
        pytest.exit(exit_msg)


def create_project():
    """Create a project on Upsun."""
    print("\n\nCreating a project on Upsun...")
    org_output = make_sp_call("upsun org:info", capture_output=True).stdout.decode()
    org_id = re.search(r"([A-Z0-9]{26})", org_output).group(1)
    print(f"  Found Upsun organization id: {org_id}")
    create_cmd = f"upsun create --title my_blog_project --org {org_id} --region us-3.platform.sh --yes"

    make_sp_call(create_cmd)


def push_project():
    """Push a non-automated deployment."""
    # Pause before making push, otherwise project resources may not be available.
    time.sleep(30)

    print("Pushing to Upsun...")
    make_sp_call("upsun push --yes")

    project_url = (
        make_sp_call("upsun url --yes", capture_output=True).stdout.decode().strip()
    )
    print(f" Project URL: {project_url}")

    project_info = make_sp_call(
        "upsun project:info", capture_output=True
    ).stdout.decode()
    project_id = re.search(r"\| id             \| ([a-z0-9]{13})", project_info).group(
        1
    )
    print(f"  Found project id: {project_id}")

    return project_url, project_id


def get_project_url_id():
    """Get project URL and id of a deployed project."""
    project_info = make_sp_call(
        "upsun project:info", capture_output=True
    ).stdout.decode()
    project_id = re.search(r"\| id             \| ([a-z0-9]{13})", project_info).group(
        1
    )
    print(f"  Found project id: {project_id}")

    project_url = (
        make_sp_call("upsun url --yes", capture_output=True).stdout.decode().strip()
    )
    print(f" Project URL: {project_url}")

    return project_url, project_id


def destroy_project(request):
    """Destroy the deployed project, and all remote resources."""
    print("\nCleaning up:")

    project_id = request.config.cache.get("project_id", None)
    if not project_id:
        print("  No project id found; can't destroy any remote resources.")

    print("  Destroying Upsun project...")
    make_sp_call(f"upsun project:delete --project {project_id} --yes")
