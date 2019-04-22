import re
import sys
import time
import datetime
from PIL import Image
import urllib.error as error
from selenium import webdriver
import urllib.request as request
from selenium.webdriver.common.by import By
from sites.doattend.main_resp import main_dict
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


event_data = main_dict()


def doattend_post_data():
    pass


class DoAttend():

    def __init__(self):
        self.email = '***REMOVED_EMAIL***'
        self.password = '***REMOVED_PASSWORD***'
        self.time_zone = 'New Delhi'
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.options.add_argument('--incognito')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("--disable-ipv6")
        self.options.add_argument("--disable-cast")
        self.options.add_argument("--disable-breakpad")
        self.options.add_argument('--disable-extentions')
        self.options.add_argument("--disable-cloud-import")
        self.options.add_argument('--enable-popup-blocking')
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--allow-http-screen-capture")
        self.options.add_argument("--disable-impl-side-painting")
        self.options.add_argument("--disable-session-crashed-bubble")
        self.options.add_argument("--disable-seccomp-filter-sandbox")
        self.options.add_argument("--disable-cast-streaming-hw-encoding")
        self.options.add_argument("--disable-client-side-phishing-detection")
        self.driver = webdriver.Chrome('/usr/bin/chromedriver',
                                  chrome_options=self.options)


    def waiter(self, driver, xpath):
        try:
            driver = self.driver
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except:
            print(
                "There was ann error in waiting for the given  xpath - {0}".format(xpath))
        else:
            return driver


    def closeBrowser(self):
        self.driver.close()


    def login(self):
        count = 3
        while count > 0:
            try:
                driver = self.driver
                driver.get('http://doattend.com')
                time.sleep(2)
                if self.waiter(driver, "//a[@href='/accounts/sign_in']") is not None:
                    driver.find_element(By.XPATH, "//a[@href='/accounts/sign_in']").click()
                    if self.waiter(driver, "//input[@id='email']") is not None:
                        driver.find_element(
                            By.XPATH, "//input[@id='email']").send_keys(self.email)
                        driver.find_element(
                            By.XPATH, "//input[@id='password']").send_keys(self.password)
                        driver.find_element(
                            By.XPATH, "//input[@id='account_submit']").click()
                    else:
                        print("There was an error in loading the login page")
                count-= 3
            except:
                self.driver.close()
                count-= 1


    def select_date_time(self, req_date, req_time, xpath):
        driver = self.driver
        if len(req_time) == 11:
            req_time = datetime.datetime.strptime(req_time, "%I:%M:%S %p")
            req_time = req_time.strftime("%H:%M")
            req_hour = int(req_time[0:2])
            req_minute = int(req_time[3:5])
        if req_time and type(req_time) == str:
            try:
                req_time = datetime.datetime.strptime(req_time, "%H:%M:%S")
                req_hour = req_time.hour
                req_minute = req_time.minute
                req_time = req_time.strftime("%H:%M")
            except:
                req_time = "00:00"
                req_hour = 0
                req_minute = 0
                pass

        req_date_obj = datetime.datetime.strptime(req_date, '%Y-%m-%d')
        req_date = req_date_obj.strftime('%b-%d-%Y')

        req_month = req_date[:3].lower()
        req_day = int(req_date[4:6])
        req_year = int(req_date[7:11])

        driver.find_element(By.XPATH, xpath).click()
        cal_month = driver.find_element(
            By.XPATH, "//span[@class='ui-datepicker-month']").text
        cal_year = int(driver.find_element(
            By.XPATH, "//span[@class='ui-datepicker-year']").text)

        while cal_year != req_year:
            driver.find_element(
                By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-e']").click()
            cal_year = int(driver.find_element(
                By.XPATH, "//span[@class='ui-datepicker-year']").text)

        while cal_month[:3].lower() != req_month:
            driver.find_element(
                By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-e']").click()
            cal_month = driver.find_element(
                By.XPATH, "//span[@class='ui-datepicker-month']").text

        days = driver.find_elements(
            By.XPATH, "//*[@id='ui-datepicker-div']//td/a[contains(.,'{0}')]".format(req_day))

        for day in days:
            if int(day.text) == req_day:
                day.click()
                break

        if req_time is not "0":
            if self.waiter(driver, "//*[@class='ui_tpicker_time']") is not None:
                hour_slider = driver.find_element(
                    By.XPATH, "/html/body/div[6]/div[2]/dl/dd[2]/a")
                minute_slider = driver.find_element(
                    By.XPATH, "/html/body/div[6]/div[2]/dl/dd[3]/a")
                sel_time = driver.find_element(
                    By.XPATH, "//*[@class='ui_tpicker_time']").text
                while sel_time != req_time:

                    sel_hour = int(sel_time[0:2])
                    hour_diff = abs(sel_hour - req_hour)
                    while sel_hour != req_hour:
                        if sel_hour < req_hour:
                            for x in range(20 * hour_diff):
                                hour_slider.send_keys(Keys.RIGHT)
                        elif sel_hour > req_hour:
                            for x in range(20 * hour_diff):
                                hour_slider.send_keys(Keys.LEFT)
                        sel_time = driver.find_element(
                            By.XPATH, "//*[@class='ui_tpicker_time']").text
                        sel_hour = int(sel_time[0:2])
                        hour_diff = abs(sel_hour - req_hour)

                    sel_minute = int(sel_time[3:5])
                    minute_diff = abs(sel_minute - req_minute)
                    while sel_minute != req_minute:
                        if sel_minute < req_minute:
                            for x in range(10 * minute_diff):
                                minute_slider.send_keys(Keys.RIGHT)
                        elif sel_minute > req_minute:
                            for x in range(10 * minute_diff):
                                minute_slider.send_keys(Keys.LEFT)
                        sel_time = driver.find_element(
                            By.XPATH, "//*[@class='ui_tpicker_time']").text
                        sel_minute = int(sel_time[3:5])
                        minute_diff = abs(sel_minute - req_minute)

        try:
            driver.find_element(
                By.XPATH, "//button[@type='button'][contains(.,'Done')]").click()
        except:
            pass


    def create_event(self, event_data):
        driver = self.driver
        driver.find_element(By.XPATH, "//a[@href='/events/new']").click()
        driver.find_element(By.ID, "event_title").send_keys(event_data['event info'][0]['event name'])

        if self.waiter(driver, "//*[@id='event_about_ifr']") is not None:
            about = driver.find_element(By.XPATH, "//*[@id='event_about_ifr']")
            driver.switch_to_frame(about)
            abt = driver.find_element_by_xpath("//*[@id='tinymce']/p")
            driver.execute_script(
                "arguments[0].textContent = arguments[1]", abt, event_data['event info'][0]['description'])
            driver.switch_to_default_content()

            time_z = Select(driver.find_element_by_xpath(
                "//select[@id='event_time_zone']"))
            time_z.select_by_value(self.time_zone)
            print("Start Date")
            self.select_date_time(event_data['event info'][0]['start date'], event_data['event info'][0]['start time'],
                             "//input[@name='event[start_date]']")
            print("End Date")
            self.select_date_time(event_data['event info'][0]['end date'], event_data['event info'][0]['end time'],
                             "//input[@name='event[end_date]']")

            try:
                _is_event_online = None
                if event_data['ercess partners categories'] == []:
                    _is_event_online = ''
                else:
                    website = ''
                    if _is_event_online:
                        print("This event is an online event")
                        driver.find_element(
                            By.XPATH, "//input[@id='event_has_no_address']").click()
                        driver.find_element(
                            By.XPATH, "//input[@id='event_venue']").send_keys(website)
                    else:
                        driver.find_element(By.ID, "event_venue").send_keys(event_data['event info'][0]['address 1']) #
                        driver.find_element(By.ID, "add1").send_keys(event_data['event info'][0]['address 1'])
                        driver.find_element(By.ID, "add2").send_keys(event_data['event info'][0]['address 2'])
                        driver.find_element(By.ID, "city").send_keys(event_data['event info'][0]['city'])
                        driver.find_element(By.ID, "event_state").send_keys(event_data['event info'][0]['state'])
                        driver.find_element(
                            By.ID, "event_postal_code").send_keys(event_data['event info'][0]['pincode'])
                        country_select = Select(
                            driver.find_element_by_xpath("//*[@id='event_country']"))
                        country_select.select_by_value(event_data['event info'][0]['country'])
            except NameError:
                driver.find_element(By.ID, "event_venue").send_keys(event_data['event info'][0]['address 1'])
                driver.find_element(By.ID, "add1").send_keys(event_data['event info'][0]['address 1'])
                driver.find_element(By.ID, "add2").send_keys(event_data['event info'][0]['address 2'])
                driver.find_element(By.ID, "city").send_keys(event_data['event info'][0]['city'])
                driver.find_element(By.ID, "event_state").send_keys(event_data['event info'][0]['state'])
                driver.find_element(
                    By.ID, "event_postal_code").send_keys(event_data['event info'][0]['pincode'])
                country_select = Select(
                    driver.find_element_by_xpath("//*[@id='event_country']"))
                country_select.select_by_value(event_data['event info'][0]['country'])

            print("subdomain process")
            contact_info = ''
            event_subdomain = ''
            driver.find_element(
                By.ID, "event_contact_info").send_keys(contact_info)
            driver.find_element(
                By.XPATH, "//*[@id='subdomain']").send_keys(event_subdomain)
            print("publish")
            driver.find_element(By.XPATH, "//input[@value='Publish']").click()


obj = DoAttend()
obj.login()
for i in event_data:
    obj.create_event(i)
    break