from mysql.connector import pooling


def get_conn():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    return connection_object, cursor


connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                              pool_size=20,
                                              pool_reset_session=True,
                                              host='localhost',
                                              database='farhaan',
                                              user='root',
                                              password='***REMOVED_PASSWORD***')


def update_datebase(event_id):
    connection_object, cursor = get_conn()
    try:
        query = """UPDATE event_status_on_channel SET promotion_status='published' WHERE event_id={0};""".format(event_id)
        cursor.execute(query)
        connection_object.commit()
        cursor.close()
        connection_object.close()
        return True
    except:
        return False


def get_event_id(event_name):
    connection_object, cursor = get_conn()

    try:
        query = """SELECT id FROM articles2 WHERE event_name = '{0}';""".format(event_name)
        cursor.execute(query)
        data = cursor.fetchall()
        event_id = data[0][0]
        resp = update_datebase(event_id)
        cursor.close()
        connection_object.close()
        print(event_name)
        return resp
    except:
        return False