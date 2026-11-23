"""Validate matches on independent messages from a classroom permutation."""
import csv
from pathlib import Path
import random
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulations.toy_cipher import encrypt


def trial(width, rounds, seed):
    rng = random.Random(seed)
    limit = 1 << width
    key = rng.randrange(limit)
    messages = rng.sample(range(limit), 8)
    expected = [encrypt(m, key, width, rounds) for m in messages]
    rows = []
    for method in ("exhaustive", "random", "greedy", "pair_greedy"):
        stream = random.Random(seed + 1)
        started = perf_counter()
        scores = 0
        encryptions = 0
        verified_keys = []
        budget = limit if method == "exhaustive" else min(1024, limit)

        def score(candidate):
            nonlocal scores, encryptions
            scores += 1
            encryptions += 4
            value = sum((encrypt(m, candidate, width, rounds) ^ c).bit_count()
                        for m, c in zip(messages[:4], expected[:4]))
            if value == 0:
                encryptions += 4
                if all([encrypt(m, candidate, width, rounds) == c
                        for m, c in zip(messages[4:], expected[4:])]):
                    verified_keys.append(candidate)
            return value

        if method in ("exhaustive", "random"):
            candidates = (range(limit) if method == "exhaustive"
                          else stream.sample(range(limit), budget))
            for candidate in candidates:
                score(candidate)
                if verified_keys and method == "random":
                    break
        else:
            masks = [1 << i for i in range(width)]
            if method == "pair_greedy":
                masks += [(1 << i) | (1 << j) for i in range(width) for j in range(i)]
            state = stream.randrange(limit)
            best = score(state)
            while scores < budget and not verified_keys:
                next_state, next_score = state, best
                for mask in masks[:budget-scores]:
                    candidate = state ^ mask
                    value = score(candidate)
                    if value < next_score:
                        next_state, next_score = candidate, value
                    if verified_keys:
                        break
                if next_score < best:
                    state, best = next_state, next_score
                elif scores < budget and not verified_keys:
                    state = stream.randrange(limit)
                    best = score(state)
        rows.append(dict(width=width, rounds=rounds, seed=seed, method=method,
                         valid_match=int(bool(verified_keys)), planted_key_found=int(key in verified_keys),
                         matching_keys=len(set(verified_keys)), scores=scores,
                         encryptions=encryptions, elapsed_ms=1000*(perf_counter()-started)))
    return rows


def main():
    rows = []
    for width in (8, 12, 16):
        for rounds in (2, 4, 8):
            for sample in range(3):
                rows.extend(trial(width, rounds, 20261200 + 100*width + 10*rounds + sample))
    with Path("results/raw/toy.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
