from scrapper import SeleniumScrapper
import time


class BoomkatScrapper(SeleniumScrapper):
    def __init__(self, chromedriver: str):
        super().__init__(chromedriver)

    def get_bestsellers_list(self, genre_id=None):
        if genre_id:
            self.driver.get(
                f"https://boomkat.com/bestsellers?q[release_date]=last-week&q[genre]={genre_id}"
            )
        else:
            self.driver.get(
                "https://boomkat.com/bestsellers?q[release_date]=last-week"
            )
        time.sleep(1)
        bestsellers_web_element = self.driver.find_elements_by_class_name(
            "bestsellers"
        )[0].text
        bestsellers_list = bestsellers_web_element.split("\n")
        bestseller_assert = bestsellers_list[0]
        assert "Bestsellers (showing last " in bestseller_assert

        bestsellers_list = [x for x in bestsellers_list if "Play All" not in x]
        offset = bestsellers_list.index("Reset")
        bestsellers_list = bestsellers_list[offset + 1 :]
        x = 0
        bestsellers = []
        for i in range(len(bestsellers_list)):
            if i % 3 == 0:
                bestsellers.append(bestsellers_list[i])
        bestsellers_all = []
        for x in bestsellers:
            try:
                bestsellers_all.append(
                    {"artist": x.split(" - ")[0], "album": x.split(" - ")[1]}
                )
            except:
                pass

        # bestsellers = [" ".join(x.split(" - ")) for x in bestsellers]
        return bestsellers_all

    def get_recommended_list(self):
        self.driver.get(
            "https://boomkat.com/new-releases?q[status]=recommended"
        )
        time.sleep(1)
        today_recommends_sec = self.driver.find_elements_by_class_name(
            "product-listing"
        )[0]
        artist_names = today_recommends_sec.find_elements_by_xpath("//strong")
        album_names = today_recommends_sec.find_elements_by_class_name(
            "album-title"
        )
        recommended = []
        for i in range(len(album_names)):
            recommended.append(
                {"artist": artist_names[i].text, "album": album_names[i].text}
            )

        return recommended
