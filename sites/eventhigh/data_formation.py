import json
import time
import calendar
from datetime import datetime
from sites.eventhigh.main_resp import main_dict
from sites.eventhigh.google_image import implicit


ticket_ids = []
event_ticket_ids = {}
resp_data = main_dict()


def tickets_str_to_date(string_date):
    if int(string_date[10:12]) > 12:
        temp = str(int(string_date[10:12]) - 12)
        if len(temp) == 1:
            temp = '0' + temp
        return string_date[:10]+'T'+temp+string_date[12:]+'.000Z'
    else:
        return string_date[:10]+'T'+string_date[10:]+'.000Z'


def datetime_to_iso(string_date):
    resp = datetime.strptime(string_date, '%Y-%m-%d%H:%M:%S')
    resp = time.mktime(resp.timetuple())*1000
    return resp


def minute_change(string):
    mins = int(string[3:5])
    if  15 >=  mins >= 0:
        return string[:3]+'00'+string[5:]
    elif 30 >= mins > 15:
        return string[:3] + '30' + string[5:]
    elif 45 >= mins > 30:
        return string[:3] + '30' + string[5:]
    elif mins > 45:
        hr = str(int(string[:2]) + 1)
        return hr + ':' + '00' + string[5:]


def custom_questions():
    pass


def ticket_details():
    all_ticket_details = []
    if resp_data:

        for i in range(len(resp_data)):
            sub_list = []
            temp = resp_data[i]['tickets']
            for j in range(len(temp)-1):

                ticket_event_name = resp_data[i]['event info'][0]['event name']
                ticket_class_data = {
                    "ticket_class": {
                        "name": resp_data[i]['tickets'][j]['ticket name'],
                        "description": resp_data[i]['tickets'][j]['ticket message'],
                        "donation": False,
                        "free": False,
                        "minimum_quantity": resp_data[i]['tickets'][j]['minimum quantity'],
                        "maximum_quantity": resp_data[i]['tickets'][j]['maximum quantity'],
                        "quantity_total": resp_data[i]['tickets'][j]['ticket quantity'],
                        "sales_start": resp_data[i]['tickets'][j]['ticket start date']+resp_data[i]['tickets'][j]['ticket start time'],
                        "sales_end": resp_data[i]['tickets'][j]['expiry date']+resp_data[i]['tickets'][j]['expiry time'],
                        "hidden": False,
                        "include_fee": False,
                        "split_fee": False,
                        "hide_description": False,
                        "auto_hide": False,
                        "auto_hide_before": "",
                        "auto_hide_after": "",
                        "order_confirmation_message": '',
                        "capacity": temp[1]['capacity'],
                        "sales_channels": [
                            "online",
                            "atd"
                        ],
                        "delivery_methods": [
                            "electronic",
                        ],
                        "cost": resp_data[i]['tickets'][j]['ticket price']
                    }
                }
                sub_list.append(ticket_class_data)
            temp_dict = {}
            temp_dict[ticket_event_name] = sub_list
            all_ticket_details.append(temp_dict)
        return all_ticket_details

    else:
        return False


def ticket_adapter():
    all_data = []
    ticket_resp = ticket_details()
    if ticket_resp:
        for counter, i in enumerate(ticket_resp):
            ticket_event_name = list(i.keys())[0]
            temp_list = []
            for j in range(len(ticket_resp[counter][ticket_event_name])):
                ticket_adapter_class= {
                    'applicableOn': [],
                    'capacity': i[ticket_event_name][j]['ticket_class']['capacity'],
                    'isExpanded': True,
                    'name': i[ticket_event_name][j]['ticket_class']['name'],
                    'note': i[ticket_event_name][j]['ticket_class']['description'],
                    'price': float(i[ticket_event_name][j]['ticket_class']['cost']),
                    'validityEnd': int(str(int(time.mktime(time.strptime(i[ticket_event_name][j]['ticket_class']['sales_end'][:10]+' '+minute_change(i[ticket_event_name][j]['ticket_class']['sales_end'][10:]),
                                                                         '%Y-%m-%d %H:%M:%S'))))+'000'),
                    'validityEndDate': str(tickets_str_to_date(i[ticket_event_name][j]['ticket_class']['sales_end'])),
                    'validityStart': int(str(int(time.mktime(time.strptime(i[ticket_event_name][j]['ticket_class']['sales_start'][:10]+' '+minute_change(i[ticket_event_name][j]['ticket_class']['sales_start'][10:]),
                                                                           '%Y-%m-%d %H:%M:%S'))))+'000'),
                    'validityStartDate': str(tickets_str_to_date(i[ticket_event_name][j]['ticket_class']['sales_start']))
                }

                temp_list.append(ticket_adapter_class)
            temp_dict = {}
            temp_dict[ticket_event_name] = temp_list
            all_data.append(temp_dict)
        return all_data

    else:
        return False


def formed_data():
    image_url = implicit()

    if resp_data:
        total_formed_data = []
        for i in range(len(resp_data)):
            event_city = resp_data[i]['event info'][0]['city']
            event_name = resp_data[i]['event info'][0]['event name']
            event_desc = resp_data[i]['event info'][0]['description']
            event_end_date = resp_data[i]['event info'][0]['end date']
            event_end_time = resp_data[i]['event info'][0]['end time']
            event_venue_name = resp_data[i]['event info'][0]['address 1']
            event_address = resp_data[i]['event info'][0]['full address']
            event_start_date = resp_data[i]['event info'][0]['start date']
            event_start_time = resp_data[i]['event info'][0]['start time']
            if resp_data[i]['ercess partners categories'] == []:
                event_category = None
            else:
                event_category = resp_data[i]['ercess partners categories'][0]['partner category']
            ticket_adapter_obj = ticket_adapter()[i][event_name]

            # import ipdb; ipdb.set_trace()
            base_template = {'title': event_name,
                             'description': event_desc,
                             'descriptionSections': [],
                             'bookingText': 'Book Tickets',
                             'participants': [],
                             'ehPrices': ticket_adapter_obj,
                             'ehPricesDisplayCount': 1,
                             'images': [image_url[event_name]],
                             'imageData': [json.dumps({"source_url":image_url[event_name],"original_image_url":image_url[event_name],"processed_image_url":image_url[event_name],"resized_image_url":image_url[event_name],"google_serving_url":image_url[event_name],"image_width":1000,"image_height":587,"image_size":547375,"dominant_color":"17 30 69","image_credits":""})],
                             'categories': [event_category],
                             'cats': ['adventure and sports'],
                             'subcategories': ['boating'],
                             'durations': [{

                                 # 'startDateTime': int(str(int(time.mktime(time.strptime(event_start_date+' '+minute_change(event_start_time[:-3]),
                                 #                                                        '%Y-%m-%d %H:%M:%S'))))+'000'),
                                 # 'endDateTime': int(str(int(time.mktime(time.strptime(event_end_date+' '+minute_change(event_end_time[:-3]),
                                 #                                                      '%Y-%m-%d %H:%M:%S'))))+'000'),
                                 # 'startDateTime': int(str(int(time.mktime(
                                 #     time.strptime(event_start_date + ' ' + event_start_time[:-3],
                                 #                   '%Y-%m-%d %H:%M:%S')))) + '000'),
                                 # 'endDateTime': int(str(int(time.mktime(
                                 #     time.strptime(event_end_date + ' ' + event_end_time[:-3],
                                 #                   '%Y-%m-%d %H:%M:%S')))) + '000'),

                                 'startDateTime': int(datetime_to_iso(event_start_date + event_start_time[:-3])),
                                 'endDateTime': int(datetime_to_iso(event_end_date + event_end_time[:-3])),

                                 'isTicketingEnabled': True,
                                 'isNewlyAdded': True}],
                             'isEverGreen': True,
                             'isPublished': True,
                             'ehPriceAddons': [],
                             'additionalFields': [],
                             'acn': 2,
                             'ascn': 4,
                             'participantsText': '',
                             'filesUploading': {},
                             'city': event_city,
                             'venue': event_venue_name,
                             'address': event_address,
                             'latLng': [19.9999859, 73.78280399999994],
                             'ehPriceSearchTerm': '',
                             'chargeConvenienceFee': False,
                             'questionsTemplate': None,
                             'addEventSource': 'diy_web',
                             'isEventSubjectedToReview': False,
                             'sectionsSubjectedToReview': ''}
            total_formed_data.append(base_template)

    else:
        return False

    return total_formed_data