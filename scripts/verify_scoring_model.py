"""Offline sanity checks for CalibrationAnchor's deterministic scoring rules."""

BPS = 10000
STABLE = "STABLE"
SHIFTED = "SHIFTED"
UNSAFE = "UNSAFE"
INSUFFICIENT = "INSUFFICIENT_COVERAGE"


def classify(total, valid, matches, uncertain, critical_semantic, critical_coverage,
             min_coverage=9000, stable_agreement=9500, unsafe_below=8000,
             max_uncertain=1000):
    coverage = (valid * BPS) // total if total else 0
    agreement = (matches * BPS) // valid if valid else 0
    uncertainty = (uncertain * BPS) // valid if valid else 0
    if coverage < min_coverage or critical_coverage > 0:
        state = INSUFFICIENT
    elif critical_semantic > 0 or agreement < unsafe_below:
        state = UNSAFE
    elif agreement < stable_agreement or uncertainty > max_uncertain:
        state = SHIFTED
    else:
        state = STABLE
    return state, coverage, agreement, uncertainty


def main():
    assert classify(3, 3, 3, 0, 0, 0)[0] == STABLE
    assert classify(3, 2, 2, 0, 0, 0)[0] == INSUFFICIENT
    assert classify(10, 10, 9, 1, 0, 0, stable_agreement=9000, max_uncertain=500)[0] == SHIFTED
    assert classify(3, 3, 2, 0, 1, 0, stable_agreement=6000, unsafe_below=2000)[0] == UNSAFE
    assert classify(100, 100, 100, 0, 0, 1)[0] == INSUFFICIENT
    assert classify(10, 10, 7, 0, 0, 0)[0] == UNSAFE
    print("Deterministic scoring sanity checks: PASS")


if __name__ == "__main__":
    main()
