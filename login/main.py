from enum import Enum

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


class Element(Enum):
    ByName = By.NAME
    ByID = By.ID
    ByTagName = By.TAG_NAME
    ByClassName = By.CLASS_NAME
    ByXpath = By.XPATH


class Login:
    def __init__(self, driver: WebDriver, url: str):
        self.driver = driver
        self.url = url

    def login(
            self,
            elem_type: Element,
            id_val: str,
            password_val: str,
            login_button_val: str,
            user_id: str,
            user_password: str,
    ) -> WebDriver:
        self.driver.get(self.url)
        user_id_elem = self.driver.find_element(elem_type, id_val)
        user_id_elem.send_keys(user_id)
        user_pw_elem = self.driver.find_element(elem_type, password_val)
        user_pw_elem.send_keys(user_password)

        self.driver.find_element(elem_type, login_button_val).click()

        return self.driver
