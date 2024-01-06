from enum import Enum

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


class Element(Enum):
    ByName = By.NAME
    ByID = By.ID
    ByTagName = By.TAG_NAME
    ByClassName = By.CLASS_NAME
    ByXpath = By.XPATH


class BrowserController:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def login(
            self,
            url,
            elem_type: Element,
            id_val: str,
            password_val: str,
            login_button_val: str,
            user_id: str,
            user_password: str,
    ) -> None:
        self.driver.get(url)
        user_id_elem = self.driver.find_element(elem_type, id_val)
        user_id_elem.send_keys(user_id)
        user_pw_elem = self.driver.find_element(elem_type, password_val)
        user_pw_elem.send_keys(user_password)

        self.driver.find_element(elem_type, login_button_val).click()

    def move(self, elem_type: Element, elem_val: str) -> None:
        self.driver.find_element(elem_type, elem_val).click()
