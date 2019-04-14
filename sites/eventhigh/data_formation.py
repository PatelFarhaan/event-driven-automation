import json
from datetime import datetime
from sites.eventhigh.main_resp import main_dict
from sites.eventhigh.google_image import implicit


ticket_ids = []
event_ticket_ids = {}
resp_data = main_dict()


def datetime_to_iso(string_date):
    string_date = string_date[:10]+' '+string_date[10:]
    resp = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    resp = datetime.timestamp(resp)
    return resp

def tickets_str_to_date(string_date):
    string_date = string_date[:10]+' '+string_date[10:]
    resp = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    return resp.date()


def tickets_str_to_time(string_date):
    string_date = string_date[:10]+' '+string_date[10:]
    resp = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    return resp.time()

def tickets_str_to_timestamp(string_date):
    string_date = string_date[:10]+' '+string_date[10:]
    resp = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    resp = datetime.timestamp(resp)
    return resp


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
                    'isExpanded': True,
                    'price': i[ticket_event_name][j]['ticket_class']['cost'],
                    'name': i[ticket_event_name][j]['ticket_class']['name'],
                    'validityStartDate': str(tickets_str_to_date(i[ticket_event_name][j]['ticket_class']['sales_start'])),
                    'validityStartOptionAmPm': 'am' if tickets_str_to_time(
                        i[ticket_event_name][j]['ticket_class']['sales_start']).hour > 12 else 'pm',
                    'validityEndDate': str(tickets_str_to_date(i[ticket_event_name][j]['ticket_class']['sales_end'])),
                    'validityEndOptionAmPm': 'am' if tickets_str_to_time(i[ticket_event_name][j]['ticket_class']['sales_end']).hour > 12 else 'pm',
                    'rank': 1,
                    'validityStart': float(tickets_str_to_timestamp(i[ticket_event_name][j]['ticket_class']['sales_start'])),
                    'validityEnd': float(tickets_str_to_timestamp(i[ticket_event_name][j]['ticket_class']['sales_end']))

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
            base_template = {'title': event_name,
                             'description': event_desc,
                             'descriptionSections': [],
                             'bookingText': 'Book Tickets', #test
                             'participants': [],
                             'ehPrices': ticket_adapter_obj,
                             'ehPricesDisplayCount': 1,
                             'images': [image_url],
                             'imageData': [json.dumps({"source_url":image_url,"original_image_url":image_url,"processed_image_url":image_url,"resized_image_url":image_url,"google_serving_url":image_url,"image_width":1000,"image_height":587,"image_size":547375,"dominant_color":"17 30 69","image_credits":""})],
                             'categories': [event_category], #test event_categories
                             'cats': ['adventure and sports'], #test
                             'subcategories': ['boating'], #test
                             'durations': [{'startDateTime': float(datetime_to_iso(event_start_date+event_start_time[:-3])),
                                            'endDateTime': float(datetime_to_iso(event_end_date + event_end_time[:-3])),
                                            'isTicketingEnabled': True,
                                            'isNewlyAdded': True}],
                             'isEverGreen': False,
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