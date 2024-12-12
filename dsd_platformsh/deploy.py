"""Manages all platform.sh-specific aspects of the deployment process."""


import simple_deploy

from dsd_platformsh.platform_deployer import PlatformDeployer
from .plugin_config import PluginConfig


@simple_deploy.hookimpl
def simple_deploy_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    plugin_config = PluginConfig()
    return plugin_config


@simple_deploy.hookimpl
def simple_deploy_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
