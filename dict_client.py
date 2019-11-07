"""
电子辞典 v1.0 客户端
env:python 3.6
"""

from socket import *
import sys

ADDR = ("127.0.0.1",1605)
s = socket(AF_INET, SOCK_DGRAM)

def register(s):
    while True:
        user_name = input("新用户请创建用户名,老用户若忘记密码请输入原用户名,不允许中间有空格\n>>")
        if " " in user_name:
            print("用户名格式不正确,请重新输入")
            continue
        break
    msg = "R " + user_name
    s.sendto(msg.encode(),ADDR)
    data, addr = s.recvfrom(128)
    if data.decode() == "ROK":
        print("账户已创建,默认密码0000,现在请修改密码,用户不要强行退出该软件")
        while True:
            password = input("请创建密码,不允许中间有空格\n>>")
            password2 = input("请确认密码\n>>")
            if password != password2 or (" " in password):
                print("密码错误,请重新输入")
                continue
            else:
                msg = "V " + user_name + " " + password
                s.sendto(msg.encode(), ADDR)
                data, addr = s.recvfrom(128)
                if data.decode() == "VOK":
                    print("创建用户成功,即将进入初始登录界面")
                    page_1()
                    break
                else:
                    print("请使用默认密码,即将进入初始登录界面")
                    page_1()
                    break
    else:
        print("修改密码中")
        while True:
            password = input("请输入新密码,不允许中间有空格\n>>")
            password2 = input("请确认新密码\n>>")
            if password != password2 or (" " in password):
                print("密码错误,请重新输入")
                continue
            else:
                msg = "V " + user_name + " " + password
                s.sendto(msg.encode(), ADDR)
                data, addr = s.recvfrom(128)
                if data.decode() == "VOK":
                    print("修改密码成功,即将进入初始登录界面")
                    page_1()
                    break
                else:
                    print("修改密码失败,请使用原先密码或者稍后再次尝试,即将进入初始登录界面")
                    page_1()
                    break

def login(s):
    user_name = input("请输入用户名\n>>")
    while True:
        password = input("请输入密码\n>>")
        msg = "L " + user_name + " " + password
        s.sendto(msg.encode(), ADDR)
        data, addr = s.recvfrom(128)
        if data.decode() == "LOK":
            print("登陆成功,进入系统")
            page_2(user_name)
            break
        elif data.decode() == "LNO":
            print("密码输入错误,请重新输入")
            continue
        else:
            print("该用户不存在,即将回到初始登录界面")
            page_1()
            break

def quit(s):
    msg = "Q "
    s.sendto(msg.encode(), ADDR)
    data, addr = s.recvfrom(128)
    if data.decode() == "EXIT":
        sys.exit("已登出,感谢您的使用")


def search(s,user_name):
    word = input("请输入要查询的单词,摁*回到上一界面\n>>")
    if word == "*":
        page_2(user_name)
    msg = "S " + user_name + " " + word
    s.sendto(msg.encode(), ADDR)
    data, addr = s.recvfrom(128)
    if data.decode() == "NULL":
        print("没有查询到该单词,请重新输入")
    else:
        print(word)
        print(data.decode())

def history(s,user_name):
    msg = "H " + user_name
    s.sendto(msg.encode(), ADDR)
    data, addr = s.recvfrom(128)
    print(data.decode())

def logout(s,user_name):
    msg = "O " + user_name
    s.sendto(msg.encode(), ADDR)
    data, addr = s.recvfrom(128)
    if data.decode() == "OUT":
        print("%s已注销,返回至初始界面" % user_name)
        page_1()



def page_1():
    while True:
        number = input("\n"
                        "---------------------------------------\n"
                           "用户注册与修改密码请摁1,用户登录请摁2,登出请摁3\n."
                           "--------------------------------------\n>>")
        if number == "1":
            register(s)
        elif number == "2":
            login(s)
        elif number == "3":
            quit(s)
        else:
            print("键入错误,请重新输入")
            continue

def page_2(user_name):
    print(" ")
    print("%s连接成功,欢迎您使用电子辞典" % user_name)
    while True:
        number = input("\n"
                        "-----------------------------------\n"
                           "查单词请摁1,查询历史记录请摁2,注销请摁3\n."
                           "----------------------------------\n>>")
        if number == "1":
            search(s,user_name)
        elif number == "2":
            history(s,user_name)
        elif number == "3":
            logout(s,user_name)
        else:
            print("键入错误,请重新输入")
            continue



if __name__ == '__main__':
    page_1()

