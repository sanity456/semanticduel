"""Offline SemanticDuel commitment helper. This script never contacts an RPC."""

from __future__ import annotations
import argparse
import hashlib
import json


def commitment(contract: str, player: str, round_number: int, move: str, nonce: str) -> str:
    payload = {
        "schema": "semanticduel/commitment/v1",
        "contract": contract.lower(),
        "player": player.lower(),
        "round": round_number,
        "move": move.replace("\r\n", "\n").replace("\r", "\n").strip(),
        "nonce": nonce.strip(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("ascii")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--player", required=True)
    parser.add_argument("--round", type=int, required=True, dest="round_number")
    parser.add_argument("--move", required=True)
    parser.add_argument("--nonce", required=True)
    args = parser.parse_args()
    print(commitment(args.contract, args.player, args.round_number, args.move, args.nonce))


if __name__ == "__main__":
    main()
