import multiprocessing
import os
from pathlib import Path
import random
import subprocess
from contextlib import contextmanager
import sys
import tempfile
import concurrent.futures
import time


def main():
    # print(install_some_things(0))
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        results = executor.map(install_some_things, range(20))

        for result in results:
            print(result)


def install_some_things(job_i):
    with venv() as env:
        subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "pip==10.0.1",
                ],
                check=True,
                env=env,
            )
        for _ in range(10):
            time.sleep(random.random() * 0.1)
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "setuptools",
                    "wheel",
                ],
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
                ],
                check=True,
                env=env,
            )
    return f'job {job_i} done'


@contextmanager
def venv():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        subprocess.run(
            [
                sys.executable,
                "-m",
                "venv",
                tmp_path,
            ]
        )

        env = os.environ.copy()
        env["PATH"] = f"{tmp_path}/bin:{env['PATH']}"
        env["PIP_CACHE_DIR"] = f"./pip-cache"

        active_python = subprocess.run(
            ["python", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            env=env,
        ).stdout.strip()

        assert Path(active_python).resolve() == Path(f"{tmp_path}/bin/python").resolve()

        yield env


if __name__ == "__main__":
    main()
