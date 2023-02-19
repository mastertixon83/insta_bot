from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from fake_useragent import UserAgent
from db_api.db_commands import DBCommands

import time
import pickle
import os
import json
import psycopg2
import psycopg2.extras
from data.config import host, PG_PASS, PG_USER, DB_NAME

db = DBCommands()

service = Service(executable_path="/home/tixon/u4eba/Python/bots/instagram/pc_helper/bot/chromedriver/chromedriver")
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
# Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36

options = webdriver.ChromeOptions()

options.add_argument(f"user-agent={useragent}")

### Disable webdriver mode
# options.add_argument("--disable-blink-features=AutomationControlled")

### Фоновый режим
# options.add_argument("--headless")


driver = webdriver.Chrome(service=service, options=options)

# url = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
url = "https://www.instagram.com"


def create_db():
    with open("db_api/create_db.sql", "r") as file:
        create_db_command = file.read()

    conn_string = f"host={host} dbname={DB_NAME} user={PG_USER} password={PG_PASS}"
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True

    cursor = conn.cursor()
    cursor.execute(create_db_command)

    return conn, cursor


def load_data_from_json(filename):
    with open(filename, 'r') as file:
        all_linnks = json.load(file)
    return all_linnks


def save_data_in_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def auth(login, password):
    if not os.path.exists(f"cookies/{login}_cookies"):

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
        with(open(f"cookies/{login}_cookies", "wb")) as file:
            pickle.dump(driver.get_cookies(), file=file)
    else:
        print("load cookies")
        ### load cookies
        with(open(f"cookies/{login}_cookies", "rb")) as file:
            for cookie in pickle.load(file=file):
                driver.add_cookie(cookie)

        time.sleep(5)
        driver.refresh()
        print("refresh page")
        time.sleep(5)
        driver.execute_script("document.getElementsByClassName('_a9-- _a9_1')[0].click()")
        time.sleep(3)


def parse_subscribers(url, conn):
    driver.get(url=url)
    time.sleep(4)
    follower_count = driver.find_element(By.XPATH,
                                         "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a/div").find_element(
        By.CLASS_NAME, "_ac2a").get_property('title').replace("\xa0", "")

    loops_count = int(follower_count) // 12
    followers = []

    while True:
        try:
            load_more = driver.find_element(By.CLASS_NAME, "_aanq")
            actions = ActionChains(driver)
            actions.move_to_element(load_more).perform()
            time.sleep(3)
        except:
            print('Done')
            time.sleep(3)
            all_urls_div = driver.find_elements(By.CLASS_NAME, '_ab8w._ab94._ab97._ab9f._ab9k._ab9p._ab9-._aba8._abcm')
            #
            # all_urls_div = driver.find_elements(By.XPATH, "//div[@class='_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p  _ab9- _aba8 _abcm']/div")

            for item in all_urls_div:
                try:
                    name = item.find_element(By.CLASS_NAME, "_aacl._aaco._aacu._aacy._aada").text
                except Exception as ex:
                    name = "None"

                account = item.find_element(By.CLASS_NAME, "_ab8y._ab94._ab97._ab9f._ab9k._ab9p._abcm").text
                link = item.find_element(By.TAG_NAME, "a").get_property("href")

                # Сохранение ссылки в БД
                sql = db.add_new_user(username=name, nickname=account, url=link)
                command = sql[0]
                args = sql[1]
                with conn.cursor() as cur:
                    print(sql)
                    cur.execute(command, args)
                    record_id = cur.fetchone()
                    print(f"Запись добавлена")
            break

    # /html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]
    # поле с сылкой на подписчика aria-labelledby


def follow(conn, count):
    # Выбрать подписчиков из БД
    command, args = db.get_users(follow=False)

    with conn.cursor() as cur:
        cur.execute(command, args)
        users = cur.fetchmany(count)

        for item in users:
            # url = item[1]
            url = "https://www.instagram.com/4ashkacoffe/"
            id = int(item[0])

            driver.get(url=url)
            time.sleep(5)

            # Подписка
            follow_btn = driver.find_element(By.XPATH,
                                             '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button')

            if follow_btn.text == "Подписаться":
                follow_btn.click()
                time.sleep(4)

            command, args = db.update_user_follow_status(id=id)
            cur.execute(command, args)


def unfollow(conn, count):
    # Выбрать подписчиков из БД
    command, args = db.get_users(follow=True)

    with conn.cursor() as cur:
        cur.execute(command, args)
        users = cur.fetchmany(count)

        for item in users:
            # url = item[1]
            url = "https://www.instagram.com/4ashkacoffe/"
            id = int(item[0])

            driver.get(url=url)
            time.sleep(5)

            # Подписка
            follows_btn = driver.find_element(By.XPATH,
                                             "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button")


            follows_btn.click()
            time.sleep(4)

            unfollow_btn = driver.find_element(By.XPATH,
                                               "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div/div[7]/div/div/div/div/div/div")

            unfollow_btn.click()
            time.sleep(10)

            command, args = db.update_user_unfollow_status(id=id)
            cur.execute(command, args)


def main():
    conn, cur = create_db()

    links = load_data_from_json("links/follow.json")

    try:
        driver.get(url=url)
        time.sleep(5)
        login = "pc_helper"
        password = "gft654gfhgf"

        auth(login=login, password=password)
        print("auth complete")

        # # Сбор подписчиков с аккаунта
        # for link in links[:1]:
        #     parse_subscribers(url=f"{link['URL']}followers/", conn=conn)

        # # Подписка
        # follow(conn=conn, count=3)

        # # Отписка
        # unfollow(conn=conn, count=3)


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
