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

**Evidence status:** implemented; the current direct suite passes 8 tests. Phase 3 still needs adversarial leader, disagreement, access, replay, and accounting-boundary coverage. The StudioNet runner probe passed, but this project has not had its own live demonstration yet.