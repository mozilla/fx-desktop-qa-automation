import pytest

NOTIFICATION_LISTENER_SCRIPT = """
    const OldNotify = window.Notification;
    const newNotify = (title, opt) => {
        window.localStorage.setItem("newestNotificationTitle", title);
        return new OldNotify(title, opt);
    };
    newNotify.requestPermission = OldNotify.requestPermission.bind(OldNotify);
    Object.defineProperty(newNotify, 'permission', {
        get: () => {
            return OldNotify.permission;
        }
    });

    window.Notification = newNotify;
"""


@pytest.fixture()
def suite_id():
    return ("1907", "Notifications, Push Notifications and Alerts")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


@pytest.fixture()
def start_notification_listener(driver):
    def _listener():
        driver.execute_script(NOTIFICATION_LISTENER_SCRIPT)

    return _listener
