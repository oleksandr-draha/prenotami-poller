from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdrivermanager.chrome import ChromeDriverManager


URL = "https://prenotami.esteri.it/"
LOGIN = ""
PASSWORD = ""
SERVICES_URL = "https://prenotami.esteri.it/Services"
BOOK_NUMBER = 4
CHECK_TIMEOUT = 2

LOGIN_LOCATOR = (By.ID, "login-email")
PASSWORD_LOCATOR = (By.ID, "login-password")
BOOK_LOCATOR = (By.XPATH, "//a[contains(@href,'/Services/Booking/')]")
NOT_AVAILABLE_LOCATOR = (By.XPATH, "//*[contains(text(),'Al momento non ci sono date disponibili per il servizio richiesto')]")
PRIVACY_CHECK_BOX_LOCATOR = (By.XPATH, "//input[@type='checkbox']")
FORWARD_BUTTON_LOCATOR = (By.ID, "btnAvanti")
OK_POPUP_LOCATOR = (By.ID, "//*[contains(text(),'OK')]")


# Setup Chrome
ChromeDriverManager().download_and_install()
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
driver = webdriver.Chrome(desired_capabilities=caps)
driver.implicitly_wait(10)


# Login to portal
driver.get(URL)
driver.find_element(*LOGIN_LOCATOR).send_keys(LOGIN)
driver.find_element(*PASSWORD_LOCATOR).send_keys(PASSWORD)
driver.find_element(*PASSWORD_LOCATOR).submit()


# Extract service link
driver.get(SERVICES_URL)
service = driver.find_elements(*BOOK_LOCATOR)[BOOK_NUMBER - 1]
service_link = service.get_attribute("href")


# Reduce timeout for waiting of elements on page
driver.implicitly_wait(CHECK_TIMEOUT)


def check_availability():
    privacy_checkbox = driver.find_elements(*PRIVACY_CHECK_BOX_LOCATOR)
    if len(privacy_checkbox):
        # If check box is present - then click it
        privacy_checkbox[0].click()
        # And click FORWARD button
        driver.find_element(*FORWARD_BUTTON_LOCATOR).click()
        return True


# Constantly polling for dates available
while not check_availability():
    driver.get(service_link)

driver.find_element(OK_POPUP_LOCATOR)

