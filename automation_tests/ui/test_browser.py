
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


def test_home_page_in_browser(driver):
    driver.get(BASE_URL)

    assert driver.title == "Automation Dashboard"

    heading = driver.find_element(By.TAG_NAME, "h1")
    assert heading.text == "Python Flask Automation Dashboard"

    assert driver.find_element(
        By.ID, "runButton"
    ).is_displayed()


def test_health_endpoint_in_browser(driver):
    driver.get(f"{BASE_URL}/health")

    assert "healthy" in driver.page_source
