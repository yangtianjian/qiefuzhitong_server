# -*- coding: utf-8 -*-
import sys
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid
import json
import random
from aliyunsdkcore.profile import region_provider

reload(sys)
sys.setdefaultencoding('utf8')

REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

ACCESS_KEY_ID = "LTAIGZfNVaBMawpy"
ACCESS_KEY_SECRET = "KAVIunyHCO95M5PJyAJ1RlP7DDFkbb"

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME,REGION,DOMAIN)

def send_verification_code(phone_numbers):

    code = str(random.randint(100000, 999999))
    sign_name = "切肤知痛"
    template_code = "SMS_126610408"
    template_param = json.dumps({"code": code})
    business_id = uuid.uuid1()

    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name);

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理
    smsResponse = json.loads(smsResponse)
    if smsResponse[u'Code'] == u'OK':
        return {'errno': 0, 'code': code}
    else:
        return {'errno': 1}
