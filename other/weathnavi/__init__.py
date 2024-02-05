from selenium.webdriver.common.by import By

from base import Base


class WealthNavi(Base):
    def __init__(self):
        super().__init__()
        self.driver.get('https://invest.wealthnavi.com/login')

    def login(self, user_id: str, password: str, otp: str | None = None):
        user_id_elem = self.driver.find_element(By.ID, 'username')
        user_id_elem.send_keys(user_id)

        user_pw_elem = self.driver.find_element(By.ID, 'password')
        user_pw_elem.send_keys(password)

        self.driver.find_element(By.ID, 'login').click()

        if otp is not None:
            otp_elem = self.driver.find_element(By.ID, 'code')
            otp_elem.send_keys(otp)

            self.driver.find_element(By.ID, 'authentication-code-login').click()

        return self
