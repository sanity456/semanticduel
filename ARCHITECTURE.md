# Architecture

One deployment represents one match. The creator is Player A; a distinct joining account becomes Player B. Each round is deterministic except for one closed semantic judgment. Players commit domain-separated SHA-256 hashes bound to contract address, player address, round, normalized move, and nonce. Only after both commitments exist can either move be revealed.

Once both reveals match, the leader and every validator independently adjudicate the frozen simultaneous moves as `A_WIN`, `B_WIN`, `TRADE`, or `STALEMATE`. They must agree exactly. Deterministic code maps the outcome to damage, appends an immutable round record, advances the phase, and decides the match from HP or the round cap.

The included offline helper computes commitments without contacting a node. There is no frontend, backend, token, randomness beacon, or secret on-chain state.
