import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.kernel import Kernel


def test_kernel_starts_no_modules():
    d = tempfile.mkdtemp()
    k = Kernel(data_dir=os.path.join(d, "data"))
    k.start()
    assert k.status() == {}
    k.stop()


def test_register_example_module():
    d = tempfile.mkdtemp()
    k = Kernel(data_dir=os.path.join(d, "data"))
    from modules.example_module import ExampleModule
    assert k.register_module(ExampleModule())
    k.start()
    assert k.status()["example_module"][0] == "Actif"
    k.stop()


def test_project_create_save_restore():
    d = tempfile.mkdtemp()
    k = Kernel(data_dir=os.path.join(d, "data"))
    k.start()
    pid = k.projects.create("P1")
    vid = k.projects.save_version(pid, {"x": 5})
    vers = k.projects.list_versions(pid)
    assert len(vers) == 1
    snap = k.projects.restore_version(pid, vid)
    assert snap == {"x": 5}
    k.stop()


def test_resource_safe_access():
    d = tempfile.mkdtemp()
    k = Kernel(data_dir=os.path.join(d, "data"))
    k.start()
    p = k.resources.temp_file("t.txt")
    k.resources.write_bytes(p, b"hi")
    assert k.resources.read_bytes(p) == b"hi"
    try:
        k.resources.read_bytes("/etc/passwd")
        raised = False
    except PermissionError:
        raised = True
    assert raised
    k.stop()
