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

    @staticmethod
    def tuling_register(msg):
        apiUrl = 'http://www.tuling123.com/openapi/api'
        data = {
            'key': 'bffee870aee3429c996e320e4b0d4187',  # 到图灵官网可以注册一个
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

    def send(self, name, connut):
        # 发送消息
        # 获取对方的信息
        users = itchat.search_friends(name=name)
        if not users:
            print("没有找到此人")
            return
        # 获取`UserName`,用于发送消息
        userName = users[0]['UserName']
        if connut.endswith(".txt"):
            itchat.send_file(u'%s' % connut, userName)
        elif connut.endswith(".png") or connut.endswith(".jpg"):
            itchat.send_image(u'%s' % connut, userName)
        elif connut.endswith(".mp4"):
            itchat.send_video(u'%s' % connut, userName)
        else:
            itchat.send(u'%s' % connut, userName)

    def timing_send(self, flock=False):
        """定时发送"""
        name = ""
        if not flock:
            name = input("发给谁:")
        connut = input("请输入发送的内容:")
        timing = input("请输入发送的时间格式为(2018-05-15 10:20):")
        ti_send = threading.Thread(target=self.timing_msg, args=(timing, name, connut, flock))
        ti_send.setDaemon(True)
        ti_send.start()

    def timing_msg(self, timing, name, connut, flock):
        while True:
            time.sleep(0.5)
            now_time = time.strftime("%Y-%m-%d %H:%M")
            print(timing+"----------------"+now_time)
            if timing == now_time:
                print("到时间了")
                if flock:
                    print("群发")
                    self.flock_send(connut)
                    break
                else:
                    print("单发")
                    self.send(name, connut)
                    break

    def flock_send(self, connut):
        """群发"""
        # 好友列表
        friends = itchat.get_friends(update=True)[0:]
        for user in friends:
            users = itchat.search_friends(name=user["NickName"])
            userName = users[0]['UserName']
            itchat.send(connut, userName)


def main():
    weixin_msg = WeiXinMsg()
    # 接收消息
    t = threading.Thread(target=weixin_msg.recv)
    t.setDaemon(True)  # 跟随父线程一起结束
    t.start()

    while True:
        print("-" * 18 + "请选择对应操作" + "-" * 18)
        print("1、发送消息")
        print("2、定时发送")
        print("3、群发消息")
        print("4、定时群发")
        print("-" * 50)
        index = input("请输入对应的操作:")
        if index == "1":
            name = input("请输入发送给谁:")
            connut = input("请输入发送的内容:")
            weixin_msg.send(name, connut)
        elif index == "2":
            weixin_msg.timing_send()
        elif index == "3":
            connut = input("请输入发送的内容:")
            weixin_msg.flock_send(connut)
        elif index == "4":
            weixin_msg.timing_send(flock=True)
        elif index == "0":
            break
        else:
            print("请重新输入")


if __name__ == '__main__':
    main()
