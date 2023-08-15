import os
import time
import random

from colorama import init
from colorama import Fore, Style
from multiprocessing import Pool
from settings import token, imap_activate, domaincount, secret_in_log, captcha_service, \
    use_proxy, proxy_type
from passlib.utils import generate_password
from faker import Faker
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

fake = Faker('ru_RU')
init()
domains = ['@autorambler.ru', '@myrambler.ru', '@rambler.ru', '@rambler.ua', '@ro.ru']


class CaptchaError(Exception):
    pass


class Browser(webdriver.Chrome):

    def __init__(self) -> None:
        super().__init__(seleniumwire_options=self.__get_proxy_options(),
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
                                            "/html/body/div/div[1]/table/tbody/tr[1]/td[2]/input")))
        self.find_element("xpath",
                          "/html/body/div/div[1]/table/tbody/tr[1]/td[2]/input").send_keys(
            token)
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
    def __get_proxy_options():

        if use_proxy:
            with open("proxy.txt", 'r') as f:
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
        return chrome_options

    def _activate_imap(self, name, domain_text, password, secret) -> None:
        try:
            self.get('https://mail.rambler.ru/settings/mailapps/change')
            WebDriverWait(self, 60).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.MailAppsChange-submitWrapper-JZ > button'))).click()
            print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP '
                  + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Fore.BLUE)
        except:
            print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP '
                  + Fore.RED + 'FAIL' + Style.RESET_ALL + Fore.BLUE)

    def run(self, name, domain_text, password, secret) -> str:

        self._setup_captcha_solver()

        self.get('https://id.rambler.ru/login-20/mail-registration')
        WebDriverWait(self, 16).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@autocomplete="username"]')))

        if domaincount != 3:
            self.find_element(By.XPATH, '//*[@class="rui-Tooltip-anchor"]').click()
            WebDriverWait(self, 6).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({domaincount})'))).click()

        WebDriverWait(self, 6).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@theme="[object Object]"][4]'))).click()
        WebDriverWait(self, 6).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child(1)'))).click()

        WebDriverWait(self, 6).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::mailbox_name"]'))).send_keys(
            name + Keys.TAB + Keys.TAB + password + Keys.TAB + password)

        WebDriverWait(self, 6).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::answer"]'))).send_keys(secret)
        try:
            WebDriverWait(self, 75).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@data-cerber-id="login_form::main::login_button"]'))).click()  # TEMP
        except TimeoutException:
            raise CaptchaError("Captcha error")

        if secret_in_log:
            secret = f':{secret}'
        else:
            secret = ''

        WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@data-cerber-id="registration_form::step_2::add_later"]'))).click()

        if imap_activate:
            self._activate_imap(name, domain_text, password, secret)
        else:
            print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret}' + Style.RESET_ALL + Fore.BLUE)

        return secret


def main(args):
    try:
        num = 1
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
        domain_text = domains[domaincount - 1]
        time.sleep(random.randint(1, 15))
        password = generate_password(28)
        name = generate_password(16)
        secret = generate_password(8)
        chrome_options = Options()
        if captcha_service == 1:
            chrome_options.add_extension("./anticaptcha-plugin_v0.63.crx")
        elif captcha_service == 2:
            chrome_options.add_extension("./Captcha-Solver.crx")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(seleniumwire_options=proxy_options, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        if captcha_service == 1:
            for i in range(5):
                try:
                    driver.get('chrome-extension://lncaoejhfdpcafpkkcddpjnhnodcajfg/popup.html')
                    time.sleep(1)
                    driver.find_element(By.NAME, 'account_key').clear()
                    time.sleep(1)
                    driver.find_element(By.NAME, 'account_key').send_keys(token)
                    time.sleep(1)
                    driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary').click()
                    time.sleep(2)
                    break
                except:
                    pass
        elif captcha_service == 2:
            for i in range(5):
                try:
                    driver.get('chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html')
                    time.sleep(1)
                    wait.until(presence_of_element_located((By.NAME, 'autoSolveHCaptcha'))).click()
                    time.sleep(1)
                    driver.find_element(By.NAME, 'apiKey').clear()
                    time.sleep(1)
                    driver.find_element(By.NAME, 'apiKey').send_keys(token)
                    driver.find_element(By.ID, 'connect').click()
                    time.sleep(1)
                    driver.switch_to.alert.accept()
                    time.sleep(2)
                    break
                except:
                    pass
        num = 2
        for i in range(5):
            try:
                driver.get('https://id.rambler.ru/login-20/mail-registration')
                wait.until(presence_of_element_located((By.XPATH, '//*[@autocomplete="username"]')))
                break
            except:
                pass

        time.sleep(2)
        num = 2.5
        for i in range(5):
            try:
                if domaincount != 3:
                    driver.find_element(By.XPATH, '//*[@class="rui-Tooltip-anchor"]').click()
                    time.sleep(2)
                    driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({domaincount})').click()
                    time.sleep(3)
                    break
            except:
                pass
        num = 3
        for i in range(5):
            try:
                driver.find_element(By.XPATH, '//*[@theme="[object Object]"][4]').click()
                time.sleep(2)
                num = 4
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child(1)').click()
                time.sleep(1)
                break
            except:
                pass
        num = 5
        driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::mailbox_name"]').send_keys(
            name + Keys.TAB + Keys.TAB + password + Keys.TAB + password)
        time.sleep(2)
        num = 6
        driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_1::answer"]').send_keys(
            secret)
        butttton_complete = WebDriverWait(driver, 75).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@data-cerber-id="login_form::main::login_button"]')))
        time.sleep(1)
        butttton_complete.click()
        if secret_in_log:
            secret = f':{secret}'
        else:
            secret = ''
        if fill_personal_information:
            try:
                gender = random.randint(1, 2)
                if gender == 1:
                    bioname = fake.first_name_female()
                    biosurname = fake.last_name_female()
                else:
                    bioname = fake.first_name_male()
                    biosurname = fake.last_name_male()
                biocity = fake.city_name()
                wait.until(presence_of_element_located(
                    (By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]')))
                driver.find_element(By.ID, 'firstname').send_keys(bioname + Keys.TAB + biosurname)
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_2::gender"]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({gender})').click()
                driver.find_element(By.ID, 'birthday').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({random.randint(1, 25)})').click()
                driver.find_element(By.XPATH,
                                    '//*[@class="rui-FormGroup-medium rui-FormGroup-normal rui-FormGroup-root"]/div/div/div/div[2]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({random.randint(1, 12)})').click()
                driver.find_element(By.XPATH,
                                    '//*[@class="rui-FormGroup-medium rui-FormGroup-normal rui-FormGroup-root"]/div/div/div/div[3]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR,
                                    f'.rui-Menu-content > :nth-child({random.randint(15, 30)})').click()
                time.sleep(1)
                driver.find_element(By.ID, 'geoid').send_keys(biocity)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, '.rui-Menu-content > :nth-child(1)'))).click()
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::step_2::registration"]').click()
            except:
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]').click()
        else:
            wait.until(presence_of_element_located(
                (By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]'))).click()
        time.sleep(1)
        with open('result.txt', 'a', encoding='utf-8') as file:
            file.write(f'{name}{domain_text}:{password}{secret}\n')
        if imap_activate:
            for attempt in range(1, 4):
                try:
                    driver.get('https://mail.rambler.ru/settings/mailapps/change')
                    if attempt == 1:
                        driver.refresh()
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '.MailAppsChange-submitWrapper-JZ > button'))).click()
                    time.sleep(1)
                    print(
                        Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP ' + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Fore.BLUE)
                    break
                except:
                    print(
                        Style.RESET_ALL + Fore.RED + f'Error imap activate [{attempt} attempt]' + Style.RESET_ALL + Fore.BLUE)
                    if attempt == 3:
                        print(
                            Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP ' + Fore.RED + 'FAIL' + Style.RESET_ALL + Fore.BLUE)
                        break
        else:
            print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret}' + Style.RESET_ALL + Fore.BLUE)

    except:
        if num == 6:
            print(Style.RESET_ALL + Fore.RED + f'Captcha error' + Style.RESET_ALL + Fore.BLUE)
        else:
            print(Style.RESET_ALL + Fore.RED + f'Unidentified error' + Style.RESET_ALL + Fore.BLUE)
    finally:
        driver.close()
        driver.quit()


# if __name__ == '__main__':
#     text = (Fore.BLUE + '''
# ██████╗░░█████╗░███╗░░░███╗██████╗░██╗░░░░░███████╗██████╗░
# ██╔══██╗██╔══██╗████╗░████║██╔══██╗██║░░░░░██╔════╝██╔══██╗
# ██████╔╝███████║██╔████╔██║██████╦╝██║░░░░░█████╗░░██████╔╝
# ██╔══██╗██╔══██║██║╚██╔╝██║██╔══██╗██║░░░░░██╔══╝░░██╔══██╗
# ██║░░██║██║░░██║██║░╚═╝░██║██████╦╝███████╗███████╗██║░░██║
# ╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═════╝░╚══════╝╚══════╝╚═╝░░╚═╝
#
#     ██████╗░███████╗░██████╗░███████╗██████╗░
#     ██╔══██╗██╔════╝██╔════╝░██╔════╝██╔══██╗
#     ██████╔╝█████╗░░██║░░██╗░█████╗░░██████╔╝
#     ██╔══██╗██╔══╝░░██║░░╚██╗██╔══╝░░██╔══██╗
#     ██║░░██║███████╗╚██████╔╝███████╗██║░░██║
#     ╚═╝░░╚═╝╚══════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
#     '''
#             + Style.RESET_ALL)
#     os.system('cls')
#     print(text)
#
#     threading = int(input(Style.RESET_ALL + Fore.BLUE + 'Threading: ' + Style.BRIGHT))
#
#     if use_proxy:
#         proxypath = input(Style.RESET_ALL + Fore.BLUE + 'Path to proxy: ' + Style.BRIGHT)
#         if not os.path.exists(proxypath):
#             print(Style.RESET_ALL + Fore.RED + 'Proxy path not found')
#             input()
#             exit()
#         else:
#             a = [proxypath] * 9999999
#     else:
#         a = ['a'] * 9999999
#
#     p = Pool(processes=threading)
#     p.map(main, a)
#     input(Fore.BLUE + "Press enter to exit......" + Style.RESET_ALL)
#     exit()

def main2():
    data = {'domain_text': domains[domaincount - 1], 'password': generate_password(28),
            'name': generate_password(16), 'secret': generate_password(8)}

    browser = Browser()

    try:
        secret = browser.run(data['name'], data['domain_text'], data['password'], data['secret'])
    except CaptchaError as cap_error:
        print(Style.RESET_ALL + Fore.RED + str(cap_error) + Style.RESET_ALL + Fore.BLUE)
    except Exception as ex:
        print(Style.RESET_ALL + Fore.RED + f'Unidentified error: {ex}' + Style.RESET_ALL + Fore.BLUE)
    finally:
        browser.close()
        browser.quit()

    with open('result.txt', 'a', encoding='utf-8') as file:
        file.write(f"{data['name']}{data['domain_text']}:{data['password']}{secret}\n")


if __name__ == '__main__':
    main2()
