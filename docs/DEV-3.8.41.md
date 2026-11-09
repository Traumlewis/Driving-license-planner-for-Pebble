# Development 3.8.41

This is a test build, not a public release. Continue version numbering with 3.8.42, 3.8.43, etc. The public GitHub release remains 3.8.4 until the owner requests another release.

- Practical counters without a fixed minimum have no extra-minute hold actions. Select them normally to edit whole units. Theory manual-unit actions remain available with checkbox totals protected.
- Watch appointment planning uses whole practice units when the selected class/profile has no minimum for that lesson type, including general driving. Mandatory practical lessons retain five-minute increments. Practice units represent 45 minutes; theory units represent 90 minutes.
- Existing persisted appointments, manual counters and accumulated minutes are retained. Choosing a whole-unit lesson type or explicitly editing its quantity saves whole units for that draft.
- Source pushes no longer publish GitHub Releases. The publication workflow is manual only. Development PBWs include (DEV) in their filenames and stay outside the tracked release directory.

Validation: all six native targets built; model/storage/translation/wakeup checks and hold tests passed in all five projects. tests/unit_entry_policy_test.py exercises actual helper/routing/application code for all 16 classes and 44 profiles, including other-class appointment editing. Native UI checks are reproducible with tools/regression_3841.py; generated development captures are ignored by Git.

Example test build:

```
python3 tools/build_all.py --output '/tmp/Fahrschul-Planer-v3.8.41(DEV).pbw'
python3 tests/release_validation.py '/tmp/Fahrschul-Planer-v3.8.41(DEV).pbw'
```
