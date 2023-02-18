from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import time
import pickle
import os

service = Service(executable_path="/home/tixon/u4eba/Python/bots/instagram/pc_helper/bot/chromedriver/chromedriver")
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

options = webdriver.ChromeOptions()

options.add_argument(f"user-agent={useragent}")

### Disable webdriver mode
# options.add_argument("--disable-blink-features=AutomationControlled")

### Фоновый режим
# options.add_argument("--headless")


driver = webdriver.Chrome(service=service, options=options)

# url = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
url = "https://www.instagram.com"


# Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36
def main():
    try:
        driver.get(url=url)
        time.sleep(25)
        login = "pc_helper"
        password = "gft654gfhgf"

        if not os.path.exists(f"{login}_cookies"):

            username_input = driver.find_element(By.NAME, "username")
            username_input.clear()
            username_input.send_keys(login)

            password_input = driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(2)
            password_input.send_keys(Keys.ENTER)
            time.sleep(15)
            driver.execute_script("document.getElementsByClassName('_acan _acao _acas _aj1-')[0].click()")
            time.sleep(15)
            driver.execute_script("document.getElementsByClassName('_a9-- _a9_1')[0].click()")
            time.sleep(10)

            ### save cookies
            with(open(f"{login}_cookies", "wb")) as file:
                pickle.dump(driver.get_cookies(), file=file)
        else:
            print("load cookies")
            ### load cookies
            with(open(f"{login}_cookies", "rb")) as file:
                for cookie in pickle.load(file=file):
                    driver.add_cookie(cookie)

            time.sleep(5)
            driver.refresh()
            print("refresh page")
            time.sleep(10)
            driver.execute_script("document.getElementsByClassName('_a9-- _a9_1')[0].click()")
            time.sleep(30)


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
