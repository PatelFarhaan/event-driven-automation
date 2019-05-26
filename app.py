import logging
import threading
# from sites.doattend.app import doattend_post_data
from sites.eventbrite.app import eventbrite_post_data
from sites.eventhigh.data_posting import eventhigh_post_data
from sites.townscript.data_posting import townscript_post_data
# from sites.eventseeker.data_posting import eventseeker_post_data
from common_utils.common_files import respective_sites_event_details



if __name__ == '__main__':
    logger = logging.basicConfig(filename='EventsLog.log',
                                 filemode='a',
                                 level=logging.DEBUG,
                                 format='%(asctime)s, %(name)s, %(levelname)s, %(message)s')

    threads = []
    events = [eventbrite_post_data, eventhigh_post_data, townscript_post_data]
    respective_sites_event_details()
    for i in events:
        t = threading.Thread(target=i, args=())
        threads.append(t)
        t.start()

    for j in threads:
        j.join()