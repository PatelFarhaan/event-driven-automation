# coding : utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import urllib.request as request
import urllib.error as error
from PIL import Image
import datetime
import time
from common_file import *
from login_credentials import *
import pdb
import subprocess
import sys
from dbconnection import get_conn
import re

connection_object, cursor = get_conn()

_email = '***REMOVED_EMAIL***'
_password = '***REMOVED_PASSWORD***'
event_data = main_dict()
main_json = event_data
event_name = event_data['event info'][0]['event name']
eventname = event_name

# Event descripttion
asciiof = {"&nbsp;": " ", "&lt;": "<", "&gt;": ">", "&amp;": "&", "&quot;": "\"", "&apos;": "\'", "&cent;": "¢",
           "&pound;": "£",
           "&yen;": "¥", "&euro;": "€", "&copy;": "©", "&reg;": "®", "&ndash;": "–", "&mdash;": "—", "&rsquo;": "’",
           "&ldquo;": "“", "&rdquo;": "”"}

cleanr = re.compile('<.*?>')
description = re.sub(cleanr, '', event_data["event info"][0]["description"])
for key in asciiof.keys():
    cleanr = re.compile(key)
    description = re.sub(cleanr, asciiof[key], description)
event_about = description

time_zone = 'New Delhi'

# Event Tags/Categories
topics = main_json['categories of events'][0]
categories = []
# for topic in topics:
categories.append(topics['topic'])

categories = list(set(categories))
categories = ", ".join(categories)
event_id = event_data["event info"][0]["event id"]
try:
    partner_catgry = event_data['ercess partners categories'][0]['partner category'] if event_data[
        'ercess partners categories'] else ''
    _is_event_online = partner_catgry.lower(
    ) == 'online' or partner_catgry.lower() == 'webinar'
    if _is_event_online:
        print("This event is an online event")
        sql = """SELECT website FROM articles2 WHERE id ='%d'""" % event_id
        cursor.execute(sql)
        data = cursor.fatchall()
        website = data[0][0]
except:
    pass

start_date = event_data['event info'][0]["start date"]
start_time = event_data['event info'][0]["start time"]
end_date = event_data['event info'][0]["end date"]
end_time = event_data['event info'][0]["end time"]

address = event_data['event info'][0]["full address"].split(" - ")[0]
venu_name = address.split(", ")[0],

if address.split(", ")[2] == address.split(", ")[-2]:
    add_1 = address.split(", ")[0]
    add_2 = address.split(", ")[1]
else:
    add_1 = address.split(", ")[1]
    add_2 = address.split(", ")[2]

add_1 = event_data['event info'][0]["address 1"]
add_2 = event_data['event info'][0]["address 2"]
city = event_data['event info'][0]["city"]
state = event_data['event info'][0]["state"]
# postal_code = full_address.split(" - ")[-1]
postal_code = event_data['event info'][0]["pincode"]
country = event_data['event info'][0]["country"]

event_subdomain = eventname.strip()
event_subdomain = re.sub('[^a-zA-Z0-9\.]', '', event_subdomain)
event_subdomain = re.sub('[\s.]', '-', event_subdomain)

if event_subdomain[0].isdigit():
    event_subdomain = "the" + event_subdomain

url_text = "http://" + event_subdomain + ".doattend.com"
contact_info = cont_name + ', ' + cont_number + ', ' + email_id


def waiter(driver, xpath):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except:
        print(
            "There was ann error in waiting for the given  xpath - {0}".format(xpath))
    else:
        return driver


def saveURL(URL):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(regex, URL) is not None:
        print("Event URL : ", url_text)
        update_db = '/var/www/html/crons/event_posting/manual/update_db.py'
        try:
            table_id = sys.argv[1]
            # URL, table_id, promotion_status, partner_status
            cmd = ['python3', update_db, url_text,
                   table_id, 'published', 'approved']

            subprocess.call(cmd)
        except:
            print("Error occured while updating database")


def login(driver):
    global _email, _password
    if waiter(driver, "//a[@href='/accounts/sign_in']") is not None:
        driver.find_element(By.XPATH, "//a[@href='/accounts/sign_in']").click()
        if waiter(driver, "//input[@id='email']") is not None:
            driver.find_element(
                By.XPATH, "//input[@id='email']").send_keys(_email)
            driver.find_element(
                By.XPATH, "//input[@id='password']").send_keys(_password)
            driver.find_element(
                By.XPATH, "//input[@id='account_submit']").click()
        else:
            print("There was an error in loading the login page")


def select_date_time(req_date, req_time, xpath):
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
        print(cal_year)
        print(req_year)
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
        if waiter(driver, "//*[@class='ui_tpicker_time']") is not None:
            hour_slider = driver.find_element(
                By.XPATH, "/html/body/div[6]/div[2]/dl/dd[2]/a")
            minute_slider = driver.find_element(
                By.XPATH, "/html/body/div[6]/div[2]/dl/dd[3]/a")
            sel_time = driver.find_element(
                By.XPATH, "//*[@class='ui_tpicker_time']").text
            while sel_time != req_time:

                # hour_slider.click()
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
        import traceback
        pass

    time.sleep(1)
    print("datetime selection")


def create_tickets(driver):
    first_ticket = True

    def create_ticket():
        if waiter(driver, "//input[@name='ticket_type[name]']") is not None:
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[name]']").send_keys(ticket["_ticket_name"])
            select_date_time(ticket['_ticket_sale_start_date'],
                             "0", "//input[@name='ticket_type[sales_open]']")
            select_date_time(ticket['_ticket_sale_end_date'],
                             "0", "//input[@name='ticket_type[sales_close]']")
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[price]']").clear()
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[price]']").send_keys(ticket['_ticket_price'])
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[available_number]']").clear()
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[available_number]']").send_keys(ticket['_total_tickets'])
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[min_qty]']").clear()
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[min_qty]']").send_keys(ticket['_min_ticket_quantity'])
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[max_qty]']").clear()
            driver.find_element(
                By.XPATH, "//input[@name='ticket_type[max_qty]']").send_keys(ticket['_max_ticket_quantity'])
            driver.find_element(
                By.XPATH, "//input[@id='ticket_type_refundable_0']").click()
            driver.find_element(
                By.XPATH, "//input[@value='Add Ticket']").click()

    _ticket_list = []
    tickets = main_json['tickets']
    for ticket in tickets:
        if "ticket name" not in ticket:
            continue
        ticket_dict = {"_ticket_name": ticket['ticket name'], "_ticket_sale_start_date": ticket['ticket start date'],
                       "_ticket_sale_start_time": ticket['ticket start time'],
                       "_ticket_sale_end_date": ticket['expiry date'], "_ticket_sale_end_time": ticket['expiry time'],
                       "_total_tickets": ticket['ticket quantity'], "_min_ticket_quantity": ticket['minimum quantity'],
                       "_max_ticket_quantity": ticket['maximum quantity'], "_ticket_price": ticket['ticket price']}
        _ticket_list.append(ticket_dict)

    for ticket in _ticket_list:
        if first_ticket is True:
            if waiter(driver, "//a[contains(.,'new ticket')]") is not None:
                driver.find_element(
                    By.XPATH, "//a[contains(.,'new ticket')]").click()
                create_ticket()
                first_ticket = False
        elif first_ticket is not True:
            if waiter(driver, "//a[contains(.,'Create a New Ticket')]") is not None:
                driver.find_element(
                    By.XPATH, "//a[contains(.,'Create a New Ticket')]").click()
                create_ticket()
                first_ticket = False


def create_event(driver):
    driver.find_element(By.XPATH, "//a[@href='/events/new']").click()
    driver.find_element(By.ID, "event_title").send_keys(event_name)

    if waiter(driver, "//*[@id='event_about_ifr']") is not None:
        about = driver.find_element(By.XPATH, "//*[@id='event_about_ifr']")
        driver.switch_to_frame(about)
        abt = driver.find_element_by_xpath("//*[@id='tinymce']/p")
        driver.execute_script(
            "arguments[0].textContent = arguments[1]", abt, event_about)
        driver.switch_to_default_content()

        time_z = Select(driver.find_element_by_xpath(
            "//select[@id='event_time_zone']"))
        time_z.select_by_value(time_zone)
        print("Start Date")
        select_date_time(start_date, start_time,
                         "//input[@name='event[start_date]']")
        print("End Date")
        select_date_time(end_date, end_time,
                         "//input[@name='event[end_date]']")

        try:
            if _is_event_online:
                print("This event is an online event")
                driver.find_element(
                    By.XPATH, "//input[@id='event_has_no_address']").click()
                driver.find_element(
                    By.XPATH, "//input[@id='event_venue']").send_keys(website)
            else:
                driver.find_element(By.ID, "event_venue").send_keys(venu_name)
                driver.find_element(By.ID, "add1").send_keys(add_1)
                driver.find_element(By.ID, "add2").send_keys(add_2)
                driver.find_element(By.ID, "city").send_keys(city)
                driver.find_element(By.ID, "event_state").send_keys(state)
                driver.find_element(
                    By.ID, "event_postal_code").send_keys(postal_code)
                country_select = Select(
                    driver.find_element_by_xpath("//*[@id='event_country']"))
                country_select.select_by_value(country)
        except NameError:
            driver.find_element(By.ID, "event_venue").send_keys(venu_name)
            driver.find_element(By.ID, "add1").send_keys(add_1)
            driver.find_element(By.ID, "add2").send_keys(add_2)
            driver.find_element(By.ID, "city").send_keys(city)
            driver.find_element(By.ID, "event_state").send_keys(state)
            driver.find_element(
                By.ID, "event_postal_code").send_keys(postal_code)
            country_select = Select(
                driver.find_element_by_xpath("//*[@id='event_country']"))
            country_select.select_by_value(country)

        print("subdomain process")
        driver.find_element(
            By.ID, "event_contact_info").send_keys(contact_info)
        driver.find_element(
            By.XPATH, "//*[@id='subdomain']").send_keys(event_subdomain)
        print("publish")
        driver.find_element(By.XPATH, "//input[@value='Publish']").click()


def modify_ticketing_options(driver):
    if waiter(driver, "/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div/h4/a") is not None:
        driver.find_element(
            By.XPATH, "/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div/h4/a").click()
    else:
        if 'Only events that you Publish will be available for the public to view. You can publish/unpublish an event later by editing it. You can setup tickets and discounts for this event once you create it' in driver.page_source:
            return False

    if waiter(driver, "//input[@value='Participant']") is not None:
        driver.find_element(By.XPATH, "//input[@value='Participant']").click()
        driver.find_element(
            By.XPATH, "//input[@id='payment_options_is_paid_true']").click()
        driver.find_element(
            By.XPATH, "//select[@name='payment_options[currency]']").click()
        select = Select(driver.find_element(
            By.XPATH, "//select[@name='payment_options[currency]']"))
        select.select_by_value("INR")
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[acc_name]']").send_keys(ac_holder_name)
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[acc_number]']").send_keys(ac_number)
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[bank]']").send_keys(bankname)
        driver.find_element(
            By.XPATH, "//textarea[@name='payment_options[branch_add]']").send_keys(branch)
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[ifsc]']").send_keys(ifsc)
        if ac_type == 'Savings Account':
            driver.find_element(By.XPATH, "//input[@value='Savings']").click()
        elif ac_type == 'Current Account':
            driver.find_element(By.XPATH, "//input[@value='Current']").click()
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[name_on_receipt]']").send_keys(organization_name)
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[sales_limit]']").clear()
        driver.find_element(
            By.XPATH, "//input[@name='payment_options[sales_limit]']").send_keys("0")
        driver.find_element(By.XPATH, "//input[@name='confirm']").click()
    return True


def upload_photos(driver):
    banner0 = event_data['event info'][0]['banner']

    if waiter(driver, "//a[contains(.,'Customize')]") is not None:
        driver.find_element(By.XPATH, "//a[contains(.,'Customize')]").click()
        if waiter(driver, "//input[contains(@id,'event_logo')]") is not None:
            try:
                banner0 = event_data['event info'][0]['banner']
                header_image = request.urlopen(banner0)
                # header_image = request.urlopen(_server_name + banner0)
            except (ValueError, error.URLError, error.HTTPError):
                print("There was ValueError, URLError or HTTPError")
            else:
                try:
                    image = Image.open(header_image)
                except OSError:
                    print("There was OSErrror")
                else:
                    if waiter(driver, "//input[contains(@id,'event_logo')]") is not None:
                        header_image_name = 'temp.' + banner0.split('.')[-1]
                        # image.save('./images' + header_image_name)
                        image.save(image_location + header_image_name)
                        driver.find_element(
                            By.XPATH, "//input[contains(@id,'event_logo')]").send_keys(
                            image_location + header_image_name)
                    else:
                        print("There was an error in opening the upload file")
            driver.find_element(By.XPATH, "//input[@value='Update']").click()
            time.sleep(2)
            if waiter(driver, "//*[@id='success_msg']") is not None:
                print("Image has been uploaded")
            else:
                print("There was an error in uploading the image")


def event_tags(driver):
    try:
        driver.find_element(By.XPATH, "//a[@id='promote_nav']").click()
        if waiter(driver, "//input[@id='token-input-tag_names']") is not None:
            driver.find_element(
                By.XPATH, "//input[@id='token-input-tag_names']").send_keys(categories)
            driver.find_element(
                By.XPATH, "//input[contains(@id,'publishable')][@name='event[publishable]']").click()
            driver.find_element(By.XPATH, "//input[@value='Update']").click()
    except NameError:
        print("This event has no categories")
    except NoSuchElementException:
        print("Element not found.")


def time_formatter(time):
    try:
        return datetime.datetime.strptime(time, '%H:%M:%S').strftime("%H:%M %p")
    except:
        try:
            return datetime.datetime.strptime(time, '%H:%M %p').strftime("%H:%M %p")
        except:
            return datetime.datetime.strptime(time, '%H:%M:%S %p').strftime('%H:%M %p')


def validators():
    if datetime.datetime.strptime(event_data['event info'][0]['end date'], '%Y-%m-%d') < datetime.datetime.strptime(
            event_data['tickets'][0]['expiry date'], '%Y-%m-%d'):
        raise Exception("Ticket expiry date({}) should be ended before Event end date({})".format(
            event_data['tickets'][0]['expiry date'], event_data['event info'][0]['end date']))

    if datetime.datetime.strptime(event_data['event info'][0]['start date'],
                                  '%Y-%m-%d') < datetime.datetime.now() or datetime.datetime.strptime(
            event_data['event info'][0]['start date'], '%Y-%m-%d') > datetime.datetime.strptime(
            event_data['event info'][0]['end date'], '%Y-%m-%d'):
        raise Exception("Event start date should be less than Event end date and should be greater than current date")

    if event_data['event info'][0]['start date'] == event_data['event info'][0]['end date']:
        if time_formatter(event_data['event info'][0]['start time']) >= time_formatter(
                event_data['event info'][0]['start time']):
            raise Exception("Event start date should be less than Event end date")

    if datetime.datetime.strptime(event_data['tickets'][0]['ticket start date'],
                                  '%Y-%m-%d') < datetime.datetime.now() or datetime.datetime.strptime(
            event_data['tickets'][0]['expiry date'], '%Y-%m-%d') < datetime.datetime.now():
        raise Exception("Ticket start date and end date must be greater than current date")


if __name__ == '__main__':

    try:
        if not event_data:
            raise Exception('There is not event data to process.')
        import datetime

        if datetime.datetime.strptime(event_data['event info'][0]['end date'], '%Y-%m-%d') < datetime.datetime.strptime(
                event_data['tickets'][0]['expiry date'], '%Y-%m-%d'):
            raise Exception("Ticket expiry date({}) should be ended before Event end date({})".format(
                event_data['tickets'][0]['expiry date'], event_data['event info'][0]['end date']))
        validators()
        print("opening")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome('/usr/bin/chromedriver',
                                  chrome_options=chrome_options)
        driver.get('http://doattend.com')
        driver.implicitly_wait(20)
        print("login")
        login(driver)
        print("create event")
        create_event(driver)
        print("modify ticketing options")
        result = modify_ticketing_options(driver)
        if not result:
            print("Error: Please verify if event is already created")
        else:

            print("create tickets")
            create_tickets(driver)
            print("upload photos")
            upload_photos(driver)
            print("event tags")
            event_tags(driver)
            print("save URL")
            print(url_text)
            saveURL(url_text)
            print("done")
        driver.close()
    except:
        import traceback

        traceback.print_exc()
