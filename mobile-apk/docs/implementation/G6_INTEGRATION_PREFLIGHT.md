# G6 Integration Preflight

This checkpoint is deliberately build-free.

Required PASS gates before the first app-v2 APK candidate:
- safety invariants;
- manifest/permission allowlist;
- modular Kotlin compile;
- targeted unit tests;
- Android lint for app-v2;
- alpha1 regression compile.

The APK remains blocked until all five CI jobs plus gate-summary are green.

Safety invariants:
- LIVE_TRADING_ENABLED = NO
- live trading authority is not granted by the mobile client
- RESEARCH_ONLY = YES
- no automatic device/host trust
- no cleartext gateway traffic
- no broad storage, camera, microphone, location, or package-install permission

Rollback checkpoints:
- cp1 files/editor green
- cp2 git green
- cp3 gateway green
- cp4 self-test green
