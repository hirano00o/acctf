from abc import abstractmethod

from selenium import webdriver

class Base:
    driver: webdriver

    def __init__(self, driver: webdriver):
        self.driver = driver
        self.driver.implicitly_wait(10)

    @abstractmethod
    def login(self, user_id: str, password: str, totp: str | None = None):
        raise NotImplementedError()

    @abstractmethod
    def logout(self):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()
