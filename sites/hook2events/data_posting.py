import json
import threading
from sites.hook2events.login_crawl import login
from sites.hook2events.data_formation import formed_data

##used ignoring ssl warnings
import warnings
warnings.filterwarnings("ignore")

def multi_thread_posting(payload, sess):

        headers = {
            'Origin': 'https://www.hook2events.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.hook2events.com/signin',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }
        url = 'https://www.hook2events.com/addPublicEvent.php'
        response = sess.post(url,verify = False,headers = headers, data=json.dumps(payload))
        eventid = response.json()['last_id']['$id']

        headers['Referer'] = 'https://www.hook2events.com/edit-event.php?event_id='+eventid
        #image
        print("Hook2events Processing Done!!!")

def hook2events_post_data():
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
        print("No Events for HOOK2EVENTS!!!")