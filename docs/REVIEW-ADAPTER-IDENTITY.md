# Adversarial Verification — FakeAdapter path identity

**Date:** 2026-09-02  
**Level:** 1. Closes the FakeAdapter half of T-19. Not Experiment 04.

Submit lock + `INVALID_REQUEST` already on `master` (`2d7caca`). This slice does not reopen them.

| Check | Result |
|---|---|
| Frozen tests | unmodified |
| Suite twice | **147 passed / 0 failed** |
| Alias writes | one repo key `src/a.py`, `files_changed == 1` |
| Alias delete | pops that key |
| P7 DENY does not mutate repo | still green |
| Real/other adapters | still T-19 residual |

```text
NEXT STEP: STOP
```
