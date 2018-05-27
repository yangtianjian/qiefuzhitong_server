from flask import Flask, request
from lib import sms
from lib import redis_service
from lib import mongo_service
from lib import models
from PIL import Image
import numpy as np
import json
from resnet23 import train_res23
from d_resnet import D_ResNet_Train
import uuid

app = Flask(__name__)

@app.route('/get_verification_code', methods=['post'])
def get_verification_code():
    phone_number = request.form['phone_number']
    #sms_status = sms.send_verification_code(phone_number)
    #if sms_status['errno'] == 0:
    if True:
        # verification_code = sms_status['code']
        verification_code = '123456'
        redis_service.store_verification_code_with_phone_number(verification_code, phone_number)
        return json.dumps({'errno': 0, 'verification_code': verification_code})
    else:
        return json.dumps({'errno': 1})

@app.route('/check_login_state', methods=['post'])
def check_login_state():
    token = request.form['token']
    result = redis_service.is_token_correct(token)
    if result['errno'] == 0:
        return json.dumps({'errno': 0, 'user_name': mongo_service.get_user_name_by_phone_number(result['phone_number'])})
    else:
        return json.dumps({'errno': 1})
 
@app.route('/login', methods=['post'])
def login():
    phone_number = request.form['phone_number']
    serial_number = request.form['serial_number']
    verification_code = request.form['verification_code']
    if redis_service.is_verification_code_with_phone_number_correct(verification_code, phone_number):
        mongo_service.create_user_by_phone_number(phone_number)
        token = redis_service.generate_token(serial_number, phone_number)
        return json.dumps({'errno': 0, 'token': token, 'user_name': mongo_service.get_user_name_by_phone_number(phone_number)})
    else:
        return json.dumps({'errno': 2})

@app.route('/recognition', methods=['post'])
def recognition():
    image = request.files['image']
    image_path = 'tmpdata/' + str(uuid.uuid1())
    image.save(image_path)
    image = Image.open(image_path).resize((128,128))
    data = np.asarray(image.convert('RGB'), dtype='float32')
    data = np.transpose(data/255)
    data = np.asarray([data])
    class_no = models.get_disease_class_no(train_res23.predict_disease(data))
    disease_info = mongo_service.get_disease_by_disease_class_no(class_no)
    return json.dumps(disease_info)
    
@app.route('/update_monitor', methods=['post'])
def update_monitor():
    token = request.form['token']
    monitor_name = request.form['monitor_name']
    image = request.files['image']
    image_path = 'data/' + str(uuid.uuid1())
    image.save(image_path)
    phone_number = redis_service.get_phone_number_by_token(token)
    pics = mongo_service.save_monitor_pic_and_get_pics(phone_number, monitor_name, image_path)
    if len(pics) >= 2:
        image_path1, image_path2 = pics[-2], pics[-1]
        image1 = Image.open(image_path1).resize((128,128))
        data1 = np.asarray(image1.convert('RGB'), dtype='float32')
        data1 = np.transpose(data1/255)
        data1 = np.asarray([data1])
        image2 = Image.open(image_path2).resize((128,128))
        data2 = np.asarray(image1.convert('RGB'), dtype='float32')
        data2 = np.transpose(data2/255)
        data2 = np.asarray([data2])
        data = [data1, data2]
        data = np.asarray(data)
        result = D_ResNet_Train.trend_predict(data)
        class_no = models.get_trend_class_no(result)
        if class_no == 0:
            trend = 'up'
        else:
            trend = 'down'
        mongo_service.update_trend(phone_number, monitor_name, trend)
    return json.dumps({'errno': 0})


@app.route('/update_user_name', methods=['post'])
def update_user_name():
    token = request.form['token']
    new_user_name = request.form['new_user_name']
    phone_number = redis_service.get_phone_number_by_token(token)
    mongo_service.update_user_name_by_phone_number(phone_number, new_user_name)
    return json.dumps({'errno': 0, 'user_name': new_user_name})

@app.route('/update_phone_number', methods=['post'])
def update_phone_number():
    old_phone_number = request.form['old_phone_number']
    new_phone_number = request.form['new_phone_number']
    old_verification_code = request.form['old_verification_code']
    new_verification_code = request.form['new_verification_code']
    if not redis_service.is_verification_code_with_phone_number_correct(old_phone_number, old_verification_code):
        return json.dumps({'errno': 2})
    if not redis_service.is_verification_code_with_phone_number_correct(new_phone_number, new_verification_code):
        return json.dumps({'errno': 2})
    mongo_service.update_phone_number(old_phone_number, new_phone_number)
    return json.dumps({'errno': 0})

@app.route('/add_monitor', methods=['post'])
def add_monitor():
    token = request.form['token']
    phone_number = redis_service.get_phone_number_by_token(token)
    monitor_name = request.form['monitor_name']
    monitor_description = request.form['monitor_description']
    return json.dumps(mongo_service.add_monitor(phone_number, monitor_name, monitor_description))

@app.route('/get_monitors', methods=['post'])
def get_monitors():
    token = request.form['token']
    phone_number = redis_service.get_phone_number_by_token(token)
    return json.dumps(mongo_service.get_monitors_by_phone_number(phone_number))

@app.route('/del_monitor', methods=['post'])
def del_monitor():
    token = request.form['token']
    monitor_name = request.form['monitor_name']
    phone_number = redis_service.get_phone_number_by_token(token)
    return json.dumps(mongo_service.del_monitor_by_phone_number_and_monitor_name(phone_number, monitor_name))

app.run("0.0.0.0", 80)
