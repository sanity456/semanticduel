# Security and limitations

- Contract state and transactions are public. Commitments hide moves only while nonces remain secret and high entropy.
- `make_commitment` is a convenience view, not a privacy boundary: the RPC provider can observe its arguments. Prefer `tools/make_commitment.py` offline.
- Commitments are domain-separated by contract, player, and round to prevent cross-match and replay substitution.
- Moves and arena prose are ASCII-bounded and delimited as untrusted prompt data.
- Independent exact outcome replay is fail-closed but subjective rounds can lose liveness.
- Damage is deterministic and never chosen by the LLM.
- There are no clocks; a player can stall after committing or before revealing. No funds are at risk in v1.
- A copied commitment is useless for another player because the player address is bound into the digest.
- Address identity is not Sybil-resistant, and no stakes or prizes are included.
