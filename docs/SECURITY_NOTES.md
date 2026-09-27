# Security notes

## Judgment and consent

- Offer owner, asset ID, quantity, description, request text, expiry, and offer key are stored before compatibility assessment. The model cannot change them.
- The compatibility snapshot binds the contract address, deterministic cycle ID, ordered offer keys, and complete offer records. The contract computes the digest outside the model response.
- The leader and validators independently assess the same directed edges. The contract requires the exact same edge order and Boolean vector, rejects unknown fields, and refuses the cycle if any edge is false.
- Semantic approval is not enough to transfer anything. Every distinct offer owner must consent; any participant may cancel the pending or ready cycle before execution.
- A cycle uses unique offers and distinct participants, with a maximum of three. An offer is locked by at most one pending cycle and consumed once.

## Accounting and timing

- `deposit_demo_asset` mints synthetic units to the caller. These balances are not backed by tokens, assets, or escrowed funds. The contract demonstrates only internal conservation and atomic state changes.
- Creation moves units from available to reserved. Execution moves each reserved offer to the next receiver. Cancellation and expiry release reserved units to the owner. The aggregate invariant is maintained per asset ID.
- Cycle consent has a frozen deadline no later than the expiry of any included offer. Pending cycles may expire and unlock offers. An offer can be canceled only by its owner after it is unlocked; anyone may expire it after its expiry.
- Time comes from `gl.message.datetime`. Direct tests can warp this time but do not prove behavior on a live chain.

## Known limitations

- The model reasons over participant-written descriptions only. No external source, proof of asset authenticity, legal right to transfer, physical handoff, or quality check is provided.
- Prompts treat participant text as untrusted and reject injected output fields, but model errors remain possible. A failed or malformed consensus response reverts the proposal.
- Amounts are fixed integers and all transfers stay inside one contract ledger. No native-value, token, cross-chain, or off-chain transfer is performed.
- Direct tests mock model responses. Live consensus, deployment runner availability, and finalized execution are unverified.
