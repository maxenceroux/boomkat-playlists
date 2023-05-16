from scrapper import SeleniumScrapper
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class SpotifyScrapper(SeleniumScrapper):
    def __init__(
        self, chromedriver: str, spotify_user: str, spotify_password: str
    ):
        super().__init__(chromedriver)
        self.spotify_user = spotify_user
        self.spotify_password = spotify_password

    def get_spotify_token(self) -> str:

        self.driver.get(
            "https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist"
        )
        start_time = time.time()
        print("Accepting OAuth")
        while (
            len(self.driver.find_elements_by_id("onetrust-accept-btn-handler"))
            == 0
        ):
            time.sleep(0.1)
            if time.time() - start_time > 10:
                print("Timed out waiting for OAuth")
                break
        time.sleep(2)
        button = self.driver.find_element_by_id(
            "onetrust-accept-btn-handler"
        ).click()
        time.sleep(1)
        print("Logging In")
        self.driver.find_elements_by_xpath("//*[contains(text(), 'Log in')]")[
            0
        ].click()
        while len(self.driver.find_elements_by_id("login-username")) == 0:
            time.sleep(0.1)
        button = self.driver.find_element_by_id("login-username")
        button.send_keys(self.spotify_user)
        button = self.driver.find_element_by_id("login-password")
        button.send_keys(self.spotify_password)
        button = self.driver.find_element_by_id("login-button").click()
        time.sleep(2)
        print("Switching to Iframe")
        iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe.sc-e9bdeb9e-0.NZqob")
        self.driver.switch_to.frame(iframe)
        
        while (
            len(
                self.driver.find_elements_by_xpath(
                    "//span[text()='Try it']"
                )
            )
            == 0
        ):
            time.sleep(0.1)
        print("Trying Endpoint")
        self.driver.find_elements_by_xpath("//span[text()='Try it']")[
            0
        ].click()
        start_time = time.time()
        print("Waiting for agreement")
        while (
            len(
                self.driver.find_elements_by_xpath(
                    "//p[text()='Agree']"
                )
            )
            == 0
        ):
            time.sleep(0.1)
            if time.time() - start_time > 3:
                print("Timed out waiting for agreement")
                break
        try:
            self.driver.find_elements_by_xpath(
                    "//p[text()='Agree']"
                )[0].click()
        except:
            pass
        print("Getting performance logs")
        logs = self.driver.get_log("performance")
        for log in logs:
            msg = json.loads(log["message"])
            if msg["message"]["method"] == "Network.requestWillBeSent":
                if (
                    "Authorization"
                    in msg["message"]["params"]["request"]["headers"]
                ):
                    token = msg["message"]["params"]["request"]["headers"][
                        "Authorization"
                    ].split("Bearer ")[-1]

        print(token)
        return token
