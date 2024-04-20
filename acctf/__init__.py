import sys
import traceback
from abc import abstractmethod
from typing import Any

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions
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

    def wait_loading(self, by: str, value: str, has_raised: bool = True):
        try:
            self.wait.until_not(lambda x: x.find_element(by, value))
        except TimeoutException as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists").with_traceback(tb)

    def find_element(self, by: str, value: str, has_raised: bool = True) -> Any:
        try:
            elem = self.wait.until(lambda x: x.find_element(by, value))
        except TimeoutException as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists").with_traceback(tb)
        return elem

    def find_elements(self, by: str, value: str, has_raised: bool = True) -> Any:
        try:
            elem = self.wait.until(lambda x: x.find_elements(by, value))
        except TimeoutException as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists").with_traceback(tb)
        return elem

    def find_element_to_be_clickable(self, by: str, value: str, has_raised: bool = True) -> Any:
        try:
            elem = self.wait.until(expected_conditions.element_to_be_clickable((by, value)))
        except TimeoutException as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise TimeoutException(f"{e}: increase the timeout or check if the element({value}) exists").with_traceback(tb)
        return elem
