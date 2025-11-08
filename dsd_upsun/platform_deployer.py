"""Manages all Upsun-specific aspects of the deployment process."""

import sys, os, subprocess, time
from pathlib import Path

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)

from . import deploy_messages as upsun_msgs
from . import utils as upsun_utils


class PlatformDeployer:
    """Perform the initial deployment to Upsun.

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and call
    `upsun push`.
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to Upsun...")

        self._validate_platform()

        self._prep_automate_all()
        self._modify_settings()
        self._add_requirements()
        self._add_platform_app_yaml()
        self._add_platform_dir()
        self._add_services_yaml()
        self._settings_env_var()

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to
        Upsun.

        Make sure CLI is installed, and user is authenticated. Make sure necessary
        resources have been created and identified, and that we have the user's
        permission to use those resources.

        Returns:
            None

        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        if dsd_config.unit_testing:
            # Unit tests don't use the CLI. Use the deployed project name that was
            # passed to the simple_deploy CLI.
            self.deployed_project_name = dsd_config.deployed_project_name
            plugin_utils.log_info(
                f"Deployed project name: {self.deployed_project_name}"
            )
            return

        self._check_upsun_settings()
        self._validate_cli()

        self.deployed_project_name = self._get_upsun_project_name()
        plugin_utils.log_info(f"Deployed project name: {self.deployed_project_name}")

        self.org_name = self._get_org_name()
        plugin_utils.log_info(f"\nOrg name: {self.org_name}")

    def _prep_automate_all(self):
        """Intial work for automating entire process.

        Returns:
            None: If creation of new project was successful.

        Raises:
            DSDCommandError: If create command fails.

        Note: create command outputs project id to stdout if known, all other
          output goes to stderr.
        """
        if not dsd_config.automate_all:
            return

        plugin_utils.write_output("  Running `upsun create`...")
        plugin_utils.write_output(
            "    (Please be patient, this can take a few minutes."
        )
        cmd = f"upsun create --title { self.deployed_project_name } --org {self.org_name} --region {dsd_config.region} --yes"

        try:
            # Note: if user can't create a project the returncode will be 6, not 1.
            #   This may affect whether a CompletedProcess is returned, or an Exception
            # is raised.
            # Also, create command outputs project id to stdout if known, all other
            # output goes to stderr.
            plugin_utils.run_slow_command(cmd)
        except subprocess.CalledProcessError as e:
            error_msg = upsun_msgs.unknown_create_error(e)
            raise DSDCommandError(error_msg)

        # Fix bug ignoring .upsun/local on Windows.
        if (msg_fixed := upsun_utils.fix_git_exclude_bug()):
            plugin_utils.write_output(msg_fixed)

    def _modify_settings(self):
        """Add upsun-specific settings.

        This settings block is currently the same for all users. The ALLOWED_HOSTS
        setting should be customized.
        """
        template_path = self.templates_path / "settings.py"
        plugin_utils.modify_settings_file(template_path)

    def _add_platform_app_yaml(self):
        """Add a .platform.app.yaml file."""

        # Build contents from template.
        if dsd_config.pkg_manager == "poetry":
            template_path = "poetry.platform.app.yaml"
        elif dsd_config.pkg_manager == "pipenv":
            template_path = "pipenv.platform.app.yaml"
        else:
            template_path = "platform.app.yaml"
        template_path = self.templates_path / template_path

        context = {
            "project_name": dsd_config.local_project_name,
            "deployed_project_name": self.deployed_project_name,
        }

        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / ".platform.app.yaml"
        plugin_utils.add_file(path, contents)

    def _add_requirements(self):
        """Add requirements for Upsun."""
        requirements = ["platformshconfig", "gunicorn", "psycopg2"]
        plugin_utils.add_packages(requirements)

    def _add_platform_dir(self):
        """Add a .platform directory, if it doesn't already exist."""
        self.platform_dir_path = dsd_config.project_root / ".platform"
        plugin_utils.add_dir(self.platform_dir_path)

    def _add_services_yaml(self):
        """Add the .platform/services.yaml file."""

        template_path = self.templates_path / "services.yaml"
        contents = plugin_utils.get_template_string(template_path, context=None)

        path = self.platform_dir_path / "services.yaml"
        plugin_utils.add_file(path, contents)

    def _settings_env_var(self):
        """Set the DJANGO_SETTINGS_MODULE env var, if needed."""
        # This is primarily for Wagtail projects, as signified by a settings/production.py file.
        if dsd_config.settings_path.parts[-2:] == ("settings", "production.py"):
            plugin_utils.write_output(
                "  Setting DJANGO_SETTINGS_MODULE environment variable..."
            )

            # Need form mysite.settings.production
            dotted_settings_path = ".".join(
                dsd_config.settings_path.parts[-3:]
            ).removesuffix(".py")

            cmd = f"upsun variable:create --level environment --environment main --name DJANGO_SETTINGS_MODULE --value {dotted_settings_path} --no-interaction --visible-build true --prefix env"
            output = plugin_utils.run_quick_command(cmd)
            plugin_utils.write_output(output)

    def _conclude_automate_all(self):
        """Finish automating the push to Upsun.

        - Commit all changes.
        - Call `upsun push`.
        - Open project.
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Pushing to Upsun...")

        # Pause to make sure project that was just created can be used.
        plugin_utils.write_output(
            "    Pausing 10s to make sure project is ready to use..."
        )
        time.sleep(10)

        # Use run_slow_command(), to stream output as it runs.
        cmd = "upsun push --yes"
        plugin_utils.run_slow_command(cmd)

        # Open project.
        plugin_utils.write_output("  Opening deployed app in a new browser tab...")
        cmd = "upsun url --yes"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)

        # Get url of deployed project.
        #   This can be done with an re, but there's one line of output with
        #   a url, so finding that line is simpler.
        # DEV: Move this to a utility, and write a test against standard Upsun
        # output.
        self.deployed_url = ""
        for line in output.stdout.decode().split("\n"):
            if "https" in line:
                self.deployed_url = line.strip()

    def _show_success_message(self):
        """After a successful run, show a message about what to do next."""

        # DEV:
        # - Mention that this script should not need to be run again unless creating
        #   a new deployment.
        # - Describe ongoing approach of commit, push, migrate. Lots to consider
        #   when doing this on production app with users, make sure you learn.

        if dsd_config.automate_all:
            msg = upsun_msgs.success_msg_automate_all(self.deployed_url)
            plugin_utils.write_output(msg)
        else:
            msg = upsun_msgs.success_msg(dsd_config.log_output)
            plugin_utils.write_output(msg)

    # --- Helper methods for methods called from deploy.py ---

    def _check_upsun_settings(self):
        """Check to see if an Upsun settings block already exists."""
        start_line = "# Upsun settings."
        plugin_utils.check_settings(
            "Upsun",
            start_line,
            upsun_msgs.upsun_settings_found,
            upsun_msgs.cant_overwrite_settings,
        )

    def _validate_cli(self):
        """Make sure the Upsun CLI is installed, and user is authenticated."""
        cmd = "upsun --version"

        # This generates a FileNotFoundError on macOS and Linux if the CLI is not installed.
        try:
            output_obj = plugin_utils.run_quick_command(cmd)
        except FileNotFoundError:
            raise DSDCommandError(upsun_msgs.cli_not_installed)

        plugin_utils.log_info(output_obj)
        if sys.platform == "win32":
            stderr = output_obj.stderr.decode(encoding="utf-8")
            if "'upsun' is not recognized as an internal or external command" in stderr:
                raise DSDCommandError(upsun_msgs.cli_not_installed)

        # Check that the user is authenticated.
        cmd = "upsun auth:info --no-interaction"
        output_obj = plugin_utils.run_quick_command(cmd)

        if "Authentication is required." in output_obj.stderr.decode():
            raise DSDCommandError(upsun_msgs.cli_logged_out)

        # There's an apparent bug in the Upsun CLI that causes the .upsun/local/
        # dir to not be ignored on Windows like it is on other OSes. We can fix
        # that ourselves until Upsun updates their CLI.
        # In the configuration-only approach, the user has already run
        # `upsun create`, so we'll try that fix here. This avoids the user running
        # `manage.py deploy` with an unclean Git status.
        if (msg_fixed := upsun_utils.fix_git_exclude_bug()):
            plugin_utils.write_output(msg_fixed)


    def _get_upsun_project_name(self):
        """Get the deployed project name.

        If using automate_all, we'll set this. Otherwise, we're looking for the name
        that was given in the `upsun create` command.
        - Try to get this from `project:info`.
        - If can't get project name:
          - Exit with warning, and inform user of --deployed-project-name
            flag to override this error.

        Retuns:
            str: The deployed project name.
        Raises:
            DSDCommandError: If deployed project name can't be found.
        """
        # If we're creating the project, we'll just use the startproject name.
        if dsd_config.automate_all:
            return dsd_config.local_project_name

        # Use the provided name if --deployed-project-name specified.
        if dsd_config.deployed_project_name:
            return dsd_config.deployed_project_name

        # Use --yes flag to avoid interactive prompt hanging in background
        #   if the user is not currently logged in to the CLI.
        cmd = "upsun project:info --yes --format csv"
        output_obj = plugin_utils.run_quick_command(cmd)
        output_str = output_obj.stdout.decode()

        # Log cmd, but don't log the output of `project:info`. It contains identifying
        # information about the user and project, including client_ssh_key.
        plugin_utils.log_info(cmd)

        # If there's no stdout, the user is probably logged out, hasn't called
        #   create, or doesn't have the CLI installed.
        # Also, I've seen both ProjectNotFoundException and RootNotFoundException
        #   raised when no project has been created.
        if not output_str:
            output_str = output_obj.stderr.decode()
            if "LoginRequiredException" in output_str:
                raise DSDCommandError(upsun_msgs.login_required)
            elif "ProjectNotFoundException" in output_str:
                raise DSDCommandError(upsun_msgs.no_project_name)
            elif "RootNotFoundException" in output_str:
                raise DSDCommandError(upsun_msgs.no_project_name)
            else:
                error_msg = upsun_msgs.unknown_error
                error_msg += upsun_msgs.cli_not_installed
                raise DSDCommandError(error_msg)

        # Pull deployed project name from output.
        lines = output_str.splitlines()
        title_line = [line for line in lines if "title," in line][0]
        # Assume first project is one to use.
        project_name = title_line.split(",")[1].strip()
        project_name = upsun_utils.get_project_name(output_str)

        # Project names can only have lowercase alphanumeric characters.
        # See: https://github.com/ehmatthes/django-simple-deploy/issues/323
        if " " in project_name:
            project_name = project_name.replace(" ", "_").lower()
        if project_name:
            return project_name

        # Couldn't find a project name. Warn user, and tell them about override flag.
        raise DSDCommandError(upsun_msgs.no_project_name)

    def _get_org_name(self):
        """Get the organization name associated with the user's Upsun account.

        This is needed for creating a project using automate_all.
        Confirm that it's okay to use this org.

        Returns:
            str: org name
            None: if not using automate-all
        Raises:
            DSDCommandError:
            - if org name found, but not confirmed.
            - if org name not found
        """
        if not dsd_config.automate_all:
            return

        cmd = "upsun organization:list --yes --format csv"
        output_obj = plugin_utils.run_quick_command(cmd)
        output_str = output_obj.stdout.decode()
        plugin_utils.log_info(output_str)

        org_names = upsun_utils.get_org_names(output_str)
        if not org_names:
            raise DSDCommandError(upsun_msgs.org_not_found)

        if len(org_names) == 1:
            # Get permission to use this org.
            org_name = org_names[0]
            if self._confirm_use_org(org_name):
                return org_name

        # Show all orgs, ask user to make selection.
        prompt = "\n*** Found multiple orgs on Upsun. ***"
        for index, name in enumerate(org_names):
            prompt += f"\n  {index}: {name}"
        prompt += "\nWhich org would you like to use? "

        valid_choices = [i for i in range(len(org_names))]

        # Confirm selection, because we do *not* want to deploy using the wrong org.
        confirmed = False
        while not confirmed:
            selection = plugin_utils.get_numbered_choice(
                prompt, valid_choices, upsun_msgs.no_org_available
            )
            selected_org = org_names[selection]

            confirm_prompt = f"You have selected {selected_org}."
            confirm_prompt += " Is that correct?"
            confirmed = plugin_utils.get_confirmation(confirm_prompt)

            return selected_org

    def _confirm_use_org(self, org_name):
        """Confirm that it's okay to use the org that was found.

        Returns:
            True: if confirmed
            DSDCommandError: if not confirmed
        """

        dsd_config.stdout.write(upsun_msgs.confirm_use_org(org_name))
        confirmed = plugin_utils.get_confirmation(skip_logging=True)

        if confirmed:
            dsd_config.stdout.write("  Okay, continuing with deployment.")
            return True
        else:
            # Exit, with a message that configuration is still an option.
            msg = upsun_msgs.cancel_upsun
            msg += upsun_msgs.may_configure
            raise DSDCommandError(msg)
