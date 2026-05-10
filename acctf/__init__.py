import sys
import traceback
from abc import abstractmethod
from typing import Any

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class Base:
    page: Page
    timeout: int

    def __init__(self, page: Page, timeout: int = 30000):
        self.page = page
        self.timeout = timeout

    @abstractmethod
    def login(self, user_id: str, password: str, totp: str | None = None):
        raise NotImplementedError()

    @abstractmethod
    def logout(self):
        raise NotImplementedError()

    def close(self):
        # Page lifecycle is managed by the caller. Kept for backward compatibility.
        pass

    def wait_loading(self, selector: str, has_raised: bool = True) -> None:
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise PlaywrightTimeoutError(
                f"{e}: increase the timeout or check if the element({selector}) exists"
            ).with_traceback(tb)

    def find_element(self, selector: str, has_raised: bool = True) -> Any:
        loc = self.page.locator(selector).first
        try:
            loc.wait_for(state="visible", timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise PlaywrightTimeoutError(
                f"{e}: increase the timeout or check if the element({selector}) exists"
            ).with_traceback(tb)
        return loc

    def find_elements(self, selector: str, has_raised: bool = True) -> Any:
        loc = self.page.locator(selector)
        try:
            loc.first.wait_for(state="visible", timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            if not has_raised:
                return None
            tb = sys.exc_info()[2]
            traceback.print_exc()
            raise PlaywrightTimeoutError(
                f"{e}: increase the timeout or check if the element({selector}) exists"
            ).with_traceback(tb)
        return loc

    def find_element_to_be_clickable(self, selector: str, has_raised: bool = True) -> Any:
        # Playwright auto-waits for actionability on click(), so visibility is sufficient here.
        return self.find_element(selector, has_raised=has_raised)
