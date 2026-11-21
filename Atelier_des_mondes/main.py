"""Entry point for Atelier des mondes (kernel)."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.kernel import Kernel


def main():
    parser = argparse.ArgumentParser(description="Atelier des mondes - Kernel")
    parser.add_argument("--data", default="data", help="Data directory")
    parser.add_argument("--demo", action="store_true", help="Run demo flow")
    args = parser.parse_args()

    kernel = Kernel(data_dir=args.data)
    kernel.start()

    if args.demo:
        # demo: create project, save version, recover
        pid = kernel.projects.create("Demo Project", "demo")
        kernel.projects.save_version(pid, {"hello": "world"})
        print("Created project", pid)
        print("Versions:", kernel.projects.list_versions(pid))
        print("Diagnostics:")
        print(kernel.diagnostics.report())

    kernel.stop()
    print("Done.")


if __name__ == "__main__":
    main()
