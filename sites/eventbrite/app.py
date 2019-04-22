import os
import shutil
import requests
import urllib.request as request
from eventbrite import Eventbrite
from sites.eventbrite.main_resp import main_dict


resp_data = main_dict()
api_key = "TZQTPFB727PO6LNQS473"
events_api = Eventbrite(api_key)


def convert24(str1):
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-3]

    elif str1[-2:] == "AM":
        return str1[:-3]
    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-3]

    else:
        return str(int(str1[:2]) + 12) + str1[2:8]


##############   SINGLE  #####################
all_event_details = []

for i in resp_data:
    event_data = {
        "event": {
            "name": {
                "html": i['event info'][0]['event name']
            },
            "description": {
                "html": i['event info'][0]['description']
            },
            "start": {
                "timezone": "Asia/Kolkata",
                "utc": i['event info'][0]['start date'] + i['event info'][0]['start time']
            },
            "end": {
                "timezone": "Asia/Kolkata",
                "utc": i['event info'][0]['end date'] + i['event info'][0]['end time']
            },
            "currency": "USD",
            "online_event": (True if i['ercess partners categories'][0]['partner category'] == ("online" or "webinar") else False),
            "organizer_id": "",
            "capacity": i['tickets'][-1]['capacity']
        }
    }
    temp = {}
    temp[i['event info'][0]['event name']] = event_data

    all_event_details.append(temp)


############### LOOP ####################


def ticket_details():
    all_ticket_details = []
    for j in resp_data:
        event_name = j['event info'][0]['event name']
        no_of_tickets = j['tickets']
        for i in range(len(no_of_tickets) - 1):
            ticket_class_data ={
                "ticket_class": {
                    "name": j['tickets'][i]['ticket name'],
                    "description": j['tickets'][i]['ticket message'],
                    "donation": False,
                    "free": False,
                    "minimum_quantity": j['tickets'][i]['minimum quantity'],
                    "maximum_quantity": j['tickets'][i]['maximum quantity'],
                    "quantity_total": j['tickets'][i]['ticket quantity'],
                    "sales_start": j['tickets'][i]['ticket start date'] + j['tickets'][i]['ticket start time'],
                    "sales_end": j['tickets'][i]['expiry date'] + j['tickets'][i]['expiry time'],
                    "hidden": False,
                    "include_fee": True,
                    "split_fee": False,
                    "hide_description": False,
                    "auto_hide": False,
                    "auto_hide_before": "",
                    "auto_hide_after": "",
                    "order_confirmation_message": '',
                    "sales_channels": [
                        "online",
                        "atd"
                    ],
                    "delivery_methods": [
                        "electronic",
                    ],
                    "cost": j['tickets'][i]['ticket price']
                }
            }
            temp = {}
            temp[event_name] = ticket_class_data
            all_ticket_details.append(temp)

    return all_ticket_details


def create_event():
    event_posting_result = []
    for i in resp_data:
        event_name = i['event info'][0]['event name']
        end_date_12f = i['event info'][0]['end time']
        end_date_24f = convert24(end_date_12f)
        start_dt = ((i['event info'][0]['start date'] + 'T' + i['event info'][0]['start time'])[:-3]) + 'Z'
        end_dt = ((i['event info'][0]['end date'] + 'T' + end_date_24f)) + 'Z'
        event_data['event']['start']['utc'] = start_dt
        event_data['event']['end']['utc'] = end_dt
        result = events_api.post_event(event_data)
        temp = {}
        temp[event_name] = result
        event_posting_result.append(temp)
    return event_posting_result


def download_media_file():
    img_folder = 'sites/eventbrite/temp_img/'
    if os.path.exists(img_folder):
        shutil.rmtree(img_folder)

    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    all_downloaded_links = []
    for i in resp_data:
        event_name = i['event info'][0]['event name']
        img_folder = img_folder+"{0}.png".format(event_name)
        resp = 400
        try:
            resp = request.urlretrieve('https://ercess.com' + i['event info'][0]['banner'], img_folder)
        except:
            pass
        temp = {}
        temp[event_name] = resp
        all_downloaded_links.append(temp)

    return all_downloaded_links


def upload_file():
    download_media_file()
    upload_details = []
    data = requests.get("https://www.eventbriteapi.com/v3/media/upload/?type=image-event-logo-preserve-quality&token="+api_key).json()
    post_args = data['upload_data']
    for i in os.listdir('sites/eventbrite/temp_img'):
        if i.endswith('.png'):
            response = requests.post(data['upload_url'],
                                     data = post_args,
                                     files = {
                                         data['file_parameter_name']: open('sites/eventbrite/temp_img/'+i,'rb')
                                     }
                                     )
            temp = {}
            event_name = i
            result = (response, data['upload_token'])
            temp[event_name] = result
            upload_details.append(temp)
    return upload_details


def create_ticket():
    try:
        try:
            event_data = create_event()
        except:
            pass

        all_ticket_details = ticket_details()


        for event in resp_data:
            event_name = event['event info'][0]['event name']
            for counter, tickets in enumerate(all_ticket_details):

                tickets[event_name]['ticket_class']['sales_start'] = tickets[event_name]['ticket_class']['sales_start'][:10] + 'T' + \
                                                         tickets[event_name]['ticket_class']['sales_start'][10:] + 'Z'
                tickets[event_name]['ticket_class']['sales_end'] = tickets[event_name]['ticket_class']['sales_end'][:10] + 'T' + \
                                                       tickets[event_name]['ticket_class']['sales_end'][10:] + 'Z'
                tickets[event_name]['ticket_class']['cost'] = 'USD:' + tickets[event_name]['ticket_class']['cost'][:-2]
                try:
                    res = events_api.post_event_ticket_class(event_id=event_data[counter][event_name]['id'],
                                                   data=tickets[event_name])
                except:
                    pass
    except:
        pass


def eventbrite_post_data():
    create_ticket()
    upload_file()
    print("EventBrite Processing Done!!!")