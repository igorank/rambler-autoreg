import os
from colorama import init
from colorama import Fore, Back, Style
import ctypes
from multiprocessing import Pool
import time
from settings import token,imap_activate,fill_personal_information,domaincount,secret_in_log,captcha_service,use_proxy,proxy_type
from passlib.utils import generate_password
from faker import Faker
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support import expected_conditions as EC
import random


fake = Faker('ru_RU')
init()
domains = ['@autorambler.ru', '@myrambler.ru', '@rambler.ru', '@rambler.ua', '@ro.ru']


def startmain(args):
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
        driver = webdriver.Chrome(seleniumwire_options=proxy_options,options=chrome_options)
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
        driver.find_element(By.XPATH,'//*[@data-cerber-id="registration_form::mail::step_1::mailbox_name"]').send_keys(name + Keys.TAB + Keys.TAB + password + Keys.TAB + password)
        time.sleep(2)
        num = 6
        driver.find_element(By.XPATH,'//*[@data-cerber-id="registration_form::mail::step_1::answer"]').send_keys(secret)
        butttton_complete = WebDriverWait(driver, 75).until(EC.element_to_be_clickable((By.XPATH,'//*[@data-cerber-id="login_form::main::login_button"]')))
        time.sleep(1)
        butttton_complete.click()
        if secret_in_log:
            secret = f':{secret}'
        else:
            secret = ''
        if fill_personal_information:
            try:
                gender = random.randint(1,2)
                if gender == 1:
                    bioname = fake.first_name_female()
                    biosurname = fake.last_name_female()
                else:
                    bioname = fake.first_name_male()
                    biosurname = fake.last_name_male()
                biocity = fake.city_name()
                wait.until(presence_of_element_located((By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]')))
                driver.find_element(By.ID, 'firstname').send_keys(bioname + Keys.TAB + biosurname)
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::mail::step_2::gender"]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({gender})').click()
                driver.find_element(By.ID, 'birthday').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({random.randint(1, 25)})').click()
                driver.find_element(By.XPATH, '//*[@class="rui-FormGroup-medium rui-FormGroup-normal rui-FormGroup-root"]/div/div/div/div[2]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({random.randint(1, 12)})').click()
                driver.find_element(By.XPATH, '//*[@class="rui-FormGroup-medium rui-FormGroup-normal rui-FormGroup-root"]/div/div/div/div[3]').click()
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, f'.rui-Menu-content > :nth-child({random.randint(15, 30)})').click()
                time.sleep(1)
                driver.find_element(By.ID, 'geoid').send_keys(biocity)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, '.rui-Menu-content > :nth-child(1)'))).click()
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::step_2::registration"]').click()
            except:
                driver.find_element(By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]').click()
        else:
            wait.until(presence_of_element_located((By.XPATH, '//*[@data-cerber-id="registration_form::step_2::add_later"]'))).click()
        time.sleep(1)
        with open('result.txt', 'a', encoding='utf-8') as file:
            file.write(f'{name}{domain_text}:{password}{secret}\n')
        if imap_activate:
            for attempt in range(1,4):
                try:
                    driver.get('https://mail.rambler.ru/settings/mailapps/change')
                    if attempt == 1:
                        driver.refresh()
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.MailAppsChange-submitWrapper-JZ > button'))).click()
                    time.sleep(1)
                    print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP ' + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Fore.BLUE)
                    break
                except:
                    print(Style.RESET_ALL + Fore.RED + f'Error imap activate [{attempt} attempt]' + Style.RESET_ALL + Fore.BLUE)
                    if attempt == 3:
                        print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret} | IMAP ' + Fore.RED + 'FAIL' + Style.RESET_ALL + Fore.BLUE)
                        break
        else:
            print(Style.RESET_ALL + Fore.BLUE + f'{name}{domain_text}:{password}{secret}' + Style.RESET_ALL + Fore.BLUE)

    except :
        if num == 6:
            print(Style.RESET_ALL + Fore.RED + f'Captha error' + Style.RESET_ALL + Fore.BLUE)
        else:
            print(Style.RESET_ALL + Fore.RED + f'Unidentified error' + Style.RESET_ALL + Fore.BLUE)
    finally:
        driver.close()
        driver.quit()



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
    ctypes.windll.kernel32.SetConsoleTitleW(f'Rambler Reger by Ukral')
    os.system('cls')
    print(text)
    if not os.path.exists('chromedriver.exe'):
        print(Style.RESET_ALL + Fore.RED + 'You dont have chromedriver.exe!')
        input()
        exit()
    threading = int(input(Style.RESET_ALL + Fore.BLUE + 'Threading: ' + Style.BRIGHT))
    # count = int(input(Style.RESET_ALL + Fore.BLUE + 'Count: ' + Style.BRIGHT))
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
    p.map(startmain, a)
    input(Fore.BLUE + "Press enter to exit......" + Style.RESET_ALL)
    exit()
