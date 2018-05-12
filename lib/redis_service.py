import redis
import uuid

def get_redis_conn():
    return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

def store_verification_code_with_phone_number(verification_code, phone_number):
    r = get_redis_conn()
    r.set("vcode" + phone_number, verification_code, 300)

def is_verification_code_with_phone_number_correct(verification_code, phone_number):
    r = get_redis_conn()
    return verification_code == r.get("vcode" + phone_number)

def generate_token(serial_number, phone_number):
    token = serial_number
    r = get_redis_conn()
    r.set(token, phone_number)
    r.set(phone_number, token)
    return token

def is_token_correct(token):
    '''For easily login, one account only support one device'''
    r = get_redis_conn()
    '''Check whether token register or not'''
    phone_number = r.get(token)
    if phone_number:
        serial_number = r.get(phone_number)
        if serial_number == token:
            return {'errno': 0, 'phone_number': phone_number}
        else:
            return {'errno': 1}
    else:
        return {'errno': 1}

def get_phone_number_by_token(token):
    r = get_redis_conn()
    phone_number = r.get(token)
    return phone_number
