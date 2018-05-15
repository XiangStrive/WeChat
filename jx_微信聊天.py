# -*- coding:utf-8 -*-
# 时间 2018/5/14 14:19
# 说明：day01
import itchat
import threading
import requests
import time


class WeiXinMsg(object):
    def __init__(self):
        # 登录不需要重复扫码
        itchat.auto_login(hotReload=True)
        # 好友列表
        self.friends = itchat.get_friends(update=True)[0:]

    @staticmethod
    def tuling_register(msg):
        """图灵机器人接口"""
        apiUrl = 'http://www.tuling123.com/openapi/api'
        data = {
            'key': '8edce3ce905a4c1dbb965e6b35c3834d',  # 到图灵官网可以注册一个
            'info': msg,  # msg['Text']获取微信接收到的消息 然后发给图灵机器人
            'userid': 'wechat-robot',  # 这里你想改什么都可以
        }
        # 我们通过如下命令发送一个post请求
        data = requests.post(apiUrl, data=data).json()

        # 图灵机器人回复的内容返回给发送者
        return data["text"]

    def recv(self):
        """接收消息"""
        @itchat.msg_register(itchat.content.TEXT)  # 注册收听类型还有文件、图片、视频类型
        def get_msg(msg):  # msg是发送的全部信息
            gender = msg["User"]["Sex"]
            if gender == 1:
                gender = "男"
            elif gender == 2:
                gender = "女"
            else:
                gender = "保密"
            message = {
                "name": msg["User"]["RemarkName"],
                "gender": gender,
                "content": msg["Text"],
                "date": time.strftime("%Y-%m-%d %X"),
                # "nick_name": msg["User"]["NickName"],
                "province": msg["User"]["Province"]
            }
            # 把收到的消息交发给图灵机器人
            content = self.tuling_register(msg["Text"])
            # content就图灵机器人回复的消息回复给发送消息的人
            return content

        # 开启自动回复会阻塞
        itchat.run()

    def send(self):
        # 发送消息
        name = input("请输入发送给谁:")
        # 获取对方的信息
        users = itchat.search_friends(name=name)
        if not users:
            print("没有找到此人")
            return
        # 获取`UserName`,用于发送消息
        userName = users[0]['UserName']
        content = input("请输入发送的内容或者文件的路径:")
        if content.endswith(".txt"):
            itchat.send_file(u'%s' % content, userName)
        elif content.endswith(".png") or content.endswith(".jpg"):
            itchat.send_image(u'%s' % content, userName)
        elif content.endswith(".mp4"):
            itchat.send_video(u'%s' % content, userName)
        else:
            itchat.send(u'%s' % content, userName)

    def timing_send(self):
        """定时发送"""
        for user in self.friends:
            if user["RemarkName"] == "":
                print(user["NickName"])
            else:
                print(user["RemarkName"])
        while True:
            name = input("请输入接收人:")
            users = itchat.search_friends(name=name)
            if users:
                break
            else:
                print("没找到此人请从新输入")
        timing = input("请输入发送的时间格式为(2018-05-15 10:20):")
        connut = input("请输入发送的内容:")
        userName = users[0]['UserName']
        ti_send = threading.Thread(target=self.timing_msg, args=(userName,timing,connut))
        ti_send.setDaemon(True)
        ti_send.start()

    def timing_msg(self, userName, timing, connut):
        while True:
            time.sleep(0.5)
            now_time = time.strftime("%Y-%m-%d %H:%M")
            if timing == now_time:
                itchat.send(connut, userName)
                break

                
    def gender_ratio(self):
        """获取男女比例"""
        # 初始化计数器，有男有女，当然，有些人是不填的
        male = 0
        female = 0
        other = 0
        # 遍历这个列表，列表里第一位是自己，所以从"自己"之后开始计算
        # 1表示男性，2女性
        for i in self.friends[1:]:
            sex = i["Sex"]
            if sex == 1:
                male += 1
            elif sex == 2:
                female += 1
            else:
                other += 1
        # 总好友数
        total = len(self.friends[1:])
        print("男性好友：%.2f%%" % (float(male) / total * 100))
        print("女性好友：%.2f%%" % (float(female) / total * 100))
        print("其他：%.2f%%" % (float(other) / total * 100))


def main():
    db = Db()
    weixin_msg = WeiXinMsg(db)
    # 接收消息
    t = threading.Thread(target=weixin_msg.recv)
    t.setDaemon(True)  # 跟随父线程一起结束
    t.start()

    while True:
        print("-" * 18 + "请选择对应操作" + "-" * 18)
        print("1、发送消息")
        print("2、查看自己好友的男女比例")
        print("3、定时发送")
        print("0、退出")
        print("-" * 50)
        index = input("请输入对应的操作:")
        if index == "1":
            weixin_msg.send()
        elif index == "2":
            weixin_msg.gender_ratio()
        elif index == "3":
            weixin_msg.timing_send()   
        elif index == "0":
            break
        else:
            print("请重新输入")


if __name__ == '__main__':
    main()
