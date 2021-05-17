import logging

import math
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Driver(WebDriver):
    logger = logging.getLogger(__name__)

    def __init__(self, executable_path="chromedriver", port=0, options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None, chrome_options=None, keep_alive=True):
        super().__init__(executable_path, port, options, service_args, desired_capabilities, service_log_path,
                         chrome_options, keep_alive)

    def wait_at_least_n_seconds_for(self, seconds: int, selector: str):
        """
        Дожидается заданное количество секунд до появления на странице
        некоторого элемента, который удовлетворяет селектору.

        Если элемент появился раньше, то засыпает на оставшееся время.
        """
        start = time.time()
        try:
            WebDriverWait(self, seconds).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException as e:
            self.logger.error(f'не нашел "{selector}" за {seconds} секунд [{self.current_url}]')
            raise e

        time_passed = time.time() - start
        time_to_sleep = math.ceil(seconds - time_passed)
        self.logger.debug(f'нашел "{selector}" за {time_passed:1.2} секунд')
        if time_to_sleep > 0:
            self.logger.debug(f"засыпает на {time_to_sleep}")
            time.sleep(time_to_sleep)

    def wait_n_seconds_for(self, seconds: int, selector: str):
        """
        Дожидается заданное количество секунд до появления на странице
        некоторого элемента, который удовлетворяет селектору.
        """
        try:
            WebDriverWait(self, seconds).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException as e:
            self.logger.error(f'не нашел "{selector} [{self.current_url}]')
            raise e

    def get_in_new_tab(self, url: str):
        """Открывает ссылку в новой вкладке и переключается на нее."""
        self.execute_script(f"window.open('{url}')")
        new_tab = self.window_handles[-1]
        self.switch_to.window(new_tab)

    def close_last_tab(self):
        """Закрывает последнюю вкладку, переключается на предыдущую."""
        self.close()
        previous_tab = self.window_handles[-1]
        self.switch_to.window(previous_tab)
