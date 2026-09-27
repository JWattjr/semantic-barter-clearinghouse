import json

import pytest


SDK = "v0.6.0-rc5"
OPEN_TIME = "2030-01-01T12:00:00Z"
OFFER_EXPIRY = "2030-01-10T00:00:00Z"
CONSENT_DEADLINE = "2030-01-08T00:00:00Z"


def llm(value) -> str:
    """The direct mock decodes once; the v0.6 SDK then parses JSON text."""
    return json.dumps(json.dumps(value))


def address_key(address):
    if isinstance(address, bytes):
        return "0x" + address.hex()
    return str(address).lower()


def deploy(direct_vm, direct_deploy, direct_owner):
    direct_vm.sender = direct_owner
    direct_vm.warp(OPEN_TIME)
    return direct_deploy("contracts/semantic_barter_clearinghouse.py", sdk_version=SDK)


def offer(contract, direct_vm, participant, offer_id, asset_id, units, offered, requested, expiry=OFFER_EXPIRY):
    with direct_vm.prank(participant):
        contract.deposit_demo_asset(asset_id, 10)
        return contract.create_offer(offer_id, asset_id, units, offered, requested, expiry)


def make_three_offers(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    a = offer(
        contract, direct_vm, direct_alice, "offer-a", "drill", 1,
        "A hand drill in good working condition with one battery charger.",
        "A set of stainless fasteners suitable for indoor construction.",
    )
    b = offer(
        contract, direct_vm, direct_bob, "offer-b", "fasteners", 2,
        "A set of stainless fasteners suitable for indoor construction.",
        "One sealed tin of interior wall paint in neutral white.",
    )
    c = offer(
        contract, direct_vm, direct_charlie, "offer-c", "paint", 3,
        "One sealed tin of interior wall paint in neutral white.",
        "A hand drill in good working condition with one battery charger.",
    )
    return a, b, c


def edges_for(keys, compatibilities):
    rows = []
    for index, receiver_key in enumerate(keys):
        giver_key = keys[(index + 1) % len(keys)]
        rows.append({
            "giver_offer_key": giver_key,
            "receiver_offer_key": receiver_key,
            "compatible": compatibilities[index],
        })
    return {"edges": rows}


def test_three_party_cycle_clears_only_after_exact_consent_and_conserves_each_asset(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, direct_charlie
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    a, b, c = make_three_offers(contract, direct_vm, direct_alice, direct_bob, direct_charlie)

    # A and B can satisfy only one direction, so a two-party exchange cannot clear.
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(edges_for([a, b], [True, False])))
    with direct_vm.expect_revert("incompatible directed exchange"):
        contract.propose_cycle(json.dumps([a, b]), CONSENT_DEADLINE)
    assert contract.get_offer(address_key(direct_alice), "offer-a")["status"] == "ACTIVE"
    assert contract.get_offer(address_key(direct_bob), "offer-b")["status"] == "ACTIVE"

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(edges_for([a, b, c], [True, True, True])))
    proposed = contract.propose_cycle(json.dumps([a, b, c]), CONSENT_DEADLINE)
    assert proposed["cycle_id"] == "C-000001"
    assert proposed["status"] == "PENDING"
    assert direct_vm.run_validator()

    with direct_vm.prank(direct_owner):
        with direct_vm.expect_revert("only a cycle participant"):
            contract.consent_cycle("C-000001")
    with direct_vm.prank(direct_alice):
        contract.consent_cycle("C-000001")
        with direct_vm.expect_revert("already consented"):
            contract.consent_cycle("C-000001")
        with direct_vm.expect_revert("every participant must consent"):
            contract.execute_cycle("C-000001")
    with direct_vm.prank(direct_bob):
        contract.consent_cycle("C-000001")
    with direct_vm.prank(direct_charlie):
        contract.consent_cycle("C-000001")
    assert contract.get_cycle("C-000001")["status"] == "READY"

    result = contract.execute_cycle("C-000001")
    assert result["status"] == "EXECUTED"
    assert len(result["transfers"]) == 3
    assert contract.get_balance(address_key(direct_alice), "fasteners") == 2
    assert contract.get_balance(address_key(direct_bob), "paint") == 3
    assert contract.get_balance(address_key(direct_charlie), "drill") == 1
    with direct_vm.expect_revert("every participant must consent"):
        contract.execute_cycle("C-000001")
    for asset in ("drill", "fasteners", "paint"):
        accounting = contract.get_asset_accounting(asset)
        assert accounting["minted_units"] == 10
        assert accounting["available_units"] == 10
        assert accounting["reserved_units"] == 0
        assert accounting["conserved"] is True


def test_validator_rejects_disagreement_and_unknown_edge_fields(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    a = offer(
        contract, direct_vm, direct_alice, "offer-a", "drill", 1,
        "A hand drill in good working condition with one battery charger.",
        "A set of stainless fasteners suitable for indoor construction.",
    )
    b = offer(
        contract, direct_vm, direct_bob, "offer-b", "fasteners", 2,
        "A set of stainless fasteners suitable for indoor construction.",
        "A hand drill in good working condition with one battery charger.",
    )
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(edges_for([a, b], [True, True])))
    proposed = contract.propose_cycle(json.dumps([a, b]), CONSENT_DEADLINE)
    assert direct_vm.run_validator()
    honest = {"edges": proposed["compatibility_edges"]}

    disagreement = json.loads(json.dumps(honest))
    disagreement["edges"][0]["compatible"] = False
    assert direct_vm.run_validator(leader_result=disagreement) is False

    forged = json.loads(json.dumps(honest))
    forged["edges"][0]["leader_override"] = True
    assert direct_vm.run_validator(leader_result=forged) is False

    reordered = json.loads(json.dumps(honest))
    reordered["edges"].reverse()
    assert direct_vm.run_validator(leader_result=reordered) is False


def test_malformed_model_edges_fail_closed_without_locking_offers(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    a = offer(
        contract, direct_vm, direct_alice, "bad-a", "drill", 1,
        "A hand drill in good working condition with one battery charger.",
        "A set of stainless fasteners suitable for indoor construction.",
    )
    b = offer(
        contract, direct_vm, direct_bob, "bad-b", "fasteners", 2,
        "A set of stainless fasteners suitable for indoor construction.",
        "A hand drill in good working condition with one battery charger.",
    )
    malformed = edges_for([a, b], [True, True])
    malformed["edges"][0]["extra"] = "leader-controlled"
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(malformed))
    with direct_vm.expect_revert("invalid compatibility response"):
        contract.propose_cycle(json.dumps([a, b]), CONSENT_DEADLINE)
    assert contract.get_offer(address_key(direct_alice), "bad-a")["status"] == "ACTIVE"
    assert contract.get_offer(address_key(direct_bob), "bad-b")["status"] == "ACTIVE"
    assert contract.get_asset_accounting("drill")["reserved_units"] == 1


def test_participant_can_cancel_cycle_and_release_offer_reservations(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    a = offer(
        contract, direct_vm, direct_alice, "cancel-a", "drill", 1,
        "A hand drill in good working condition with one battery charger.",
        "A set of stainless fasteners suitable for indoor construction.",
    )
    b = offer(
        contract, direct_vm, direct_bob, "cancel-b", "fasteners", 2,
        "A set of stainless fasteners suitable for indoor construction.",
        "A hand drill in good working condition with one battery charger.",
    )
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(edges_for([a, b], [True, True])))
    contract.propose_cycle(json.dumps([a, b]), CONSENT_DEADLINE)
    with direct_vm.prank(direct_owner):
        with direct_vm.expect_revert("only a cycle participant"):
            contract.cancel_cycle("C-000001")
    with direct_vm.prank(direct_alice):
        contract.consent_cycle("C-000001")
    with direct_vm.prank(direct_bob):
        contract.cancel_cycle("C-000001")
        with direct_vm.expect_revert("no longer cancellable"):
            contract.cancel_cycle("C-000001")
    with direct_vm.prank(direct_alice):
        contract.cancel_offer("cancel-a")
        with direct_vm.expect_revert("no longer active"):
            contract.cancel_offer("cancel-a")
    with direct_vm.prank(direct_bob):
        contract.cancel_offer("cancel-b")
    assert contract.get_balance(address_key(direct_alice), "drill") == 10
    assert contract.get_balance(address_key(direct_bob), "fasteners") == 10
    assert contract.get_asset_accounting("drill")["conserved"] is True
    assert contract.get_asset_accounting("fasteners")["conserved"] is True


def test_expired_pending_cycle_unlocks_and_expired_offers_return_to_owners(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    a = offer(
        contract, direct_vm, direct_alice, "expire-a", "drill", 1,
        "A hand drill in good working condition with one battery charger.",
        "A set of stainless fasteners suitable for indoor construction.",
    )
    b = offer(
        contract, direct_vm, direct_bob, "expire-b", "fasteners", 2,
        "A set of stainless fasteners suitable for indoor construction.",
        "A hand drill in good working condition with one battery charger.",
    )
    direct_vm.mock_llm(r"SEMANTIC BARTER EDGE REVIEW", llm(edges_for([a, b], [True, True])))
    contract.propose_cycle(json.dumps([a, b]), "2030-01-02T00:00:00Z")
    with direct_vm.prank(direct_alice):
        contract.consent_cycle("C-000001")
    direct_vm.warp("2030-01-11T00:00:00Z")
    contract.expire_cycle("C-000001")
    contract.expire_offer(address_key(direct_alice), "expire-a")
    contract.expire_offer(address_key(direct_bob), "expire-b")
    assert contract.get_cycle("C-000001")["status"] == "EXPIRED"
    assert contract.get_balance(address_key(direct_alice), "drill") == 10
    assert contract.get_balance(address_key(direct_bob), "fasteners") == 10
    assert contract.get_asset_accounting("drill")["conserved"] is True
    assert contract.get_asset_accounting("fasteners")["conserved"] is True


@pytest.mark.parametrize(
    "keys_json, deadline, message",
    [
        ("[]", CONSENT_DEADLINE, "exactly two or three"),
        ('["x","x"]', CONSENT_DEADLINE, "only once"),
        ('["x","y"]', "2030-01-01T00:00:00Z", "must be in the future"),
    ],
)
def test_cycle_input_bounds_are_enforced_before_model_call(
    direct_vm, direct_deploy, direct_owner, keys_json, deadline, message
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    with direct_vm.expect_revert(message):
        contract.propose_cycle(keys_json, deadline)
