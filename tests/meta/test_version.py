import logging
from subprocess import check_output


def test_version(opt_ci, fx_executable):
    """Get the Fx version"""

    version = check_output([fx_executable, "--version"]).decode()
    logging.info(version)
    if opt_ci:
        with open("artifacts/fx_version", "w") as fh:
            fh.write(version)
