import json
import argparse
import os
from datetime import datetime
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_cond
import pyotp as pyotp
from loguru import logger


def get_otp(k):
    totp = pyotp.TOTP(k)
    return totp.now()


def search_and_reply():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Load settings from file in json format.')
    conf_args = parser.parse_args()
    if conf_args.config:
        with open(conf_args.config, "r") as fp:
            args = json.load(fp)

    try:
        options = FirefoxOptions()
        if bool(args['headless']):
            options.add_argument("--headless")
            logger.info("Running headless browser")
        driver = webdriver.Firefox(options=options,
                                   service=FirefoxService(GeckoDriverManager().install(), log_path=os.devnull))
        driver.get("https://www.twitter.com/login")
        driver.maximize_window()
        wait = WebDriverWait(driver, timeout=10, poll_frequency=5)
    except selenium.common.exceptions.TimeoutException:
        logger.error("Browser or webdriver error! Sorry!")
        driver.close()
        quit()

    try:
        wait.until(
            exp_cond.visibility_of_element_located((By.XPATH, "//input[@name='text']"))
        ).send_keys(args['username'])
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//span[text()='Next']"))).click()
        wait.until(
            exp_cond.visibility_of_element_located((By.XPATH, "//input[@name='password']"))
        ).send_keys(args['password'])
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//span[text()='Log in']"))).click()

        if bool(args['otp']):
            wait.until(
                exp_cond.visibility_of_element_located((By.XPATH, "//input[@name='text']"))
            ).send_keys(get_otp(args['otp']))
            wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//span[text()='Next']"))).click()

        if bool(wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//span[text()='Home']")))):
            logger.info("Successfully logged in")
    except selenium.common.exceptions.TimeoutException:
        logger.error("Login error! Sorry!")
        driver.get_screenshot_as_file('error-{}.png'.format(datetime.now().strftime('%Y-%m-%d-%H_%M_%S')))
        driver.close()
        quit()

    q = '{} min_replies:{} min_faves:{} min_retweets:{} -filter:links -filter:replies'.format(
        args['search'],
        args['min_replies'],
        args['min_faves'],
        args['min_retweets']
    )

    if bool(args['exclude_word']):
        q = q + " -{}".format(args['exclude_word'])

    logger.info("Doing search")
    try:
        searchbox_input = "//input[@data-testid='SearchBox_Search_Input']"
        # fill search box
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, searchbox_input))).send_keys(q)

        # submit search
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, searchbox_input))).submit()

        # click in lasted tab
        tab_lasted = "//div[@data-testid='ScrollSnap-List']//a[@tabindex='-1']"
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, tab_lasted))).click()

        # click reply in the first result
        content_editables = "//div[@contenteditable='true']"
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//div[@data-testid='reply']"))).click()
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, content_editables))).send_keys(" ")
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, content_editables))).send_keys(args['message'])
    except selenium.common.exceptions.TimeoutException:
        logger.error("Search error! Sorry!")
        driver.get_screenshot_as_file('error-{}.png'.format(datetime.now().strftime('%Y-%m-%d-%H_%M_%S')))
        driver.close()
        quit()

    try:
        user_replied = wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//div[@dir='ltr']"))).text
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']"))).click()
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, searchbox_input))).clear()
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, searchbox_input))).send_keys(
            "(from:{}) ({})".format(args["username"], user_replied)
        )
        wait.until(exp_cond.visibility_of_element_located((By.XPATH, searchbox_input))).submit()

        string_time = "//div[@data-testid='User-Names']//a[@dir='auto']"
        url_reply = wait.until(exp_cond.visibility_of_element_located((By.XPATH, string_time))).get_attribute('href')
        logger.info("Replied link: {}.".format(url_reply))
    except selenium.common.exceptions.TimeoutException:
        logger.error("Reply error! Sorry!")
        driver.get_screenshot_as_file('error-{}.png'.format(datetime.now().strftime('%Y-%m-%d-%H_%M_%S')))
        driver.close()
        quit()

    logger.info("Reply posted")
    driver.close()

    logger.info("Bye!")


if __name__ == '__main__':
    search_and_reply()
    quit()
