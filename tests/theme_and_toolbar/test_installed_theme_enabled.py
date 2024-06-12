from time import sleep

from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AmoThemes


def test_find_more_themes(driver: Firefox):
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    about_addons.get_element("find-more-themes-button").click()
    driver.switch_to.window(driver.window_handles[-1])

    # Continuing to call the object "about_addons" is confusing
    base = about_addons
    base.url_contains("addons.mozilla.org")
    base.url_contains("firefox/themes")


def test_installed_theme_enabled(driver: Firefox):
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    starting_theme = about_addons.get_element("enabled-theme-title").get_attribute(
        "innerText"
    )
    amo = AmoThemes(driver).open()
    amo.install_recommended_theme()
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # NOTE: AMO does not enforce that the listed theme name remains the same after installation
    about_addons.check_theme_has_changed(starting_theme)
