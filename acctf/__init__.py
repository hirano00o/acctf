from abc import abstractmethod
from typing import Any

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


class Base:
    driver: webdriver
    wait: WebDriverWait

    def __init__(self, driver: webdriver, timeout: float = 30):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=timeout)

    @abstractmethod
    def login(self, user_id: str, password: str, totp: str | None = None):
        raise NotImplementedError()

    @abstractmethod
    def logout(self):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()

    def find_element(self, by: str, value: str, has_raised: bool = True) -> Any:
        try:
            elem = self.wait.until(lambda x: x.find_element(by, value))
        except TimeoutException as e:
            if not has_raised:
                return None
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists")
        return elem

    def find_elements(self, by: str, value: str, has_raised: bool = True) -> Any:
        try:
            elem = self.wait.until(lambda x: x.find_elements(by, value))
        except TimeoutException as e:
            if not has_raised:
                return None
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists")
        return elem
