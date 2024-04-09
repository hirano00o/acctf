from abc import abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

class Base:
    driver: WebDriver

    def __init__(self, executable_path: str=None):
        options = Options()
        options.add_argument('--headless')
        service = Service(executable_path=executable_path)
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.implicitly_wait(10)

    @abstractmethod
    def login(self, user_id: str, password: str, totp: str | None = None):
        raise NotImplementedError()

    @abstractmethod
    def logout(self):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()
