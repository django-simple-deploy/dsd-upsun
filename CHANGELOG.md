Changelog: dsd-platformsh
===

0.9 - Simplified usage from core
---

### 0.9.1 (unreleased)

#### External changes

- Updated messaging to use deploy command instead of simple_deploy.

#### Internal changes

- Updated tests for Python 3.12 and Postgres 16.
- Uses config instead of returning individual attributes to core.
- Simplified packaging; all setup.cfg config moved to pyproject.toml.

### 0.9.0

#### External changes

- Specifies Python 3.12 instead of 3.10, and Postgres 16 instead of 12.

#### Internal changes

- Simplified packaging config.
- Updated requirements.
- Updated test for authenticated CLI session for e2e tests.
- Returns platform name to core.
- Added required MANIFEST.in file back.

0.8 - First use of external plugins with django-simple-deploy
---

### 0.8.2

#### External changes

- None

#### Internal changes

- Requires django-simple-deploy. This is more important for non-default plugins, but it means you can just install the plugin without having to also explicitly install django-simple-deploy.

### 0.8.1

#### External changes

- Bugfix: Includes templates dir in package.

#### Internal changes

- None

### 0.8.0

#### External changes

- Initial release.

#### Internal changes

- Initial release.