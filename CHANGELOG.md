Changelog: dsd-upsun
===

### 1.2.1

#### External changes

- The dialog for selecting which organization shows the org name, ID, and whether it's a Flex or Fixed org. This makes it much easier to select the appropriate org for users who have multiple orgs. New Upsun accounts have a default Flex plan, so all new users trying to make a Fixed deployment will likely have at least two orgs.

#### Internal changes

- The util function `get_org_names()` is now `get_org_ids_names()`.

### 1.2.0

The version is jumping to 1.2.0, because the dsd-platformsh plugin that this is based on already had a 1.1.0 release.

#### External changes

- Clarifies copy on README.
- Shows correct error message when the Upsun CLI is not installed.
- Messages show `upsun` as the command to use, not `platform`.
- Simplifies error messages.

#### Internal changes

- Utility function to address bug in ignoring `.upsun/local/` dir on Windows.
- Uses `dsd_pre_inspect()` hook to address that bug for config-only runs. Calls that function during automate-all runs.

### 0.1.0

#### External changes

- This is a port of the dsd-platformsh plugin, which is being deprecated as Platform.sh has rebranded to Upsun.

#### Internal changes

- Most names are converted from Platform.sh to Upsun.
- Some names are still Platform.sh-based, where Upsun has continued to use that name.
