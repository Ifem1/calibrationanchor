import pytest


@pytest.fixture(scope="session", autouse=True)
def _windows_gltest_stdin_cleanup_compatibility():
    """Restore stdin before gltest unlinks its temporary calldata file on Windows."""
    import os
    import sys

    if sys.platform != "win32":
        yield
        return

    from gltest.direct import loader

    original = loader._inject_message_to_fd0
    original_load = loader._load_module

    def inject_with_windows_safe_unlink(vm):
        import tempfile

        from genlayer.py import calldata
        from genlayer.py.types import Address

        sender = Address(vm.sender) if isinstance(vm.sender, bytes) else vm.sender
        contract = Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address
        origin = Address(vm.origin) if isinstance(vm.origin, bytes) else vm.origin
        message = {
            "contract_address": contract,
            "sender_address": sender,
            "origin_address": origin,
            "stack": [],
            "value": vm._value,
            "datetime": vm._datetime,
            "is_init": False,
            "chain_id": vm._chain_id,
            "entry_kind": 0,
            "entry_data": b"",
            "entry_stage_data": None,
        }
        encoded = calldata.encode(message)
        fd, path = tempfile.mkstemp()
        original_stdin = os.dup(0)
        vm._original_stdin_fd = original_stdin
        try:
            os.write(fd, encoded)
            os.lseek(fd, 0, 0)
            os.dup2(fd, 0)
        finally:
            os.close(fd)
        # Windows cannot unlink an open file. Keep it until the loader has
        # imported the contract and its message context, then restore stdin.
        pending_paths.append(path)

    pending_paths = []

    def load_module_and_cleanup(contract_path):
        try:
            return original_load(contract_path)
        finally:
            if pending_paths:
                from gltest.direct import wasi_mock

                vm = getattr(wasi_mock._local, "vm", None)
                saved_fd = getattr(vm, "_original_stdin_fd", None) if vm is not None else None
                if saved_fd is not None:
                    os.dup2(saved_fd, 0)
                    os.close(saved_fd)
                    vm._original_stdin_fd = None
                while pending_paths:
                    path = pending_paths.pop()
                    try:
                        os.unlink(path)
                    except FileNotFoundError:
                        pass

    loader._inject_message_to_fd0 = inject_with_windows_safe_unlink
    loader._load_module = load_module_and_cleanup
    try:
        yield
    finally:
        loader._inject_message_to_fd0 = original
        loader._load_module = original_load


@pytest.fixture(autouse=True)
def _strict_direct_mode(direct_vm):
    direct_vm.check_pickling = True
    # Keep stable-tooling transaction timestamps synchronized after warp.
    original_refresh = direct_vm._refresh_gl_message

    def refresh_with_datetime():
        original_refresh()
        import sys

        gl = sys.modules.get("genlayer.gl")
        if gl is not None and isinstance(getattr(gl, "message_raw", None), dict):
            gl.message_raw["datetime"] = direct_vm._datetime

    direct_vm._refresh_gl_message = refresh_with_datetime
    direct_vm._refresh_gl_message()
    yield
