import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pyotp as pyotp
import argparse
from loguru import logger


def get_otp(k):
    totp = pyotp.TOTP(k)
    return totp.now()


def search_and_reply():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--headless', dest='headless', action='store_true', help="Headless Browser")
    parser.add_argument('--no-headless', dest='headless', action='store_false', help="Headless Browser")
    parser.set_defaults(headless=True)
    parser.add_argument("-u", "--username", type=str, help="Twitter Username")
    parser.add_argument("-p", "--password", type=str, help="Twitter Password")
    parser.add_argument("-otp", "--otp", type=str, help="OTP Secret Key")
    parser.add_argument("-s", "--search", type=str, help="String to search")
    parser.add_argument("-m", "--message", type=str, help="Reply message")
    parser.add_argument("-mr", "--min_replies", type=int, default=0, help="Minimal replies")
    parser.add_argument("-mf", "--min_faves", type=int, default=0, help="Minimal favorites")
    parser.add_argument("-mrt", "--min_retweets", type=int, default=0, help="Minimal retweets")

    args = parser.parse_args()

    options = FirefoxOptions()
    if args.headless:
        options.add_argument("--headless")
        logger.info("Running headless browser")
    s = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=s)
    driver.get("https://www.twitter.com/login")
    time.sleep(5)

    driver.find_element(By.XPATH, "//input[@name='text']").send_keys(args.username)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    time.sleep(5)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(args.password)
    driver.find_element(By.XPATH, "//span[text()='Log in']").click()


    if args.otp is not None:
        time.sleep(5)
        driver.find_element(By.XPATH, "//input[@name='text']").send_keys(get_otp(args.otp))
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

    time.sleep(5)
    logger.info("Successfully logged in")

    q = '{} min_replies:{} min_faves:{} min_retweets:{} -filter:links -filter:replies'.format(
        args.search,
        args.min_replies,
        args.min_faves,
        args.min_retweets
    )

    logger.info("Doing search")
    search_string = 'https://twitter.com/search?q={}&src=typed_query&f=live'.format(q)
    driver.get(search_string)
    time.sleep(12)
    driver.find_element(By.XPATH, "//div[@data-testid='reply']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//div[@contenteditable='true']").send_keys(" ")
    driver.find_element(By.XPATH, "//div[@contenteditable='true']").send_keys(args.message)
    time.sleep(3)

    driver.find_element(By.XPATH, "//div[@data-testid='tweetButton']").click()

    logger.info("Reply posted")
    driver.close()

    logger.info("Bye!")


if __name__ == '__main__':
    search_and_reply()
