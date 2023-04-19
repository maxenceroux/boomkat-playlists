from scrapper import SeleniumScrapper
import time
import json


class SpotifyScrapper(SeleniumScrapper):
    def __init__(
        self, chromedriver: str, spotify_user: str, spotify_password: str
    ):
        super().__init__(chromedriver)
        self.spotify_user = spotify_user
        self.spotify_password = spotify_password

    def get_spotify_token(self) -> str:

        self.driver.get(
            "https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile"
        )
        start_time = time.time()
        while len(
            self.driver.find_elements_by_id("onetrust-accept-btn-handler") == 0
        ):
            time.sleep(0.1)
            if time.time() - start_time > 10:
                print("Timed out waiting for OAuth")
                break
        button = self.driver.find_element_by_id(
            "onetrust-accept-btn-handler"
        ).click()
        time.sleep(1)

        self.driver.find_elements_by_xpath("//*[contains(text(), 'Log in')]")[
            0
        ].click()
        while len(self.driver.find_elements_by_id("login-username") == 0):
            time.sleep(0.1)
        button = self.driver.find_element_by_id("login-username")
        button.send_keys(self.spotify_user)
        button = self.driver.find_element_by_id("login-password")
        button.send_keys(self.spotify_password)
        button = self.driver.find_element_by_id("login-button").click()
        while len(
            self.driver.find_elements_by_xpath(
                "//*[contains(text(), 'Try it')]"
            )
            == 0
        ):
            time.sleep(0.1)
        self.driver.find_elements_by_xpath("//*[contains(text(), 'Try it')]")[
            0
        ].click()
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
                    break
                else:
                    token = None
        return token
