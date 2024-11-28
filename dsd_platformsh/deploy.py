"""Manages all platform.sh-specific aspects of the deployment process."""


import simple_deploy
from dsd_platformsh.platform_deployer import PlatformDeployer
from . import deploy_messages as platform_msgs


@simple_deploy.hookimpl
def simple_deploy_automate_all_supported():
    """Specify whether --automate-all is supported on the specified platform."""
    return True


@simple_deploy.hookimpl
def simple_deploy_get_automate_all_msg():
    """Get platform-specific confirmation message for --automate-all flag."""
    return platform_msgs.confirm_automate_all

@simple_deploy.hookimpl
def simple_deploy_get_platform_name():
    """Return the name of the platform that's being deployed to.

    DEV: Consider returning a config object if there ends up being more info to share
    back to core.
    """
    return "platform_sh"


@simple_deploy.hookimpl
def simple_deploy_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
