import pytest

NOTIFICATION_LISTENER_SCRIPT = """
    window.notifications = [];

    Notification.requestPermission().then(function(permission) {
        if (permission === "granted") {
            const OriginalNotification = window.Notification;
            window.Notification = function(title, options) {
                // Store notifications in an array
                window.notifications.push({title: title, body: options.body});
                return new OriginalNotification(title, options);
            };
        }
    });
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
