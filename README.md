dsd-upsun
===

dsd-upsun is a plugin for deploying Django projects to [Upsun](https://upsun.com) (formerly Platform.sh), using django-simple-deploy.

This is an officially supported plugin, so the full documentation for dsd-upsun is included in the [django-simple-deploy](https://django-simple-deploy.readthedocs.io/en/latest/) docs. The Quick Start page for Upsun is [here](https://django-simple-deploy.readthedocs.io/en/latest/quick_starts/quick_start_upsun/).

Upsun documentation
---

The home page for the [Upsun docs](https://devcenter.upsun.com) is a good starting point, but it can be hard to know where to look for Django-specific information. Here are some helpful links to be aware of, whether you're deploying a project to Upsun or helping maintain this plugin.

Upsun has two approaches to deployment: Fixed and Flex. With a Fixed plan, you specify the size of the resources you want to use for your project. When your project grows, you'll need to upgrade to a higher Fixed plan. With a Flex plan, you can select from a wider variety of specific resource sizes. When your project grows you can scale individual resources yourself, or you can let Upsun scale resources for you.

Currently, dsd-upsun only supports Fixed deployments. The roadmap includes a plan to add support for both Fixed and Flex deployments.

### Fixed docs


The main documentation page for Fixed deployments is [here](https://fixed.docs.upsun.com). Other relevant pages include:

- [Fixed philosophy](https://fixed.docs.upsun.com/learn/overview/philosophy.html)
- [Python on Upsun Fixed](https://fixed.docs.upsun.com/languages/python.html)
- [Django on Upsun Fixed](https://fixed.docs.upsun.com/guides/django.html)
- [Deploy Django on Upsun Fixed](https://fixed.docs.upsun.com/guides/django/deploy.html)
- [Django configuration](https://fixed.docs.upsun.com/guides/django/deploy/customize.html#django-configuration)
- [Configure Django for Upsun Fixed](https://fixed.docs.upsun.com/guides/django/deploy/configure.html)

The main page for Flex deployments is [here](https://docs.upsun.com). Other relevant pages include:

- [Operational maturity for Django](https://upsun.com/django/)
- [Deploy Django on Upsun Flex](https://docs.upsun.com/get-started/stacks/django.html)
