import os
from pathlib import Path
import random
import subprocess
from contextlib import contextmanager
import sys
import tempfile
import threading
import time
import traceback
import _thread

failures = []


def main():
    # print(install_some_things(0))

    threads = []

    for thread_i in range(20):
        t = threading.Thread(target=thread_main, args=(thread_i,))
        t.daemon = True
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

        if failures:
            sys.exit(1)


def thread_main(thread_i):
    # pip_version = random.choice(["22.2.2", "21.3.1", "20.3.4"])  # 💥
    # pip_version = "20.3.4"  # ✅
    # pip_version = "22.2.2"  # ✅
    # pip_version = "21.3.1"  # ✅
    # pip_version = ["21.3.1", "20.3.4"][thread_i % 2]  # ✅
    # pip_version = ["22.2.2", "21.3.1", "20.3.4"][thread_i % 3]  # 💥
    # pip_version = ["22.2.2", "20.3.4"][thread_i % 2]  # 💥
    # pip_version = ["22.2.2", "21.3.1"][thread_i % 2]  # 💥
    # pip_version = ["22.2.2", "22.2.1"][thread_i % 2]  # ✅
    pip_version = ["22.2", "22.1.2"][thread_i % 2]  # 💥

    try:
        install_some_things_in_a_venv(pip_version)
        print(f"thread {thread_i} done")
    except subprocess.CalledProcessError as e:
        print(f"thread {thread_i} failed: {e}")
        print(e.stdout)
        print(e.stderr)
        traceback.print_exc()
        failures.append(e)
    except Exception as e:
        print(f"thread {thread_i} failed: {e}")
        traceback.print_exc()
        failures.append(e)


def install_some_things_in_a_venv(pip_version):
    with venv() as env:
        subprocess.run(
            [
                "python",
                "-m",
                "pip",
                "install",
                f"pip=={pip_version}",
            ],
            text=True,
            capture_output=True,
            check=True,
            env=env,
        )
        for _ in range(10):
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "setuptools",
                    "wheel",
                    "delocate",
                ],
                text=True,
                capture_output=True,
                check=True,
                env=env,
            )
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "uninstall",
                    "-y",
                    "setuptools",
                    "wheel",
                    "delocate",
                ],
                text=True,
                capture_output=True,
                check=True,
                env=env,
            )


@contextmanager
def venv():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        subprocess.run(
            [
                sys.executable,
                "-m",
                "venv",
                str(tmp_path),
            ]
        )

        env = os.environ.copy()

        if sys.platform == "win32":
            env["PATH"] = os.pathsep.join(
                [str(tmp_path), f"{tmp_path}/Scripts", env["PATH"]]
            )
        else:
            env["PATH"] = os.pathsep.join([f"{tmp_path}/bin", env["PATH"]])

        active_python = subprocess.run(
            ["python", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            shell=(sys.platform == "win32"),
            env=env,
        ).stdout.strip()

        if sys.platform == "win32":
            assert (
                Path(active_python).resolve() == Path(f"{tmp_path}/python").resolve()
            ), f"active_python mismatch: {active_python}, {tmp_path}"
        else:
            assert (
                Path(active_python).resolve()
                == Path(f"{tmp_path}/bin/python").resolve()
            )

        yield env


if __name__ == "__main__":
    main()
