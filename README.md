# Semantic Barter Clearinghouse

`SemanticBarterClearinghouse` clears directed exchange cycles among participants with differently described offers and requests. Participants mint demo units into their own ledger, reserve exact quantities in offers, and provide descriptions of what they offer and what they seek. GenLayer assesses semantic compatibility between adjacent offers in a proposed cycle of two or three distinct participants. Deterministic code binds the assessed edges to an exact cycle snapshot, requires consent from every participant, and transfers all reserved demo units atomically within the contract ledger.

The model does not select quantities, asset IDs, participants, or balances. A transfer exchanges only the explicit demo asset ID and quantity registered in the corresponding offer.

## Toolchain

The source pins `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`; the installed linter validates the exact header. This contract is deployed on StudioNet chain 61999 at `0x7825aa21426894b598c751C83813954CbfF9fCf0` from source commit `ec60bc2d81ad11afe2d0f9754eb8ed505cc17ccb`; deployed source matches the Git blob. The live demonstration and public-view read-back are recorded in [the release record](deployments/studionet-release-2026-09-28.json). The installed v0.6 RC Python dependencies are pinned in `requirements.txt`.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
genvm-lint lint contracts/semantic_barter_clearinghouse.py
genvm-lint validate contracts/semantic_barter_clearinghouse.py
genvm-lint schema contracts/semantic_barter_clearinghouse.py --output contracts/abi.json
python -m pytest
```

Direct-mode tests mock the model call. They test contract transitions and the validator closure locally; they do not prove live network consensus.

## Lifecycle

1. A participant calls `deposit_demo_asset` to mint an explicitly synthetic demo asset ID into their own available balance.
2. The participant creates an offer with an asset ID, exact units, an offered-item description, a requested-item description, and an expiry. The contract moves those units from available balance to reserved offer escrow.
3. Anyone may propose an ordered cycle containing two or three active offers from distinct participants. For each receiver, GenLayer assesses whether the next offer's description can satisfy that receiver's request. Any incompatible directed edge rejects the proposal.
4. The contract stores the accepted compatibility vector, offer keys, consent deadline, and deterministic snapshot digest. Each participant must consent to that exact cycle. A participant may cancel the whole cycle before execution; an unconsented cycle expires after its deadline.
5. Once all parties consent, anyone may call `execute_cycle` before the cycle or offer expiry. The contract sends each offered asset to the next participant in the cycle in one state transition and consumes each offer once.
6. An unlocked owner can cancel an offer; anyone can expire an offer after its deadline. Both operations release its reserved units back to its owner.

## API and limits

Constructor has no parameters. Public writes are `deposit_demo_asset`, `create_offer`, `propose_cycle`, `consent_cycle`, `execute_cycle`, `cancel_cycle`, `expire_cycle`, `cancel_offer`, and `expire_offer`. Views are `get_balance`, `get_asset_accounting`, `get_offer`, and `get_cycle`. The extracted interface is [contracts/abi.json](contracts/abi.json).

The project caps the contract at 24 offers and 16 cycle records. Each cycle has two or three unique offer keys and at most three distinct participants. Offer descriptions are bounded. GenLayer treats participant descriptions as untrusted text. The prototype has no external evidence fetch because compatibility is judged from the participants' own descriptions; it cannot establish item quality, ownership, delivery, or real-world availability.

Demo units are minted by a faucet method and have no external backing. This is an internal atomic ledger demonstration, not physical barter, a token, cross-chain settlement, or delivery enforcement.

See [mechanism differentiation](docs/MECHANISM_DIFFERENTIATION.md), [test matrix](docs/TEST_MATRIX.md), [security notes](docs/SECURITY_NOTES.md), [complete demo sequence](examples/demo_sequence.md), and the [submission draft](SUBMISSION_DRAFT.md).

## Why GenLayer

Validators must interpret whether each free-text offered item can satisfy the next participant's frozen request; consent records willingness but does not prove compatibility, and deterministic code cannot compare these descriptions.
