# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""Minimal consumer proving CalibrationAnchor is a reusable IC primitive."""

from genlayer import *


@gl.contract_interface
class ICalibrationAnchor:
    class View:
        def is_latest_stable(self, suite_id: u256, expected_suite_hash: str, min_run_id: u256) -> bool: ...
        def latest_anchor(self, suite_id: u256) -> dict: ...

    class Write:
        pass


class CalibrationGate(gl.Contract):
    anchor_address: Address
    suite_id: u256
    expected_suite_hash: str
    minimum_run_id: u256
    opened: bool
    opened_run_id: u256
    opened_run_hash: str

    def __init__(
        self,
        anchor_address: Address,
        suite_id: u256,
        expected_suite_hash: str,
        minimum_run_id: u256 = u256(0),
    ):
        self.anchor_address = anchor_address
        self.suite_id = suite_id
        self.expected_suite_hash = expected_suite_hash
        self.minimum_run_id = minimum_run_id
        self.opened = False
        self.opened_run_id = u256(0)
        self.opened_run_hash = ""

    @gl.public.write
    def open_if_calibrated(self) -> None:
        if self.opened:
            raise gl.vm.UserError("CalibrationGate has already been opened")
        anchor = ICalibrationAnchor(self.anchor_address)
        if not anchor.view().is_latest_stable(
            self.suite_id,
            self.expected_suite_hash,
            self.minimum_run_id,
        ):
            raise gl.vm.UserError("latest CalibrationAnchor run is not STABLE for the pinned suite")
        latest = anchor.view().latest_anchor(self.suite_id)
        if latest.get("exists") is not True:
            raise gl.vm.UserError("CalibrationAnchor has no finalized run")
        self.opened = True
        self.opened_run_id = u256(int(latest.get("run_id", 0)))
        self.opened_run_hash = str(latest.get("run_hash", ""))

    @gl.public.view
    def status(self) -> dict:
        return {
            "opened": bool(self.opened),
            "suite_id": int(self.suite_id),
            "expected_suite_hash": str(self.expected_suite_hash),
            "minimum_run_id": int(self.minimum_run_id),
            "opened_run_id": int(self.opened_run_id),
            "opened_run_hash": str(self.opened_run_hash),
        }
