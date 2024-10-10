import pytest
import time
from selenium.webdriver import Firefox
@pytest.fixture()
def test_case():
    return "C2245178"
def test_primary_password_setup(driver: Firefox):
    """
    C2245178 - Primary Password Setup
    """
    driver.get("about:preferences#privacy")
    time.sleep(2)
    assert driver.execute_script("""
        const checkbox = document.querySelector('#useMasterPassword');
        if (checkbox && !checkbox.checked) {
            checkbox.click();
            return true;
        }
        return checkbox ? checkbox.checked : false;
    """), "Failed to click checkbox"
    
    time.sleep(2)
    password_data = {
        "primary_password": "TestPassword123",
        "confirm_password": "TestPassword123"
    }
    
    assert driver.execute_script(f"""
        return new Promise(resolve => {{
            const doc = document.querySelector('browser.dialogFrame').contentDocument;
            const pw1 = doc.querySelector('input#pw1');
            const pw2 = doc.querySelector('input#pw2');
            if (!pw1 || !pw2) return resolve(false);
            pw1.value = "{password_data['primary_password']}";
            pw2.value = "{password_data['confirm_password']}";
            [pw1, pw2].forEach(i => i.dispatchEvent(new Event('input', {{bubbles: true}})));
            setTimeout(() => {{
                const okButton = doc.querySelector('dialog#changemp')?.shadowRoot
                    ?.querySelector('button[dlgtype="accept"][label="OK"]');
                okButton ? (okButton.click(), resolve(true)) : resolve(false);
            }}, 1000);
        }});
    """), "Failed to set password"
    time.sleep(2)
    
    # Try to handle the alert
    driver.switch_to.alert.accept()
    time.sleep(2)
    assert driver.execute_script("""
        return document.querySelector('#useMasterPassword')?.checked;
    """), "Verification failed"
    driver.quit()