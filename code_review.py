from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import datetime
import uuid
import os
import json
import time


options = webdriver.ChromeOptions()
options.add_experimental_option(
    "excludeSwitches", ["enable-logging"]
)  # The above two code is to cater for the selenium error message
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
options.add_argument("--window-size=1500,1080")
driver = webdriver.Chrome(options=options)
URL = "https://www.agoda.com/en-gb/search?city=17193&checkIn=2023-03-03&los=14&rooms=1&adults=2&children=0&cid=1891458&locale=en-gb&ckuid=9cdf223f-a3ce-4890-965a-b2aab1ae50d6&prid=0&gclid=Cj0KCQjwqc6aBhC4ARIsAN06NmOZjaRodGcrUeKINOPnKgTZEfVb8z7hDSCrkddzvLoQZA07tdLlcnsaAg2qEALw_wcB&currency=GBP&correlationId=d880d555-ceda-41ba-b708-41c298e4db9b&pageTypeId=1&realLanguageId=16&languageId=1&origin=GB&tag=24bd4b3f-b6a1-50d5-e639-d9c49ca41c49&userId=9cdf223f-a3ce-4890-965a-b2aab1ae50d6&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=2&currencyCode=GBP&htmlLanguage=en-gb&cultureInfoName=en-gb&machineName=am-pc-4f-acm-web-user-7d974b9749-vw7ck&trafficGroupId=5&sessionId=ug4znrtc3dsxzbtr2i4zpami&trafficSubGroupId=122&aid=82361&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&checkOut=2023-03-17&priceCur=GBP&textToSearch=Bali&productType=-1&travellerType=1&familyMode=off"
driver.get(URL)


class Scraper:
    """This class contains different methods that work together to scrape certain information from a given website"""

    def __init__(self) -> None:
        self.hotel_link_list = []
        self.extended_hotel_link_list = []
        self.dict_properties = {
            "ID": [],
            "Timestamp": [],
            "Hotel Name": [],
            "Price": [],
            "Location": [],
            "Rating/10": [],
            "Image URL": [],
        }

    def accept_cookie(self) -> None:
        """This method accepts the cookies, this is done by finding and clicking the accept cookie button"""
        time.sleep(2)
        try:
            accept_cookies_button = driver.find_element(
                by=By.XPATH,
                value='//*[@id="consent-banner-container"]/div/div[2]/div/button[2]',
            )
            accept_cookies_button.click()
        except:
            pass  # If there is no cookies button, we won't find it, so we can pass

    def top_reviewed(self) -> None:
        """This method clicks the top review tab, so only top reviewed hotels are displayed."""
        time.sleep(2)
        review_bar = driver.find_element(
            by=By.XPATH, value='//*[@id="sort-bar"]/div/a[2]'
        )
        review_bar.click()
        time.sleep(2)

    def scroller(self) -> None:
        time.sleep(10)
        """This method is for scrolling the page, it does so by comparing the scrolled 
            height to the page height, if not equal, it scrolls some more until scrolled 
            height equals page height.
        """
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(20)
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight);")
            # Wait to load page
            time.sleep(20)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def list_of_hotel_links(self) -> List:
        """This method finds the hotel links and appends them to a list

        Returns:
            The list of hotel links.
        """
        time.sleep(2)
        try:
            hotel_container = driver.find_element(
                by=By.XPATH, value='//*[@id="contentContainer"]'
            )  # XPath corresponding to the Container
            hotel_list = hotel_container.find_elements(
                by=By.XPATH, value='//li/div/a[contains(@class, "PropertyCard__Link")]'
            )
            for hotel_link in hotel_list:
                time.sleep(10)
                links = hotel_link.get_attribute("href")
                self.hotel_link_list.append(links)
            return self.hotel_link_list
        except:
            pass

    def page_crawler(self) -> List:
        """This method collects all the hotel links from a range of pages specified,
        it does this by clicking the next page button, collects links and adds them to big list.

        Returns:
            An extended list of hotel links.
        """
        for page in range(2):
            time.sleep(2)
            self.extended_hotel_link_list.extend(self.list_of_hotel_links())
            next_button = driver.find_element(
                by=By.XPATH, value='//*[@id="paginationNext"]'
            )
            time.sleep(10)
            ActionChains(driver).move_to_element(next_button).click(
                next_button
            ).perform()
            self.scroller()
        # print(self.extended_hotel_link_list)
        return self.extended_hotel_link_list

    def get_price(self) -> Dict:
        """This method collects the price of the hotels.

        Returns:
            A dictionary with the prices.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            time.sleep(5)
            try:
                price = driver.find_element(
                    by=By.XPATH,
                    value='//*[@id="hotelNavBar"]/div/div/div/span/div/span[5]',
                ).text
                self.dict_properties["Price"].append(price)
            except:
                price = "Price Not Found"
                self.dict_properties["Price"].append(price)
                continue
        return self.dict_properties

    def get_hotelname(self) -> Dict:
        """This method collects the hotel names of the properties found

        Returns:
            A dictionary with the hotel names.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            time.sleep(20)
            try:
                hotel_name = driver.find_element(
                    by=By.XPATH,
                    value='//*[@id="property-main-content"]/div[1]/div[2]/div[1]/h1',
                ).text
                self.dict_properties["Hotel Name"].append(hotel_name)
            except:
                hotel_name = "Name not Found"
                self.dict_properties["Hotel Name"].append(hotel_name)
                continue
        return self.dict_properties

    def get_location(self) -> Dict:
        """This method collects the location of the hotels.

        Returns:
            A dictionary with the locations.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            time.sleep(5)
            try:
                location = driver.find_element(
                    by=By.XPATH,
                    value='//*[@id="property-main-content"]/div[1]/div[2]/div[2]/span[1]',
                ).text
                self.dict_properties["Location"].append(location)
            except:
                location = "Location not Found"
                self.dict_properties["Location"].append(location)
                continue
        return self.dict_properties

    def get_rating(self) -> Dict:
        """This method collects the rating of the hotels.

        Returns:
            A dictionary with the ratings.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            time.sleep(5)
            try:
                rating = driver.find_element(
                    by=By.XPATH,
                    value='//*[@id="property-critical-root"]/div/div[4]/div[2]/div[1]/div[1]/div/div[1]/div/div[1]/div/div/div/h3',
                ).text
                self.dict_properties["Rating/10"].append(rating)
            except:
                rating = "Rating not Found"
                self.dict_properties["Rating/10"].append(rating)
            continue
        return self.dict_properties

    def image_url(self) -> Dict:
        """This method finds and appends the image link to a dictioionary

        Returns:
            A dictionary with the links of images.
        """
        try:
            for link in self.extended_hotel_link_list[0:10]:
                driver.get(link)
                time.sleep(5)
                see_all_photos = driver.find_element(
                    by=By.XPATH, value='//*[@id="property-critical-root"]'
                )
                time.sleep(5)
                image = see_all_photos.find_element(
                    by=By.XPATH, value='//img[contains(@class, "SquareImage")]'
                )
                img = image.get_attribute("src")
                self.dict_properties["Image URL"].append(img)
            return self.dict_properties
        except:
            pass

    def timestamp(self) -> Dict:
        """Method creates a date and time for when the record was scraped.

        Returns:
            A dictionary with timesstamps for every record.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.dict_properties["Timestamp"].append(date)
        return self.dict_properties

    def unique_id(self) -> Dict:
        """This method creates unique id for every record in a dictionary

        Returns:
            A dictionary with uniquely generated ids per record.
        """
        for link in self.extended_hotel_link_list[0:10]:
            driver.get(link)
            id = str(uuid.uuid4())
            self.dict_properties["ID"].append(id)
        driver.quit()
        return self.dict_properties

    def create_folders(self) -> None:
        """Method creates a folder and subfolder in a specified path."""
        newpath = r"C:\Users\kambo\Desktop\Data-Collection-Pipeline\raw_data\hotels"

        if not os.path.exists(newpath):
            os.makedirs(newpath)

    def create_file(self) -> None:
        """Method creates a json file within a specified path."""
        with open(
            r"C:\Users\kambo\Desktop\Data-Collection-Pipeline\raw_data\hotels\data.json",
            "w",
        ) as file:
            json.dump(self.dict_properties, file)


def info():
    crawler = Scraper()
    crawler.accept_cookie()
    crawler.top_reviewed()
    crawler.scroller()
    crawler.page_crawler()
    crawler.get_price()
    crawler.get_hotelname()
    crawler.get_location()
    crawler.get_rating()
    crawler.image_url()
    crawler.timestamp()
    crawler.unique_id()
    crawler.create_folders()
    crawler.create_file()


if __name__ == "__main__":
    info()
