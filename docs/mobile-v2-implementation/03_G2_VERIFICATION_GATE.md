# G2 Verification Gate

A dedicated implementation workflow now validates the implementation branch without building an APK.

Checks:
1. static safety invariants;
2. private-key pattern rejection in new implementation modules;
3. core:model/core:result/testing:fakes compilation;
4. targeted core unit tests;
5. existing alpha1 app compile regression;
6. explicit output that APK build remains blocked until G7.

This workflow intentionally contains no `assembleDebug` task.

LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
RESEARCH_ONLY = YES
