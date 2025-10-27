"""Manages all platform.sh-specific aspects of the deployment process."""

import django_simple_deploy

from dsd_upsun.platform_deployer import PlatformDeployer
from .plugin_config import PluginConfig


@django_simple_deploy.hookimpl
def dsd_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    plugin_config = PluginConfig()
    return plugin_config


@django_simple_deploy.hookimpl
def dsd_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
