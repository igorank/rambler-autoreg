import os
import time
import random
import traceback

from datetime import datetime
from colorama import init
from colorama import Fore, Style
from multiprocessing import Pool
from settings import token, imap_activate, domaincount, secret_in_log, captcha_service, \
    use_proxy, proxy_type, headless
from passlib.utils import generate_password
from faker import Faker
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (ElementClickInterceptedException, TimeoutException,
                                        NoSuchElementException, ElementNotInteractableException)

fake = Faker('ru_RU')
init()
domains = ['@autorambler.ru', '@myrambler.ru', '@rambler.ru', '@rambler.ua', '@ro.ru']

CAPTCHA_CLICKABLE_TEXT = ["Решить с 2Captcha", "API_CONNECTION_ERROR"]
CAPTCHA_STATUS_MINUS_TEXT = ["Слишком много попыток регистрации. Попробуйте позже.",
                             "API_HTTP_CODE_500", "API_HTTP_CODE_520",
                             "API_HTTP_CODE_521", "Ошибка создания новой учётной записи."
                                                  " Попробуйте повторить через 5 минут.",
                             "ERROR_CAPTCHA_UNSOLVABLE"]


class CaptchaError(Exception):
    pass


def log(message: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


class Browser(webdriver.Chrome):

    def __init__(self, args) -> None:
        super().__init__(seleniumwire_options=self.__get_proxy_options(args),
                         options=self.__get_chrome_options())

    @staticmethod
    def _press_ok(driver):
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        time.sleep(1)
        driver.switch_to.alert.accept()

    @staticmethod
    def _alt_click(driver, element) -> bool:
        for _ in range(3):
            try:
                driver.find_element("xpath",
                                    element).click()
                return True
            except ElementClickInterceptedException:
                time.sleep(2)
        return False

    def __settings_rucaptcha_solver(self, extension_id="ifibfemgeogfhoebkmokieepdoobkbpo"):
        # setup settings for captcha solver
        if len(self.window_handles) >= 2:
            self.close()
            self.switch_to.window(self.window_handles[0])
            self.switch_to.window(self.window_handles[-1])
        self.get(f"chrome-extension://{extension_id}/options/options.html")
        WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//input[@name="apiKey"]')))
        self.find_element("xpath",
                          '//input[@name="apiKey"]').send_keys(token)
        WebDriverWait(self, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="autoSolveHCaptcha"]')))
        self._alt_click(self, '//*[@id="autoSolveHCaptcha"]')
        # driver.find_element("xpath",
        #                     '//*[@id="autoSolveHCaptcha"]').click()
        WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "/html/body/div/div[1]/table/"
                                            "tbody/tr[1]/td[3]/button")))
        self.find_element("xpath", "/html/body/div/div[1]/table/tbody/tr[1]/td[3]/button").click()
        self._press_ok(self)

    def _setup_captcha_solver(self):
        if captcha_service == 1:  # TEMP
            for i in range(5):
                try:
                    self.get('chrome-extension://lncaoejhfdpcafpkkcddpjnhnodcajfg/popup.html')
                    time.sleep(1)
                    self.find_element(By.NAME, 'account_key').clear()
                    time.sleep(1)
                    self.find_element(By.NAME, 'account_key').send_keys(token)
                    time.sleep(1)
                    self.find_element(By.CSS_SELECTOR, '.btn.btn-primary').click()
                    time.sleep(2)
                    break
                except:
                    pass
        elif captcha_service == 2:
            self.__settings_rucaptcha_solver()

    @staticmethod
    def __get_proxy_options(args):

        if use_proxy:
            with open(args, 'r') as f:
                proxy_list = f.read().splitlines()
            proxy = random.choice(proxy_list)
            proxy_options = {
                "proxy": {
                    "https": f"{proxy_type}://{proxy}"
                }
            }
        else:
            proxy_options = {
                "proxy": {
                    "no_proxy": "localhost,127.0.0.1"
                }
            }

        return proxy_options

    @staticmethod
    def __get_chrome_options():

        chrome_options = Options()

        if captcha_service == 1:
            chrome_options.add_extension("./anticaptcha-plugin_v0.63.crx")
        elif captcha_service == 2:
            chrome_options.add_extension("./Captcha-Solver.crx")

        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                    ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"')

        if headless:
            chrome_options.add_argument("--headless=chrome")  # new
            # chrome_options.add_argument('--headless')

        return chrome_options

    def _activate_imap(self, name, domain_text, password, secret) -> None:
        self.get('https://mail.rambler.ru/settings/mailapps/change')

        for _ in range(3):
            if not self.__check_captcha_solver_presence():
                self.refresh()
                continue

            if self._check_captcha_status():
                WebDriverWait(self, 12).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.MailAppsChange-submitWrapper-JZ > button'))).click()

                try:
                    WebDriverWait(self, 8).until(EC.invisibility_of_element_located(
                        (By.XPATH, '//div[@class="rui-Popup-popup MailAppsChange-mailAppPopup-21"]')))
                except TimeoutException:
                    raise CaptchaError("Captcha error")

                log(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP '
                    + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Fore.BLUE)
                time.sleep(3)
                return
            else:
                self.refresh()
                continue

        raise CaptchaError("Captcha error")

    def __check_captcha_solver_presence(self) -> bool:
        try:
            WebDriverWait(self, 12).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="captcha-solver captcha-solver_inner"]')))
            return True
        except (ElementNotInteractableException,
                NoSuchElementException, TimeoutException):
            return False

    def _check_captcha(self, timeout=65) -> int:
        for _ in range(timeout):
            try:
                captcha_solver = self.find_element(By.CLASS_NAME, 'captcha-solver-info')
                captcha_solver_text = captcha_solver.text

                if captcha_solver_text in CAPTCHA_CLICKABLE_TEXT:
                    captcha_solver.click()
                elif captcha_solver_text == "Капча решена!":
                    return 1
                elif captcha_solver_text == "ERROR_SITEKEY":
                    return 0
                elif any(ele in captcha_solver_text for ele in CAPTCHA_STATUS_MINUS_TEXT):
                    return 0  # default 0
            except NoSuchElementException:
                pass
            time.sleep(1)
        return -1

    def _check_captcha_status(self) -> bool:
        captcha_status = self._check_captcha()
        if captcha_status == 1:
            return True
        else:
            return False

    def run(self, name, domain_text, password, secret) -> None:

        self._setup_captcha_solver()

        self.get('https://id.rambler.ru/login-20/mail-registration')

        for _ in range(3):
            WebDriverWait(self, 16).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@autocomplete="username"]')))

            if domaincount != 3:
                self.find_element(By.XPATH, '//*[@class="rui-Tooltip-anchor"]').click()
                WebDriverWait(self, 6).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({domaincount})'))).click()

            try:
                element = WebDriverWait(self, 6).until(EC.presence_of_element_located((By.XPATH,
                                                                                       '//input['
                                                                                       '@class="rui-RadioButton-real" '
                                                                                       'and @value="question"]')))
                self.execute_script("arguments[0].click();", element)
            except TimeoutException:
                pass

            WebDriverWait(self, 5).until(EC.element_to_be_clickable(  # selenium.common.exceptions.TimeoutException
                (By.XPATH, '//*[@theme="[object Object]"][4]'))).click()

            self.execute_script("arguments[0].click();", WebDriverWait(self, 6).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child(1)'))))

            WebDriverWait(self, 6).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::mailbox_name"]'))).send_keys(
                name + Keys.TAB + Keys.TAB + password + Keys.TAB + password)

            WebDriverWait(self, 6).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::answer"]'))).send_keys(secret)

            if not self.__check_captcha_solver_presence():
                self.refresh()
                continue

            if self._check_captcha_status():
                try:
                    WebDriverWait(self, 12).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@data-cerber-id="login_form::main::login_button"]'))).click()
                except TimeoutException:
                    raise CaptchaError("Captcha error")

                if secret_in_log:
                    secret = f':{secret}'
                else:
                    secret = ''

                try:
                    WebDriverWait(self, 7).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@data-cerber-id='
                                                                  '"registration_form::step_2::add_later"]'))).click()
                except TimeoutException:  # Пройдите верификацию, пожалуйста
                    raise CaptchaError("Captcha error")

                if imap_activate:
                    self._activate_imap(name, domain_text, password, secret)
                else:
                    log(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret}'
                        + Style.RESET_ALL + Fore.BLUE)

                with open('result.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{name}{domain_text}:{password}{secret}\n")

                return
            else:
                self.refresh()
                continue

        raise CaptchaError("Captcha error")


def main(args):
    data = {'domain_text': domains[domaincount - 1], 'password': generate_password(28),
            'name': generate_password(16), 'secret': generate_password(8)}

    browser = Browser(args)

    try:
        browser.run(data['name'], data['domain_text'], data['password'], data['secret'])
    except CaptchaError as cap_error:
        log(Style.RESET_ALL + Fore.RED + str(cap_error) + Style.RESET_ALL + Fore.BLUE)
    except Exception as ex:
        log(Style.RESET_ALL + Fore.RED + f'Unidentified error: {ex.__class__.__name__}' + Style.RESET_ALL + Fore.BLUE)
        # print(str(traceback.format_exc()))  # DEBUG
    finally:
        browser.close()
        browser.quit()


if __name__ == '__main__':
    text = (Fore.BLUE + '''
██████╗░░█████╗░███╗░░░███╗██████╗░██╗░░░░░███████╗██████╗░
██╔══██╗██╔══██╗████╗░████║██╔══██╗██║░░░░░██╔════╝██╔══██╗
██████╔╝███████║██╔████╔██║██████╦╝██║░░░░░█████╗░░██████╔╝
██╔══██╗██╔══██║██║╚██╔╝██║██╔══██╗██║░░░░░██╔══╝░░██╔══██╗
██║░░██║██║░░██║██║░╚═╝░██║██████╦╝███████╗███████╗██║░░██║
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═════╝░╚══════╝╚══════╝╚═╝░░╚═╝

    ██████╗░███████╗░██████╗░███████╗██████╗░
    ██╔══██╗██╔════╝██╔════╝░██╔════╝██╔══██╗
    ██████╔╝█████╗░░██║░░██╗░█████╗░░██████╔╝
    ██╔══██╗██╔══╝░░██║░░╚██╗██╔══╝░░██╔══██╗
    ██║░░██║███████╗╚██████╔╝███████╗██║░░██║
    ╚═╝░░╚═╝╚══════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
    '''
            + Style.RESET_ALL)
    os.system('cls')
    print(text)

    threading = int(input(Style.RESET_ALL + Fore.BLUE + 'Threading: ' + Style.BRIGHT))

    if use_proxy:
        proxypath = input(Style.RESET_ALL + Fore.BLUE + 'Path to proxy: ' + Style.BRIGHT)
        if not os.path.exists(proxypath):
            print(Style.RESET_ALL + Fore.RED + 'Proxy path not found')
            input()
            exit()
        else:
            a = [proxypath] * 9999999
    else:
        a = ['a'] * 9999999

    p = Pool(processes=threading)
    p.map(main, a)
    input(Fore.BLUE + "Press enter to exit......" + Style.RESET_ALL)
    exit()
