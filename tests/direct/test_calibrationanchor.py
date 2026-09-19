"""Direct-mode lifecycle tests for CalibrationAnchor."""

CONTRACT = "contracts/calibrationanchor.py"
CLASSIFIER = r"CALIBRATIONANCHOR / BENCHMARK CASE"
WEB_URL = "https://example.com/calibration-source"
WEB_BODY = "Official benchmark fixture. The service state is healthy and available."
WEB_BODY_CHANGED = "Official benchmark fixture. The service state is degraded and unavailable."


def mock_label(vm, label):
    vm.clear_mocks()
    vm.mock_llm(CLASSIFIER, label)


def create_draft(vm, deploy, **thresholds):
    vm.warp("2026-09-19T00:00:00+00:00")
    contract = deploy(CONTRACT)
    suite_id = contract.create_suite(
        "Consensus regression suite",
        "Measures whether frozen semantic propositions keep the expected adjudication behaviour.",
        thresholds.get("min_coverage_bps", 9000),
        thresholds.get("stable_agreement_bps", 9500),
        thresholds.get("unsafe_below_bps", 8000),
        thresholds.get("max_uncertain_bps", 1000),
    )
    return contract, suite_id


def add_static(contract, suite_id, number, gold="SUPPORTED", critical=False, weight=1):
    return contract.add_static_case(
        suite_id,
        f"Static case {number}",
        f"Fixture {number}: the control is active and the requirement is satisfied.",
        "The control is active and the requirement is satisfied.",
        gold,
        "The frozen context directly establishes the proposition.",
        weight,
        critical,
    )


def sealed_three(vm, deploy, critical_first=False, **thresholds):
    contract, suite_id = create_draft(vm, deploy, **thresholds)
    cases = [
        add_static(contract, suite_id, 1, critical=critical_first),
        add_static(contract, suite_id, 2),
        add_static(contract, suite_id, 3),
    ]
    contract.seal_suite(suite_id)
    return contract, suite_id, cases


def execute(vm, contract, run_id, case_id, label):
    mock_label(vm, label)
    return contract.execute_case(run_id, case_id)


def finalize_all_supported(vm, contract, suite_id, cases):
    run_id = contract.open_run(suite_id)
    for case_id in cases:
        execute(vm, contract, run_id, case_id, "SUPPORTED")
    contract.finalize_run(run_id)
    return run_id


def test_create_suite_exposes_thresholds(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    suite = contract.get_suite(suite_id)
    assert suite["status_name"] == "DRAFT"
    assert suite["min_coverage_bps"] == 9000
    assert suite["stable_agreement_bps"] == 9500
    assert suite["unsafe_below_bps"] == 8000


def test_rejects_inverted_thresholds(direct_vm, direct_deploy):
    direct_vm.warp("2026-09-19T00:00:00+00:00")
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("stable threshold"):
        contract.create_suite("Bad", "Bad thresholds", 9000, 7000, 8000, 1000)


def test_rejects_out_of_range_thresholds(direct_vm, direct_deploy):
    direct_vm.warp("2026-09-19T00:00:00+00:00")
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("0..10000"):
        contract.create_suite("Bad", "Bad thresholds", 10001, 9500, 8000, 1000)


def test_only_owner_can_add_cases(direct_vm, direct_deploy, direct_alice):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("only suite owner"):
            add_static(contract, suite_id, 1)


def test_static_case_is_hashed_and_readable(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    case_id = add_static(contract, suite_id, 1, weight=7, critical=True)
    case = contract.get_case(case_id)
    assert case["case_type_name"] == "STATIC"
    assert case["gold_verdict_name"] == "SUPPORTED"
    assert case["weight"] == 7
    assert case["critical"] is True
    assert len(case["case_hash"]) == 64
    assert len(case["context_hash"]) == 64


def test_duplicate_case_is_rejected(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    add_static(contract, suite_id, 1)
    with direct_vm.expect_revert("duplicate benchmark case"):
        add_static(contract, suite_id, 1)


def test_invalid_gold_label_is_rejected(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    with direct_vm.expect_revert("gold_verdict"):
        add_static(contract, suite_id, 1, gold="MAYBE")


def test_minimum_three_cases_required(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    add_static(contract, suite_id, 1)
    add_static(contract, suite_id, 2)
    with direct_vm.expect_revert("at least 3"):
        contract.seal_suite(suite_id)


def test_seal_freezes_definition(direct_vm, direct_deploy):
    contract, suite_id, _ = sealed_three(direct_vm, direct_deploy)
    suite = contract.get_suite(suite_id)
    assert suite["status_name"] == "SEALED"
    assert len(suite["suite_hash"]) == 64
    with direct_vm.expect_revert("suite is not draft"):
        add_static(contract, suite_id, 4)


def test_open_run_is_permissionless(direct_vm, direct_deploy, direct_alice):
    contract, suite_id, _ = sealed_three(direct_vm, direct_deploy)
    with direct_vm.prank(direct_alice):
        run_id = contract.open_run(suite_id)
    assert contract.get_run(run_id)["status_name"] == "OPEN"


def test_only_one_run_open_per_suite(direct_vm, direct_deploy):
    contract, suite_id, _ = sealed_three(direct_vm, direct_deploy)
    contract.open_run(suite_id)
    with direct_vm.expect_revert("already open"):
        contract.open_run(suite_id)


def test_static_match_records_consensus_result(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = contract.open_run(suite_id)
    result_id = execute(direct_vm, contract, run_id, cases[0], "SUPPORTED")
    result = contract.get_result(result_id)
    assert result["runtime_state_name"] == "OK"
    assert result["observed_verdict_name"] == "SUPPORTED"
    assert result["outcome_name"] == "MATCH"
    assert direct_vm.run_validator() is True


def test_static_flip_is_not_relabelled_as_match(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = contract.open_run(suite_id)
    result_id = execute(direct_vm, contract, run_id, cases[0], "NOT_SUPPORTED")
    assert contract.get_result(result_id)["outcome_name"] == "FLIP"


def test_ambiguous_on_clear_gold_is_uncertain(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = contract.open_run(suite_id)
    result_id = execute(direct_vm, contract, run_id, cases[0], "AMBIGUOUS")
    assert contract.get_result(result_id)["outcome_name"] == "UNCERTAIN"


def test_ambiguous_gold_can_match(direct_vm, direct_deploy):
    contract, suite_id = create_draft(direct_vm, direct_deploy)
    case_id = add_static(contract, suite_id, 1, gold="AMBIGUOUS")
    add_static(contract, suite_id, 2)
    add_static(contract, suite_id, 3)
    contract.seal_suite(suite_id)
    run_id = contract.open_run(suite_id)
    result_id = execute(direct_vm, contract, run_id, case_id, "AMBIGUOUS")
    assert contract.get_result(result_id)["outcome_name"] == "MATCH"


def test_same_case_cannot_execute_twice(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = contract.open_run(suite_id)
    execute(direct_vm, contract, run_id, cases[0], "SUPPORTED")
    with direct_vm.expect_revert("already executed"):
        execute(direct_vm, contract, run_id, cases[0], "SUPPORTED")


def test_case_from_other_suite_is_rejected(direct_vm, direct_deploy):
    contract, suite_id, _ = sealed_three(direct_vm, direct_deploy)
    other = contract.create_suite("Other", "Other benchmark", 9000, 9500, 8000, 1000)
    foreign = add_static(contract, other, 9)
    run_id = contract.open_run(suite_id)
    with direct_vm.expect_revert("another suite"):
        execute(direct_vm, contract, run_id, foreign, "SUPPORTED")


def test_cannot_finalize_partial_run(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = contract.open_run(suite_id)
    execute(direct_vm, contract, run_id, cases[0], "SUPPORTED")
    with direct_vm.expect_revert("every benchmark case"):
        contract.finalize_run(run_id)


def test_all_matches_finalize_stable(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = finalize_all_supported(direct_vm, contract, suite_id, cases)
    run = contract.get_run(run_id)
    assert run["calibration_state_name"] == "STABLE"
    assert run["coverage_bps"] == 10000
    assert run["agreement_bps"] == 10000
    assert len(run["behavior_hash"]) == 64
    assert len(run["run_hash"]) == 64


def test_latest_stable_requires_exact_suite_hash(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = finalize_all_supported(direct_vm, contract, suite_id, cases)
    suite_hash = contract.current_suite_hash(suite_id)
    assert contract.is_latest_stable(suite_id, suite_hash, run_id) is True
    assert contract.is_latest_stable(suite_id, "0" * 64, run_id) is False
    assert contract.is_latest_stable(suite_id, suite_hash, run_id + 1) is False


def test_critical_flip_forces_unsafe(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy, critical_first=True)
    run_id = contract.open_run(suite_id)
    execute(direct_vm, contract, run_id, cases[0], "NOT_SUPPORTED")
    execute(direct_vm, contract, run_id, cases[1], "SUPPORTED")
    execute(direct_vm, contract, run_id, cases[2], "SUPPORTED")
    contract.finalize_run(run_id)
    run = contract.get_run(run_id)
    assert run["critical_failures"] == 1
    assert run["calibration_state_name"] == "UNSAFE"


def test_noncritical_degradation_can_be_shifted(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(
        direct_vm,
        direct_deploy,
        stable_agreement_bps=9000,
        unsafe_below_bps=3000,
        max_uncertain_bps=4000,
    )
    run_id = contract.open_run(suite_id)
    execute(direct_vm, contract, run_id, cases[0], "NOT_SUPPORTED")
    execute(direct_vm, contract, run_id, cases[1], "SUPPORTED")
    execute(direct_vm, contract, run_id, cases[2], "SUPPORTED")
    contract.finalize_run(run_id)
    assert contract.get_run(run_id)["calibration_state_name"] == "SHIFTED"


def test_retired_suite_cannot_open_new_run(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    finalize_all_supported(direct_vm, contract, suite_id, cases)
    contract.retire_suite(suite_id)
    assert contract.get_suite(suite_id)["status_name"] == "RETIRED"
    with direct_vm.expect_revert("suite is not active"):
        contract.open_run(suite_id)


def test_cannot_retire_with_open_run(direct_vm, direct_deploy):
    contract, suite_id, _ = sealed_three(direct_vm, direct_deploy)
    contract.open_run(suite_id)
    with direct_vm.expect_revert("cannot retire"):
        contract.retire_suite(suite_id)


def test_second_run_records_behavior_change_count(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(
        direct_vm,
        direct_deploy,
        stable_agreement_bps=6000,
        unsafe_below_bps=2000,
    )
    first = finalize_all_supported(direct_vm, contract, suite_id, cases)
    first_hash = contract.get_run(first)["behavior_hash"]

    second = contract.open_run(suite_id)
    execute(direct_vm, contract, second, cases[0], "NOT_SUPPORTED")
    execute(direct_vm, contract, second, cases[1], "SUPPORTED")
    execute(direct_vm, contract, second, cases[2], "SUPPORTED")
    contract.finalize_run(second)
    second_run = contract.get_run(second)
    assert second_run["previous_run_id"] == first
    assert second_run["changed_count"] == 1
    assert second_run["behavior_hash"] != first_hash


def test_latest_anchor_exposes_finalized_hashes(direct_vm, direct_deploy):
    contract, suite_id, cases = sealed_three(direct_vm, direct_deploy)
    run_id = finalize_all_supported(direct_vm, contract, suite_id, cases)
    anchor = contract.latest_anchor(suite_id)
    assert anchor["exists"] is True
    assert anchor["run_id"] == run_id
    assert anchor["calibration_state_name"] == "STABLE"
    assert len(anchor["run_hash"]) == 64
