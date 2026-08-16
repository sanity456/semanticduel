# Security audit receipt

Review date: 2026-08-16

Status: reviewed testnet candidate. No critical, high, or medium-severity implementation defects were found in this engineering review. This is not an independent third-party certification.

## Reviewed artifact

- Contract: `contracts/semantic_duel.py`
- Size: 17,134 bytes
- SHA-256: `8fc849d67699b84f85065021227f7ea94691414bcf97d760e9c3a7de83f6c6e8`
- GenVM runner: pinned to `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- The retrieved StudioNet and Bradbury source bytes exactly match this artifact.

## Verification completed

- GenVM lint and SDK schema validation: pass; 6 views, 6 writes, 2 constructor arguments.
- Strict Pyright type check: pass with zero diagnostics.
- Direct-mode tests: 11 passed, including domain-separated commitments, player/round replay resistance, reveal mismatch, deterministic damage, HP safety, terminal states, malformed output, and no-state-on-failure behavior.
- Five-validator GLSim tests: 1 full commit-reveal round passed.
- Live StudioNet workflow: deployment and resolution `FINALIZED / MAJORITY_AGREE`; observed round outcome `TRADE` and HP `5-5`.
- Live Bradbury workflow: deployment and resolution `ACCEPTED / AGREE / FINISHED_WITH_RETURN`; observed round outcome `STALEMATE` and HP `6-6`.
- Dependency integrity: `pip check` passed. Repository secret scan found no wallet, keystore, mnemonic, password, or private-key material.

## Findings and residual risks

- Low: there are no reveal deadlines or forced timeouts. A player can stall after joining or committing; no funds are held, and redeployment is the recovery path.
- Low: weak or reused nonces can expose moves to offline guessing. The offline helper protects transport privacy but cannot create nonce entropy for the player.
- Informational: commitments hide moves only until reveal; contract state and transaction data are public.
- Informational: exact independent LLM agreement favors safety over liveness, while damage mapping remains fully deterministic.

Exact addresses, transaction hashes, status evidence, and workflow hashes are in `evidence/studionet.json` and `evidence/bradbury.json`.
