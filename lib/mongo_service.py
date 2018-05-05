from pymongo import MongoClient
import uuid
import time

def get_conn():
    return MongoClient('127.0.0.1', 27017)

def get_db():
    return get_conn()['intel']

def get_user_name_by_phone_number(phone_number):
    user_collection = get_db()['user']
    return user_collection.find_one({'phone_number': phone_number})['user_name']

def create_user_by_phone_number(phone_number):
    user_collection = get_db()['user']
    resp = user_collection.find_one({'phone_number': phone_number})
    if resp is None:
        user_collection.insert_one({
            'user_id': str(uuid.uuid1()),
            'user_name': phone_number,
            'phone_number': phone_number,
            'reports':[],
            'monitors':{}
        })

def update_user_name_by_phone_number(phone_number, user_name):
    user_collection = get_db()['user']
    resp = user_collection.update_one(
        {'phone_number': phone_number},
        {'$set': {'user_name': user_name}})

def update_phone_number(old_phone_number, new_phone_number):
    user_collection = get_db()['user']
    resp = user_collection.update_one({'phone_number': old_phone_number},{'$set':{'phone_number': new_phone_number}})

def generate_report_by_phone_number(phone_number, report):
    report_id = str(uuid.uuid1())
    report_collection = get_db()['report']
    user_collection = get_db()['user']
    user_resp = report_collection.find_one({'phone_number': phone_number})
    reports = user_resp['reports']
    reports.append(report_id)
    user_collection.update_one(
        {'phone_number': phone_number},
        {'$set': {'reports': reports}}
    )
    report.update_one('report_id', report_id)
    report_collection.insert_one(report)

def get_report(report_id):
    report_collection = get_db()['report']
    resp = report_collection.find_one({'report_id': report_id})
    return resp

def add_monitor(phone_number, monitor_name, monitor_description):
    monitor_id = str(uuid.uuid1())
    user_collection = get_db()['user']
    monitor_collection = get_db()['monitor']
    resp = user_collection.find_one({'phone_number': phone_number})
    if monitor_name in resp['monitors']:
        return {'errno': 1}
    monitors = resp['monitors']
    monitor = {'trend': 'unknown', 'pic_list': [], 'monitor_name': monitor_name, 'monitor_description': monitor_description, 'analysis': '',
               'time': time.strftime("%Y/%m/%d", time.localtime(time.time()))}
    monitor.update({'monitor_id': monitor_id})
    monitors.update({monitor_name: monitor_id})
    user_collection.update_one({'phone_number': phone_number}, {'$set':{'monitors':monitors}})
    monitor_collection.insert_one(monitor)
    return {'errno': 0}

def update_trend(phone_number, monitor_name, trend):
    user_collection = get_db()['user']
    monitor_collection = get_db()['monitor']
    resp = user_collection.find_one({'phone_number': phone_number})
    monitors = resp['monitors']
    monitor_id = monitors[monitor_name]
    monitor_collection.update_one({'monitor_id': monitor_id}, {'$set': {'trend': trend}})

def get_monitors_by_phone_number(phone_number):
    user_collection = get_db()['user']
    monitor_collection = get_db()['monitor']
    resp = user_collection.find_one({'phone_number': phone_number})
    monitors = resp['monitors']
    result = []
    for monitor_id in monitors.values():
        monitor = monitor_collection.find_one({'monitor_id': monitor_id})
        del monitor['_id']
        result.append(monitor)
    return result

def del_monitor_by_phone_number_and_monitor_name(phone_number, monitor_name):
    user_collection = get_db()['user']
    monitor_collection = get_db()['monitor']
    resp = user_collection.find_one({'phone_number': phone_number})
    monitors = resp['monitors']
    monitor_id = monitors[monitor_name]
    del monitors[monitor_name]
    user_collection.update_one({'phone_number': phone_number}, {'$set':{'monitors':monitors}})
    monitor_collection.delete_one({'monitor_id': monitor_id})

def get_disease_by_disease_class_no(class_no):
    disease_collection = get_db()['disease']
    result = disease_collection.find_one({'class_no': class_no})
    del result['_id']
    return result

def save_monitor_pic_and_get_pics(phone_number, monitor_name, image_path):
    user_collection = get_db()['user']
    monitor_collection = get_db()['monitor']
    resp = user_collection.find_one({'phone_number': phone_number})
    monitors = resp['monitors']
    monitor_id = monitors[monitor_name]
    monitor = monitor_collection.find_one({'monitor_id': monitor_id})
    monitor['pic_list'].append(image_path)
    monitor_collection.update_one({'monitor_id': monitor_id}, {'$set': {'time': time.strftime("%Y/%m/%d", time.localtime(time.time())), 'pic_list': monitor['pic_list']}})
    return monitor['pic_list']
