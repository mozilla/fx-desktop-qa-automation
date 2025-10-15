import json
import logging
from subprocess import check_output


def test_version(driver, opt_ci, fx_executable):
    """Get the Fx version"""

    version = check_output([fx_executable, "--version"]).decode()
    assert driver.capabilities["browserVersion"] in version
    logging.info(version)
    logging.warning(f"Fx version {driver.capabilities}")
    driver.get("chrome://browser/content/aboutDialog.xhtml")
    ver_label = driver.find_element("id", "version")
    ver_info = json.loads(ver_label.get_attribute("data-l10n-args"))
    assert ver_info.get("version") in version
    if opt_ci:
        with open("artifacts/fx_version", "w") as fh:
            fh.write(version)
