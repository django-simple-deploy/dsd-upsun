Changelog: dsd-upsun
===

### 0.8.0

The version is jumping to 0.8.0, because dsd-platformsh was already at 1.0. We're pretty close to 1.0, and I want the version number to indicate that more clearly than a 0.2.0 release would.

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
