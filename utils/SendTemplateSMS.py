#-*- coding: UTF-8 -*-  

from .CCPRestSDK import REST
import configparser

#主账号
accountSid = '8a216da86cdb6950016ce026845d02a1'

#主账号Token
accountToken = '297b78d42a2640aa90f50eb29465a7b0'

#应用Id
appId ='8a216da86cdb6950016ce026858f02a8'

#请求地址，格式如下，不需要http://
serverIP = 'app.cloopen.com'

#端口
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送短信
  # @param to 手机号
  # @param datas 数据内容  格式为数组如{'12','34'} 不需要用''替换
  # @param $tempId 模板Id

def send_template_SMS(to,datas,tempId):
    print('test')
    #初始化REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)
    
    return rest.sendTemplateSMS(to,datas,tempId)


if __name__ == '__main__':
    #sendTemplateSMS(手机号码,内容数据,模板Id)
    #测试模板ID为1
    #【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入
    #测试模板数据内容格式为 {'分钟','验证码'}
    send_template_SMS('18667018590',{'3','1234'},1)
    # send_template_SMS('13091463622', {'3','1234'}, 1)