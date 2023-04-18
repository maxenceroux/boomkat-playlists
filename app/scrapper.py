from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumScrapper:
    def __init__(self, chromedriver: str) -> None:
        self.chromedriver = chromedriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1024x768")
        caps = DesiredCapabilities.CHROME
        caps["goog:loggingPrefs"] = {"performance": "ALL"}
        if self.chromedriver == "local":
            self.driver = webdriver.Chrome(
                desired_capabilities=caps, options=chrome_options
            )
        else:
            self.driver = webdriver.Remote(
                "http://chrome:4444/wd/hub",
                desired_capabilities=caps,
                options=chrome_options,
            )

    def quit(self):
        self.driver.quit()
