import json
import threading
from sites.eventseeker.login_crawl import login
from sites.eventseeker.data_formation import formed_data
import urllib.parse


import warnings
warnings.filterwarnings("ignore")

def multi_thread_posting(payload, sess):

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://eventseeker.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    data_structure_venue = {
        'call': 'create_url_venue',
        'rand_num': 'FDCjMcU',
        'alreadyTempId': '',
        'form_data': None, #encoded data will be here
        'venueId': '',
        'fromWhere': 'fromEvent',
        'userwantsToContinue': '1',
        'refer_from': 'ugc_event'
    }
    data_structure_event = {
        'call': 'create_url_event',
        'rand_num': '8XFl8og',
        'alreadyTempId': '',
        'form_data': None,
        'eventId': '',
        'fromWhere': 'draft',
        'whichServer': 'ugc',
        'start_time': '16:30:10',
        'end_time': '21:0:10'
    }
    #fetch city id to be used in form data
    citydata = {'fromWhere': 'ugcEvent'}
    cityurl = "https://eventseeker.com/"+str(payload[1]['city']).strip() +"/ugc-v"
    payload[0]['venueCityId'] = sess.post(cityurl, data=citydata,headers = headers).json()['data']['cityId']

    #create nested encoded data
    form_data_encoded_venue = urllib.parse.urlencode(payload[0])
    form_data_encoded_event = urllib.parse.urlencode(payload[1])
    data_structure_venue['form_data'] = form_data_encoded_venue
    data_structure_event['form_data'] = form_data_encoded_event


    #creating venue and event
    url = 'https://eventseeker.com/ajaxcalls'
    venue_response = sess.post(url,headers = headers, data=data_structure_venue)

    event_response = sess.post(url, headers = headers, data=data_structure_event)
    try:
        eventid = event_response.json()['last_id']['$id']
    except: pass

    print("EVENTSEEKER Processing Done!!!")

def eventseeker_post_data():
    threads = []
    resp, sess = login()
    payloads = formed_data()

    if payloads:
        if resp.status_code == 200:
            for i in payloads:
                t = threading.Thread(target=multi_thread_posting, args=(i, sess))
                threads.append(t)
                t.start()

            for j in threads:
                j.join()
    else:
        print("No Events for EVENTSEEKER!!!")