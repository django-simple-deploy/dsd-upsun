"""Manages all Upsun-specific aspects of the deployment process."""

import django_simple_deploy

from dsd_upsun.platform_deployer import PlatformDeployer
from .plugin_config import PluginConfig
from . import utils as upsun_utils


@django_simple_deploy.hookimpl
def dsd_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    plugin_config = PluginConfig()
    return plugin_config


@django_simple_deploy.hookimpl
def dsd_pre_inspect():
    """Do some work before core inspects the user's project."""
    # There's an apparent bug in the Upsun CLI that causes the .upsun/local/
    # dir to not be ignored on Windows like it is on other OSes. We can fix
    # that ourselves until Upsun updates their CLI.
    # In the configuration-only approach, the user has already run
    # `upsun create`, so we'll try that fix here. This avoids the user running
    # `manage.py deploy` with an unclean Git status.
    if (msg_fixed := upsun_utils.fix_git_exclude_bug()):
        return msg_fixed


@django_simple_deploy.hookimpl
def dsd_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
