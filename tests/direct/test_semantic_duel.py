from __future__ import annotations
import json
import pytest
from fixtures.match import A_WIN, ARENA, B_WIN, MAX_ROUNDS, MOVE_A, MOVE_B, NONCE_A, NONCE_B
from tests.conftest import CONTRACT_PATH, DIRECT_SDK_VERSION
from tools.make_commitment import commitment

PROMPT = r"independent referee for one simultaneous combat round"


def join_and_commit(contract, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_bob
    contract.join()
    direct_vm.sender = direct_alice
    commitment_a = contract.make_commitment(MOVE_A, NONCE_A)
    contract.commit_move(commitment_a)
    direct_vm.sender = direct_bob
    commitment_b = contract.make_commitment(MOVE_B, NONCE_B)
    contract.commit_move(commitment_b)
    return commitment_a, commitment_b


def reveal(contract, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract.reveal_move(MOVE_A, NONCE_A)
    direct_vm.sender = direct_bob
    contract.reveal_move(MOVE_B, NONCE_B)


def prepare_round(contract, direct_vm, direct_alice, direct_bob, already_joined=False):
    if not already_joined:
        join_and_commit(contract, direct_vm, direct_alice, direct_bob)
    else:
        direct_vm.sender = direct_alice
        contract.commit_move(contract.make_commitment(MOVE_A, NONCE_A))
        direct_vm.sender = direct_bob
        contract.commit_move(contract.make_commitment(MOVE_B, NONCE_B))
    reveal(contract, direct_vm, direct_alice, direct_bob)


def test_commit_reveal_and_round_resolution(semanticduel, direct_vm, direct_alice, direct_bob):
    commits = join_and_commit(semanticduel, direct_vm, direct_alice, direct_bob)
    assert all(value.startswith("sha256:") for value in commits)
    reveal(semanticduel, direct_vm, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps(A_WIN))
    semanticduel.resolve_round()
    state = semanticduel.get_state()
    assert state["round"] == 2
    assert state["hp_a"] == 6
    assert state["hp_b"] == 4
    assert state["phase"] == "COMMITTING"
    record = semanticduel.get_round(0)
    assert record["outcome"] == "A_WIN"
    assert record["damage_b"] == 2


def test_offline_helper_matches_contract(semanticduel, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_bob
    semanticduel.join()
    direct_vm.sender = direct_alice
    onchain = semanticduel.make_commitment(MOVE_A, NONCE_A)
    address = f"0x{bytes(direct_vm._contract_address).hex()}" if isinstance(direct_vm._contract_address, bytes) else str(direct_vm._contract_address)
    player = f"0x{bytes(direct_alice).hex()}"
    assert onchain == commitment(address, player, 1, MOVE_A, NONCE_A)


def test_commitment_binds_nonce_player_and_round(semanticduel, direct_vm, direct_alice, direct_bob):
    join_and_commit(semanticduel, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("player_a_commitment_mismatch"):
        semanticduel.reveal_move(MOVE_A, "wrong_nonce_2026")
    semanticduel.reveal_move(MOVE_A, NONCE_A)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("player_b_commitment_mismatch"):
        semanticduel.reveal_move(MOVE_A, NONCE_A)


def test_three_wins_finish_match(semanticduel, direct_vm, direct_alice, direct_bob):
    for index in range(3):
        prepare_round(semanticduel, direct_vm, direct_alice, direct_bob, already_joined=index > 0)
        direct_vm.mock_llm(PROMPT, json.dumps(A_WIN))
        semanticduel.resolve_round()
        direct_vm.clear_mocks()
    state = semanticduel.get_state()
    assert state["winner"] == "A"
    assert state["resolution"] == "CONSENSUS"
    assert state["hp_b"] == 0
    assert semanticduel.get_round_count() == 3


def test_malformed_output_writes_no_round(semanticduel, direct_vm, direct_alice, direct_bob):
    prepare_round(semanticduel, direct_vm, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"outcome": "A_WIN", "damage": 99}))
    with direct_vm.expect_revert("[LLM_ERROR]"):
        semanticduel.resolve_round()
    assert semanticduel.get_round_count() == 0
    assert semanticduel.get_state()["hp_b"] == 6


def test_validator_replays(semanticduel, direct_vm, direct_alice, direct_bob):
    prepare_round(semanticduel, direct_vm, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps(A_WIN))
    semanticduel.resolve_round()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps(B_WIN))
    assert direct_vm.run_validator(leader_result=leader) is False
    assert direct_vm.run_validator(leader_error=RuntimeError("broken")) is False


def test_forfeit_and_cancel(semanticduel, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_bob
    semanticduel.join()
    semanticduel.forfeit()
    assert semanticduel.get_state()["winner"] == "A"


def test_cancel_before_join(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(str(CONTRACT_PATH), ARENA, MAX_ROUNDS, sdk_version=DIRECT_SDK_VERSION)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_creator"):
        contract.cancel_unjoined()
    direct_vm.sender = direct_alice
    contract.cancel_unjoined()
    assert contract.get_state()["winner"] == "CANCELLED"


@pytest.mark.parametrize(
    ("arena", "rounds", "message"),
    [("short", MAX_ROUNDS, "invalid_arena"), (ARENA, 2, "invalid_max_rounds"), (ARENA, 13, "invalid_max_rounds")],
)
def test_constructor_validation(direct_vm, direct_deploy, direct_alice, arena, rounds, message):
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert(message):
        direct_deploy(str(CONTRACT_PATH), arena, rounds, sdk_version=DIRECT_SDK_VERSION)
