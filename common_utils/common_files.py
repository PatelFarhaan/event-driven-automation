from datetime import datetime
from mysql.connector import pooling


connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                              pool_size=20,
                                              pool_reset_session=True,
                                              host='localhost',
                                              database='farhaan',
                                              user='root',
                                              password='***REMOVED_PASSWORD***')

def get_conn():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    return connection_object, cursor


def std_time(string):
    resp = string.split(':')
    result = ''

    for i in resp:
        if len(i) != 2:
            i = '0'+i+':'
        else:
            i = i + ':'
        result+= i
    return result[:-1]


def events_write_process():

    connection_object, cursor = get_conn()

    sql1 = """SELECT event_status_on_channel.event_id, partner_sites.table_id, partner_sites.site_name, event_status_on_channel.table_id 
            FROM event_status_on_channel 
            INNER JOIN partner_sites 
            ON event_status_on_channel.site_id = partner_sites.table_id 
            WHERE event_status_on_channel.promotion_status = 'ready to upload' AND partner_sites.method = 'manual'"""
    try:
        cursor.execute(sql1)
        data1 = cursor.fetchall()
        f = open('common_utils/event_details.txt', 'w')
        for info1 in data1:
            eventid = info1[0]
            siteid = info1[1]
            sitename = info1[2]
            res = (str(eventid)+','+str(siteid)+','+str(sitename)+'\n')
            f.write(res)

    except Exception as e:
        print('Something went wrong while fetching from event_status_on_channel')
        print(e)

    cursor.close()
    connection_object.close()



def main_process(event_id,site_id,response=None,index=None):

    connection_object, cursor = get_conn()
    main_json = {}
    users_list = []
    topics_list = []
    tickets_list = []
    articles2_list = []
    questions_list = []
    ticket_discount_list = []
    attendee_form_options_list = []
    ercess_partners_categories_list = []
    status_promotion_ticketing_list = []

    sql = """SELECT * FROM articles2 WHERE id ='%d'""" %event_id
    try:

        cursor.execute(sql)
        data = cursor.fetchall()
        for info in data:
            eventid = info[0]
            countryname = info[1]
            eventname = info[2]
            profileimg = info[5]
            banner0 = info[6]
            sdate = str(info[8])[:10]
            edate = str(info[9])[:10]
            addr1 = info[10]
            addr2 = info[11]
            pincode = info[12]
            full_address = info[16]
            state = info[13]
            city = info[14]

            # import ipdb;
            # ipdb.set_trace()

            stime = std_time(str(info[19]))

            s_time = datetime.strptime(stime,"%H:%M:%S")
            stime = s_time.strftime("%I:%M:%S %p")

            etime = std_time(str(info[20]))

            e_time = datetime.strptime(etime,"%H:%M:%S")
            etime = e_time.strftime("%I:%M:%S %p")


            description = info[21]

            articles2 = {"event id":eventid, "country":countryname, "event name":eventname, "profile image":profileimg, "banner":banner0, "start date":sdate,
                         "end date":edate, "address 1":addr1, "address 2":addr2, "pincode":pincode, "full address":full_address, "state":state, "city":city,
                         "start time":stime, "end time":etime, "description":description}
            articles2_list.append(articles2)

        main_json['event info'] = articles2_list
    except Exception as e:
        print('Something went wrong while fetching from articles2 table.')
        print(e)


    #tickets
    # import ipdb; ipdb.set_trace()
    sql1 = """SELECT * FROM tickets WHERE event_id = '%d' and active = 1""" %event_id
    tkt_qty_sum = 0
    try:
        cursor.execute(sql1)
        data1 = cursor.fetchall()
        for info1 in data1:
            tktid = info1[0]
            eventid1 = info1[1]
            tktname = info1[2]
            original_tkt_price = info1[3]
            other_charges = info1[4]
            other_charges_type = info1[5]
            tkt_qty = info1[6]
            min_qty = info1[7]
            max_qty = info1[8]
            qty_left = info1[9]
            ticket_msg = info1[10]
            if other_charges == '':
                other_charges = 0


            ticket_start_date = str(info1[11])[:10]

            ticket_start_time = str(info1[11])[11:]


            expiry_date = str(info1[12])[:10]
            expiry_time = str(info1[12])[11:]

            ticket_label= info1[13]
            active1 = info1[14]

            tkt_price = original_tkt_price
            tkt_qty_sum+= tkt_qty
            if other_charges_type == 1:
                tkt_price = str(int(original_tkt_price) + int(other_charges))
            elif other_charges_type == 2:
                tkt_price = str(int(original_tkt_price) * (1 + (int(other_charges) / 100)))

            if other_charges_type == 1:
                other_charges_type = 'flat'
            if other_charges_type == 2:
                other_charges_type = 'percent'

            if active1 == 1:
                active1 = 'active'
            else:
                active1 = 'inactive'

            tickets ={"ticket id": tktid, "ticket name":tktname, "original ticket price":original_tkt_price,"ticket price":tkt_price,"other charges":other_charges,"other charges type":other_charges_type,
                      "ticket quantity":tkt_qty, "minimum quantity":min_qty, "maximum quantity":max_qty, "quantity left":qty_left, "ticket message":ticket_msg,
                      "ticket start date":ticket_start_date, "ticket start time": ticket_start_time, "expiry date":expiry_date, "expiry time": expiry_time, "ticket label":ticket_label, "active":active1}
            tickets_list.append(tickets)

            ## ticket discounts
            sql2 = """SELECT * FROM `ticket_discounts` WHERE event_id ='%d' AND ticket_id = '%d'""" %(eventid1, tktid)
            try:
                cursor.execute(sql2)
                data2 = cursor.fetchall()
                for info2 in data2:
                    tableid2 = info2[0]
                    eventid2 = info2[1]
                    ticketid2 = info2[2]
                    coupon = info2[3]
                    discountamt = info2[4]
                    discounttype = info2[5]
                    discountstart = info2[6]
                    discountend = info2[7]
                    active2 = info2[8]

                    ticket_discount = {"table_id": tableid2, "coupon": coupon,"discount amount":discountamt, "discount type":discounttype,
                                       "discount start":discountstart, "discount end":discountend, "active":active2}
                    ticket_discount_list.append(ticket_discount)

                main_json['tickets'] = ticket_discount_list

            except Exception as e:
                print('Something went wrong while fetching from discount table.')
                print(e)

        tickets_list.append({'capacity': tkt_qty_sum})
        main_json['tickets'] = tickets_list

    except Exception as e:
        print('Something went wrong while fetching from tickets table.')
        print(e)


    #categories of events
    sql3 = """SELECT categorized_events.category_id, categorized_events.topic_id, categories.category FROM categorized_events INNER JOIN categories WHERE categorized_events.category_id = categories.category_id """
    try:
        cursor.execute(sql3)
        data3 = cursor.fetchall()
        for info3 in data3:
            categoryid3 = info3[0]
            topic_id3 = info3[1]
            category3 = info3[2]

            json_3 = {"category id":categoryid3, "topic id":topic_id3, "category name":category3}

            sql4 = """SELECT * FROM topics WHERE topics_id ='%s'""" % topic_id3
            cursor.execute(sql4)
            data4 = cursor.fetchall()
            for info4 in data4:
                topic4 = info4[1]
                caterg4 = info4[2]


                if topic4 == None:
                    topic4 = ''
                else:
                    json_4 = {"topic": topic4}

                    topics_list.append(json_4)

        main_json['categories of events'] = topics_list
    except Exception as e:
        print('Something went wrong while fetching from categorized_events table.')
        print(e)


    #status promotion ticketing
    sql5 = """SELECT * FROM status_promotion_ticketing WHERE event_id ='%d'""" %event_id
    try:
        cursor.execute(sql5)
        data5 = cursor.fetchall()
        for info5 in data5:
            sptkt_id = info5[0]
            eventid5 = info5[1]
            private5 = info5[4]
            ticketing = info5[8]
            connected_user = info5[10]

            if private5 == 0:
                private5 = 'public'
            elif private5 == 1:
                private5 = 'private'

            if ticketing == 0:
                ticketing = 'free'
            elif ticketing == 1:
                ticketing = 'paid'

            status_promotion_ticketing = {"private":private5, "ticketing":ticketing, "connected user":connected_user}
            status_promotion_ticketing_list.append(status_promotion_ticketing)

        main_json['status promotion ticketing'] = status_promotion_ticketing_list
    except Exception as e:
        print('Something went wrong while fetching from status_promotion_ticketing table.')
        print(e)

    # import ipdb; ipdb.set_trace()
    # attendees
    sql6="""SELECT * FROM attendee_form_builder WHERE event_id ='%d'""" %event_id
    try:
        cursor.execute(sql6)
        data6 = cursor.fetchall()
        for info6 in data6:
            qts_id6 = info6[0]
            qts_title6 = info6[2]
            qts_type6 = info6[3]
            qts_acces6 = info6[4]

            if qts_acces6 == 1:
                qts_acces6 = 'mandatory'
            elif qts_acces6 == 2:
                qts_acces6 = 'optional'

            json_6 = {"question id":qts_id6, "question title":qts_title6, "question type":qts_type6, "question accessibility":qts_acces6}

            sql7 ="""SELECT * FROM `attendee_form_types` WHERE type_id = '%d'""" %qts_type6
            try:
                cursor.execute(sql7)
                data7 = cursor.fetchall()
                for info7 in data7:
                    name7 = info7[1]

                    json_6['name'] = name7

                    sql8 = """ SELECT * FROM `attendee_form_options` WHERE event_id = '%d' AND ques_id = '%d'""" %(event_id,qts_id6)
                    # print(sql8)
                    try:
                        cursor.execute(sql8)
                        data8 = cursor.fetchall()
                        for info8 in data8:
                            option_id8 = info8[0]
                            option_name8 = info8[3]

                            attendee_form_options = {'option id':option_id8, "option name":option_name8}
                            attendee_form_options_list.append(attendee_form_options)
                    except Exception as e:
                        print('Something went wrong while fetching from attendee_form_options table.')
                        print(e)

            except Exception as e:
                print('Something went wrong while fetching from attendee_form_types table.')
                print(e)


        main_json['attendees'] = attendee_form_options_list
    except Exception as e:
        print('Something went wrong while fetching from attendee_form_builder table.')
        print(e)


    # users
    sql9 = """SELECT * FROM users"""
    try:
        cursor.execute(sql9)
        data9 = cursor.fetchall()
        for info9 in data9:
            frstnme9 = info9[3]
            lastnme9 = info9[4]
            user9 = info9[5]
            mobile9 = info9[6]

            users ={'first name': frstnme9, 'last name': lastnme9, 'user': user9, 'mobile no': mobile9}
            users_list.append(users)

        main_json['users'] = users_list
    except Exception as e:
        print('Something went wrong while fetching from users table.')
        print(e)


    # ercess partners categories
    sql10 = """SELECT * FROM ercess_partners_categories WHERE ercess_category = '%d' and partner_id = '%d'""" %(categoryid3, site_id)
    try:
        cursor.execute(sql10)
        data10 = cursor.fetchall()
        for info10 in data10:
            ercess_catgry = info10[1]
            partner_catgry = info10[2]
            partner_id = info10[3]

            ercess_partners_categories = {'ercess category': ercess_catgry, 'partner category':partner_catgry, 'partner id':partner_id}
            ercess_partners_categories_list.append(ercess_partners_categories)

        main_json['ercess partners categories'] = ercess_partners_categories_list
    except Exception as e:
        print('Something went wrong while fetching from ercess_partners_categories table.')
        print(e)

    cursor.close()
    connection_object.close()

    if not (response and index) == None:
        response[index] = main_json
    else:
        return main_json


def respective_sites_event_details():

    events_write_process()
    doattend = open('sites/doattend/event_details.txt', 'w+')
    event_high = open('sites/eventhigh/event_details.txt', 'w+')
    event_brite = open('sites/eventbrite/event_details.txt', 'w+')
    town_script = open('sites/townscript/event_details.txt', 'w+')
    with open('common_utils/event_details.txt', 'r') as f:
        event_details = f.readlines()

    for i in event_details:
        temp = i.replace('\n', '')
        temp = tuple(temp.split(','))
        if temp[1] == '7':
            res = (str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + '\n')
            event_high.write(res)
        if temp[1] == '1':
            res = (str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + '\n')
            town_script.write(res)
        if temp[1] == '13':
            res = (str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + '\n')
            event_brite.write(res)
        if temp[1] == '16':
            res = (str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + '\n')
            doattend.write(res)

    doattend.close()
    event_high.close()
    event_brite.close()
    town_script.close()