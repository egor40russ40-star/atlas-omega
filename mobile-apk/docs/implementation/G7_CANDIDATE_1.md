# G7 Candidate 1

Source candidate:
- versionCode: 23
- versionName: 0.2.0-alpha2-candidate1
- package: omega.atlas.mobile.v2.dev
- side-by-side installation with prior alpha1 remains possible

G7 build is isolated from the normal implementation pipeline.
It runs only on branch: atlas-mobile-v2-g7-build.

Candidate workflow must:
1. re-check safety invariants;
2. run app-v2 lint;
3. assemble app-v2 debug APK;
4. verify APK ZIP integrity;
5. verify Android signature with apksigner;
6. generate SHA-256;
7. upload an immutable workflow artifact.

The candidate is not a release until real-device certification.
