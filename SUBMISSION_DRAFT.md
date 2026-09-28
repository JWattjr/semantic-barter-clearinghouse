# Submission draft

`SemanticBarterClearinghouse` assesses directed compatibility between participant-described offers and requests, then requires exact consent from every participant before atomically transferring the reserved quantities in its internal ledger.

**Live demonstration:** on StudioNet chain 61999, all three two-party cycles rolled back as incompatible, while the fully consented three-party cycle executed and replay of its consumed offers rolled back; the deployed source matches commit `ec60bc2d81ad11afe2d0f9754eb8ed505cc17ccb`.

**What it proves:** validator compatibility judgments can gate a consent-bound three-party exchange and the contract ledger prevents offer reuse.

**What it does not prove:** ownership, condition, or delivery of physical goods, or custody and settlement of real assets; demo units are synthetic.

The contract is deployed at `0x7825aa21426894b598c751C83813954CbfF9fCf0`. The [StudioNet release record](deployments/studionet-release-2026-09-28.json) contains transaction outcomes and the complete available public-view read-back. The 9-test direct suite mocks the compatibility judgment; integration tests were not run.
