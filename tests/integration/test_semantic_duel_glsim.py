from __future__ import annotations
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address
from fixtures.match import A_WIN, ARENA, MAX_ROUNDS, MOVE_A, MOVE_B, NONCE_A, NONCE_B
from tools.make_commitment import commitment

PROMPT = "independent referee for one simultaneous combat round"


def test_five_validator_round():
    account_a, account_b = create_accounts(2)
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps(A_WIN)}})
    context = {"validators": [validator.to_dict() for validator in validators]}
    path = Path(__file__).resolve().parents[2] / "contracts" / "semantic_duel.py"
    factory = get_contract_factory(contract_file_path=path)
    receipt = factory.deploy_contract_tx(args=[ARENA, MAX_ROUNDS], account=account_a, wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(receipt)
    contract_address = extract_contract_address(receipt)
    contract_a = factory.build_contract(contract_address, account=account_a)
    contract_b = contract_a.connect(account_b)
    assert tx_execution_succeeded(contract_b.join(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    commitment_a = commitment(str(contract_address), account_a.address, 1, MOVE_A, NONCE_A)
    commitment_b = commitment(str(contract_address), account_b.address, 1, MOVE_B, NONCE_B)
    assert tx_execution_succeeded(contract_a.commit_move(args=[commitment_a]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert tx_execution_succeeded(contract_b.commit_move(args=[commitment_b]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert tx_execution_succeeded(contract_a.reveal_move(args=[MOVE_A, NONCE_A]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert tx_execution_succeeded(contract_b.reveal_move(args=[MOVE_B, NONCE_B]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    resolved = contract_a.resolve_round(args=[]).transact(transaction_context=context, wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(resolved)
    assert contract_a.get_round(args=[0]).call()["outcome"] == "A_WIN"
