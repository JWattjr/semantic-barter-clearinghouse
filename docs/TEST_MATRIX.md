# Test matrix

Run `python -m pytest` from the repository root. Compatibility responses are mocked in direct mode, so tests do not establish live network consensus.

| Invariant or behavior | Test |
|---|---|
| A two-party cycle with one incompatible reverse edge fails; a compatible three-party cycle clears after exact consent and conserves each asset | `test_three_party_cycle_clears_only_after_exact_consent_and_conserves_each_asset` |
| Validator rejects disagreement, reordered edges, and unknown fields | `test_validator_rejects_disagreement_and_unknown_edge_fields` |
| Malformed leader edge output fails closed without locking offers or changing their escrow | `test_malformed_model_edges_fail_closed_without_locking_offers` |
| Only a participant can cancel a cycle; cancellation releases offer locks, and offers return their reserves once | `test_participant_can_cancel_cycle_and_release_offer_reservations` |
| Unconsented cycle expiry unlocks offers; expired offers return escrow to their owners | `test_expired_pending_cycle_unlocks_and_expired_offers_return_to_owners` |
| Cycle length, offer uniqueness, and consent deadline bounds are enforced | `test_cycle_input_bounds_are_enforced_before_model_call` (three parameter cases) |

The current run passed 8 direct-mode tests. GenVM lint passed 3 checks, contract validation reported 13 methods (4 views, 9 writes), and schema extraction succeeded. No network deployment was attempted.
