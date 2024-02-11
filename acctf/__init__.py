from abc import abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

class Base:
    driver: WebDriver

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    @abstractmethod
    def login(self, user_id: str, password: str, otp: str | None = None):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()
