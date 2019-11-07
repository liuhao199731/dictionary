"""
电子辞典 v1.0 服务端
env:python 3.6
"""

import pymysql
from socket import *
import os,sys
import signal
import time
signal.signal(signal.SIGCHLD,signal.SIG_IGN)    # 处理僵尸进程

HOST = "127.0.0.1"
PORT = 1605
ADDR = (HOST,PORT)


db = pymysql.connect(user = "root",passwd = "123456",database = "dict",charset = "utf8")
cur = db.cursor()

def do_register(s,user_name,addr):
    print("创建用户中...")
    try:
        sql = "insert into users (user_name,password) values (%s,0000);"
        cur.execute(sql, [user_name])
        db.commit()
        s.sendto(b"ROK", addr)
        print("用户%s已注册成功,进入修改密码阶段" % user_name)
        return
    except Exception:
        db.rollback()
        s.sendto("\n用户名已存在,进入修改密码界面".encode(), addr)
        print("用户%s进入修改密码阶段" % user_name)
        return

def do_verify(s,user_name,password,addr):
    print("修改密码中...")
    try:
        sql = "update users set password = %s where user_name = %s;"
        cur.execute(sql,[password,user_name])
        db.commit()
        s.sendto(b"VOK", addr)
        print("用户%s修改密码成功" % user_name)
        return
    except Exception:
        db.rollback()
        s.sendto("\n修改密码失败".encode(), addr)
        print("用户%s修改密码失败" % user_name)
        return

def do_login(s,user_name,password,addr):
    print("处理用户%s登入中..." % user_name)
    sql = "select password from users where user_name = %s;"
    cur.execute(sql, [user_name])
    try:
        one_row = cur.fetchone()
        if password == one_row[0]:
            s.sendto(b"LOK", addr)
            print("用户%s进入系统" % user_name)
            return
        else:
            s.sendto(b"LNO", addr)
            print("用户%s登录失败" % user_name)
            return
    except Exception:
        s.sendto("该用户不存在".encode(), addr)
        print("用户%s不存在" % user_name)
        return

def do_quit(s,addr):
    s.sendto(b"EXIT",addr)
    print("用户已退出...")
    return


def do_search(s,user_name,word,addr):
    print("%s用户正在查询%s单词..." % (user_name,word))
    sql = "select mean from words where word = %s;"
    cur.execute(sql, [word])
    db.commit()
    try:
        one_row = cur.fetchone()
        answer = one_row[0]
        s.sendto(answer.encode(),addr)
    except Exception:
        s.sendto(b"NULL", addr)
        return
    try:
        sql = "select search_log from users where user_name = %s;"
        cur.execute(sql, [user_name])
        db.commit()
        one_row = cur.fetchone()
        search_log = one_row[0]
        if search_log == None:
            new_search_log = "%s  %s" % (word,time.ctime())
        else:
            new_search_log = "%s  %s \n%s" % (word,time.ctime(),search_log)
        sql = "update users set search_log = %s where user_name = %s;"
        cur.execute(sql, [new_search_log,user_name])
        db.commit()
        print("记录%s的历史数据完成" % user_name)
    except Exception as e:
        print(e)
        db.rollback()

def do_history(s,user_name,addr):
    print("%s用户正在查询历史记录..." % user_name)
    sql = "select search_log from users where user_name = %s;"
    cur.execute(sql, [user_name])
    db.commit()
    try:
        one_row = cur.fetchone()
        answer = one_row[0]
        s.sendto(answer.encode(), addr)
        print("已将历史数据发送至%s" % user_name)
    except Exception:
        s.sendto("历史数据为空".encode(), addr)
        db.rollback()

def do_logout(s,user_name,addr):
    print("%s用户正在注销..." % user_name)
    sql= "update users set search_log = NULL where user_name = %s;"
    cur.execute(sql, [user_name])
    db.commit()
    s.sendto(b"OUT", addr)
    print("%s用户注销成功..." % user_name)
    return



def do_request(s):
    while True:
        data,addr = s.recvfrom(1024)
        # 只切前两项,防止用户输入的消息中有空格也被切掉
        tmp = data.decode().split(" ",3)
        # 根据不同的请求类型,执行不同的事件
        if tmp[0] == "R":
            do_register(s,tmp[1],addr)
        elif tmp[0] == "V":
            do_verify(s,tmp[1],tmp[2],addr)
        elif tmp[0] == "L":
            do_login(s,tmp[1],tmp[2],addr)
        elif tmp[0] == "Q":
            do_quit(s,addr)
        elif tmp[0] == "S":
            do_search(s,tmp[1],tmp[2],addr)
        elif tmp[0] == "H":
            do_history(s,tmp[1],addr)
        elif tmp[0] == "O":
            do_logout(s,tmp[1],addr)



def main():
    s = socket(AF_INET,SOCK_DGRAM)
    s.bind(ADDR)
    pid = os.fork()
    if pid < 0:
        sys.exit("进程错误!")
    elif pid == 0:
        pass
    else:
        do_request(s) # 接受客户端请求

if __name__ == '__main__':
    main()