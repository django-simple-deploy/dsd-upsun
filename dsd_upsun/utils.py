"""Utilities specific to Upsun deployments."""

from pathlib import Path
import sys


def get_project_name(output_str):
    """Get the project name from the output of `upsun project:info`.

    Command is run with `--format csv` flag.

    Returns:
        str: project name
    """
    lines = output_str.splitlines()
    title_line = [line for line in lines if "title," in line][0]
    # Assume first project is one to use.
    project_name = title_line.split(",")[1].strip()

    return project_name


def get_org_names(output_str):
    """Get org names from output of `upsun organization:list --yes --format csv`.

    Sample input:
        Name,Label,Owner email
        <org-name>,<org-label>,<org-owner@example.com>
        <org-name-2>,<org-label-2>,<org-owner-2@example.com>

    Returns:
        list: [str]
        None: If user has no organizations.
    """
    if "No organizations found." in output_str:
        return None

    lines = output_str.split("\n")[1:]
    return [line.split(",")[0] for line in lines if line]


def fix_git_exclude_bug():
    """Fix the bug where .upsun/local/ is not ignored on Windows.

    See: https://github.com/platformsh/cli/issues/286

    Returns:
        Str: confirmation message if bug was fixed
        None: if no changes were made
    """
    if sys.platform != "win32":
        return

    path_upsun_local = Path(".upsun") / "local"
    if not path_upsun_local.exists():
        return
    
    path_exclude = Path(".git") / "info" / "exclude"
    if not path_exclude.exists():
        return
    
    exclude_text = path_exclude.read_text()
    exclude_text_fixed = exclude_text.replace(r"/.upsun\local", r"/.upsun/local")

    if exclude_text_fixed != exclude_text:
        path_exclude.write_text(exclude_text_fixed)
        return "Fixed /.upsun/local entry in .git/info/exclude file."
