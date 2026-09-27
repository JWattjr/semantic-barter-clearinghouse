# Complete demo sequence

The executable direct-mode demonstration is `test_three_party_cycle_clears_only_after_exact_consent_and_conserves_each_asset` in `tests/test_barter.py`. Run:

```powershell
python -m pytest tests/test_barter.py::test_three_party_cycle_clears_only_after_exact_consent_and_conserves_each_asset
```

1. Alice mints 10 `drill` demo units and offers one hand drill, requesting stainless fasteners.
2. Bob mints 10 `fasteners` units and offers two fastener units, requesting a sealed tin of paint.
3. Charlie mints 10 `paint` units and offers three paint units, requesting a hand drill.
4. The test first proposes `[Alice, Bob]`. Alice's request matches Bob's offer; Bob's reverse request does not match Alice's drill. The two-party proposal reverts and both offers remain active.
5. The test then proposes `[Alice, Bob, Charlie]`. The compatibility vector is true for all directed edges, and the deterministic snapshot digest is stored with cycle `C-000001`.
6. Alice, Bob, and Charlie each consent. Before the final consent, execution fails. After the final consent, execution sends Bob's two fastener units to Alice, Charlie's three paint units to Bob, and Alice's one drill unit to Charlie.
7. Each offer is marked consumed. All 10 units of each asset are available again across the three participants, none remain reserved, and each asset ledger reports conservation.

The compatibility vector is mocked in the local direct-mode test; it is not a live consensus receipt.
