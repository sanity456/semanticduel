# SemanticDuel

SemanticDuel is a standalone, frontend-free GenLayer game for simultaneous natural-language combat. Players commit and reveal moves; validators agree on a closed round outcome; deterministic code applies damage and advances the match.

Writes: `join`, `commit_move`, `reveal_move`, `resolve_round`, `forfeit`, `cancel_unjoined`.

Views: `make_commitment`, `get_state`, `get_revealed_moves`, `get_round_count`, `get_round`, `get_policy`.

For private commitment preparation, use `tools/make_commitment.py` locally rather than sending the move and nonce to an RPC view.

```powershell
genvm-lint check contracts/semantic_duel.py
python -m pytest tests/direct -v

# Terminal 1: start a five-validator GLSim network.
python tests/run_glsim.py --port 4000 --validators 5 --no-browser

# Terminal 2: run the integration suite while GLSim is running.
python -m pytest tests/integration -v -s
```

See `ARCHITECTURE.md`, `SECURITY.md`, `AUDIT.md`, and `evidence/` before deployment.
