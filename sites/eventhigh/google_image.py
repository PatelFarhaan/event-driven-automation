import os
import shutil
import urllib
import threading
from gcloud import storage
from urllib.request import urlopen
from sites.eventhigh.main_resp import main_dict


image_file = 'sites/eventhigh/temp_images/'


def image_downloading (event_name, img_folder, img_link, all_downloaded_links):
    resp = True
    try:
        urllib.request.urlretrieve(img_link, img_folder)
    except:
        resp = False

    all_downloaded_links[event_name] = resp


def download_media_file():
    resp_data = main_dict()
    threads = []
    all_downloaded_links = {}

    if os.path.exists(image_file):
        shutil.rmtree(image_file)

    if not os.path.exists(image_file):
        os.makedirs(image_file)

    for index, i in enumerate(resp_data):  #to check
        event_name = i['event info'][0]['event name']
        img_folder = image_file + "{0}.png".format(event_name)
        img_link = 'https://ercess.com' + i['event info'][0]['banner']
        t = threading.Thread(target=image_downloading,
                             args=(event_name, img_folder, img_link, all_downloaded_links))
        threads.append(t)
        t.start()

    for j in threads:
        j.join()

    return all_downloaded_links


def image_uploading(image_name, all_uploaded_images):
    try:
        bucket_name = 'eventhigh_images'
        object_name = image_name
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        image_name = image_file+image_name+'.png'
        blob.upload_from_filename(filename=image_name, content_type='image/jpeg')
        blob.make_public()
        all_uploaded_images[object_name] = blob.public_url
    except:
        all_uploaded_images[object_name] = False

    return all_uploaded_images


def implicit():
    resp = download_media_file()
    all_uploaded_images = {}
    threads = []

    for index, ele in enumerate(resp):
        t = threading.Thread(target=image_uploading, args=(ele, all_uploaded_images))
        threads.append(t)
        t.start()

    for j in threads:
        j.join()

    return all_uploaded_images