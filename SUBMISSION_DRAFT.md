# Submission draft — not deployed or submitted

**Status: local draft only. This contract is undeployed and has not been submitted to the GenLayer Portal.**

## Project

`SemanticBarterClearinghouse` forms directed exchange cycles from participant offers and requests. A GenLayer judgment checks whether the next participant's described offer can satisfy each request. The contract binds that compatibility vector to a deterministic cycle snapshot, requires exact consent from each distinct participant, and atomically transfers the pre-reserved demo asset quantities within its own ledger.

## Distinguishing mechanism

A three-party cycle can clear when neither two-party orientation satisfies both parties. Offer reservations move only after every participant consents; each asset amount remains conserved across available and reserved balances. No model output chooses quantities or recipients.

## Local verification recorded

- GenVM lint: passed 3 checks.
- Contract validation: 13 methods (4 views, 9 writes).
- ABI schema extraction: succeeded to `contracts/abi.json`.
- Direct-mode tests: 8 passed, including three-party clearing, two-party failure, validator disagreement, malformed leader output, expiry, cancellation, and per-asset conservation.
- Live deployment, physical delivery, real asset custody, and Portal review: not performed.

## Limitations

The faucet creates synthetic demo units. Participant descriptions do not prove title, quality, or delivery. Direct tests mock compatibility judgments and do not prove live network consensus. No cross-chain settlement is implemented.
