# Distinctiveness audit

Scope: contract source review against the other nine portfolio contracts, the named standalone contracts, and relevant local projects. This is a local comparison, not an ecosystem-wide originality claim.

**Disposition: KEEP.** Validators check each directed free-text exchange edge; participant approval and compatibility are separate gates.

| Closest comparator | Its judgment | Participants and actions | Its state changes | Capability or invariant implemented here |
|---|---|---|---|---|
| Standalone ClaimNet Semantic Exposure Graph | Classifies a relation between two fixed market claims. | An owner provides two claims and requests a pairwise result. | Stores relation and risk band; it moves no assets. | This contract creates an ordered cycle of two or three distinct offer owners, locks those offers, checks every directed offer-to-request edge, and transfers each exact asset amount once. |
| New License Bundle Clearinghouse | Judges whether selected license terms permit one requested use and whether licenses conflict. | A requester selects works; every distinct licensor approves the exact request digest. | Reserves fees, then issues one permission and distributes fees. | Barter exchanges a different asset between each adjacent participant in a cycle; it does not grant a permission over a bundle or pay fixed license fees. |
| New Partial Settlement Matcher (withheld) | Judges compatibility of settlement conditions for selected obligations. | A case funder creates a dispute; parties to covered obligations approve an exact offer. | Transfers payment rows and discharges only listed obligations. | Both use semantic review plus consent and a reserved ledger. This project is distinct where every two-party match can fail but a fully consented three-party cycle can clear; the withheld matcher settles dispute obligations instead of matching goods. |
| Local MetalSwap | Fetches public metal prices and finalizes a binary market outcome. | Users stake on a side; a finality gate enables claims. | Distributes a pooled market balance. | It settles an externally priced market; it does not interpret offered/requested descriptions or require every member of a barter cycle to consent. |

The mechanism is implemented in contracts/semantic_barter_clearinghouse.py (_assess_cycle, propose_cycle, consent_cycle, execute_cycle). Demo units are internal ledger entries, not delivery or custody of real goods.

**Evidence status:** the 9-test direct suite and StudioNet demonstration both passed. Three incompatible two-party cycles rolled back; the compatible three-party cycle executed after exact consent, and replay of its consumed offers rolled back. The deployed source matches commit `ec60bc2d81ad11afe2d0f9754eb8ed505cc17ccb`. Anonymous URL verification is recorded in the release artifact after repository publication.

## Final self-review

| Gate | Result | Evidence |
|---|---|---|
| Technical readiness | PASS | 9 parameter-expanded direct tests, 3 GenVM lint checks, 13 validated methods, source-blob match, and all 16 StudioNet transactions finalized (12 successful calls and 4 expected rollbacks). |
| Distinctiveness | PASS | Every two-party cycle failed on an incompatible directed edge; the fully consented three-party cycle executed and each consumed-offer replay failed. |
| Evidence readiness | PENDING | Deployment, transaction outcomes, and public-view readback are recorded; anonymous HTTP checks run after publication. |

**Verdict:** READY WITH CAVEATS, pending evidence-link verification.

**What ran:** static source review; 9 mocked direct tests; GenVM lint and SDK validation; live StudioNet deployment, writes, expected-failure transactions, and public-view readback. No integration test suite was run.

**Unverified:** ownership or quality of offered goods, physical delivery, external custody, and real asset settlement. The full internal contract state is not exposed; the recorded readback covers all public views.

**Top caveats:** the faucet mints synthetic balances (`contracts/semantic_barter_clearinghouse.py:174`), and compatibility judgments use participant-provided descriptions (`contracts/semantic_barter_clearinghouse.py:248`).

**Distinct reusable contribution:** a fully consented directed exchange cycle can clear when every two-party orientation fails, while each reserved offer is consumed at most once.
