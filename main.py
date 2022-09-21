import sys

from selenium import webdriver
from selenium.common import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://prenotami.esteri.it/"
LOGIN = ""
PASSWORD = ""
SERVICES_URL = "https://prenotami.esteri.it/Services"
BOOK_NUMBER = 0
CHECK_TIMEOUT = 2

if not LOGIN:
    try:
        LOGIN = sys.argv[1]
    except IndexError:
        LOGIN = input("User email: ")

if not PASSWORD:
    try:
        PASSWORD = sys.argv[2]
    except IndexError:
        PASSWORD = input("User password: ")

if not BOOK_NUMBER:
    try:
        BOOK_NUMBER = int(sys.argv[3])
    except IndexError:
        BOOK_NUMBER = int(input("Number of service to book: "))

LOGIN_LOCATOR = (By.ID, "login-email")
PASSWORD_LOCATOR = (By.ID, "login-password")
BOOK_LOCATOR = (By.XPATH, "//a[contains(@href,'/Services/Booking/')]")
NOT_AVAILABLE_LOCATOR = (By.XPATH, "//*[contains(text(),'Al momento non ci sono date disponibili per il servizio richiesto')]")
PRIVACY_CHECK_BOX_LOCATOR = (By.XPATH, "//input[@type='checkbox']")
FORWARD_BUTTON_LOCATOR = (By.ID, "btnAvanti")
OK_POPUP_LOCATOR = (By.ID, "//*[contains(text(),'OK')]")
AVAILABLE_DAY = (By.XPATH, "//td[@class='day availableDay']")
SUBMIT_BUTTON = (By.ID, "btnPrenotaNoOtp")


# Setup Chrome
service = ChromeDriverManager().install()
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
driver = webdriver.Chrome(service, desired_capabilities=caps)
driver.implicitly_wait(10)


# Login to portal
print("Getting portal")
driver.get(URL)
print("Logging with provided credentials")
driver.find_element(*LOGIN_LOCATOR).send_keys(LOGIN)
driver.find_element(*PASSWORD_LOCATOR).send_keys(PASSWORD)
driver.find_element(*PASSWORD_LOCATOR).submit()


# Extract service link
print("Getting services list")
driver.get(SERVICES_URL)
service = driver.find_elements(*BOOK_LOCATOR)[BOOK_NUMBER - 1]
service_link = service.get_attribute("href")


# Reduce timeout for waiting of elements on page
driver.implicitly_wait(CHECK_TIMEOUT)


def check_availability():
    privacy_checkbox = driver.find_elements(*PRIVACY_CHECK_BOX_LOCATOR)
    if len(privacy_checkbox):
        # If check box is present - then click it
        print("Service is available for booking. Trying to book it")
        privacy_checkbox[0].click()
        # And click FORWARD button
        driver.find_element(*FORWARD_BUTTON_LOCATOR).click()
        return True


# Constantly polling for dates available
print("Starting to wait for dates available")
while not check_availability():
    driver.get(service_link)


def wait_for_alert():
    try:
        driver.switch_to.alert.accept()
        driver.switch_to.default_content()
        return True
    except NoAlertPresentException:
        return False


# Waiting for alert to appear
print("Waiting for confirmation shown")
while not wait_for_alert():
    pass


# Selecting first available day and submit
print("Selecting first available day")
driver.find_element(*AVAILABLE_DAY).click()
print("Confirming booking")
driver.find_element(*SUBMIT_BUTTON).click()

print("Booking was finished")
input("Press Enter when finished")
