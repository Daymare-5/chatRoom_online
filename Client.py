from socket import *
import threading
import json
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
import Server

IP = ''
serverIP = ''
serverPort = 12000
user = ''  # 当前用户名
users = []  # 在线用户列表


def extract_ip():
    """获取当前主机的ip地址。"""
    global IP
    st = socket(AF_INET, SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()


extract_ip()
"""--------------------登陆窗口--------------------"""
window0 = tkinter.Tk()
# 窗口属性
width = 300
height = 210
window0.geometry(f'{width}x{height}')
screen_width = window0.winfo_screenwidth() / 2 - width / 2
screen_height = window0.winfo_screenheight() / 2 - height / 2
window0.geometry(f"+{int(screen_width)}+{int(screen_height)}")
window0.title('在线聊天室')
window0.resizable(False, False)
# 窗口内容
labelIP = tkinter.Label(window0, text='当前IP地址')
labelIP.place(x=20, y=20, width=100, height=40)
contentIP = tkinter.Label(window0, width=60, text=IP)
contentIP.place(x=120, y=25, width=100, height=30)

server = tkinter.StringVar()
server.set('')
labelServer = tkinter.Label(window0, text='聊天室IP地址')
labelServer.place(x=20, y=65, width=100, height=40)
entryServer = tkinter.Entry(window0, width=60, textvariable=server)
entryServer.place(x=120, y=70, width=100, height=30)

USER = tkinter.StringVar()
USER.set('')
labelUSER = tkinter.Label(window0, text='用户名')
labelUSER.place(x=20, y=115, width=100, height=40)
entryUSER = tkinter.Entry(window0, width=60, textvariable=USER)
entryUSER.place(x=120, y=120, width=100, height=30)


def enter(*args):
    global user, serverIP
    user = entryUSER.get()
    serverIP = entryServer.get()
    if not user:
        tkinter.messagebox.showwarning('警告', message='用户名为空，\n将使用默认用户名（IP）')
    user = user + '(' + IP + ')'
    if not serverIP:
        tkinter.messagebox.showwarning('错误', message='聊天室IP地址为必填！')
    else:
        window0.destroy()


def create(*args):
    try:
        cServer = Server.ChatServer()
        cServer.start()
        tkinter.messagebox.showwarning('结果', message='聊天室创建成功！\n输入你的地址，进入聊天室吧！')
        server.set(IP)
    except:
        tkinter.messagebox.showwarning('错误', message='聊天室已存在！！')


loginButton = tkinter.Button(window0, text="创建", command=create, bg="White")
loginButton.place(x=80, y=165, width=40, height=25)
loginButton = tkinter.Button(window0, text="进入", command=enter, bg="White")
loginButton.place(x=180, y=165, width=40, height=25)
window0.bind('<Return>', enter)
window0.mainloop()

"""--------------------建立连接--------------------"""
try:
    socket = socket(AF_INET, SOCK_STREAM)
    socket.connect((serverIP, serverPort))
    socket.send(user.encode())
except:
    tkinter.messagebox.showwarning('错误', message='聊天室不存在！')
    exit(0)


"""--------------------聊天窗口--------------------"""
window1 = tkinter.Tk()
# 窗口属性
width = 640
height = 480
window1.geometry(f'{width}x{height}')
screen_width = window1.winfo_screenwidth() / 2 - width / 2
screen_height = window1.winfo_screenheight() / 2 - height / 2
window1.geometry(f"+{int(screen_width)}+{int(screen_height)}")
window1.title('在线聊天室')
window1.resizable(False, False)
# 消息显示框
messageBox = ScrolledText(window1)
messageBox.place(x=5, y=0, width=510, height=360)
messageBox.tag_config('tag1', foreground='red', background="yellow")
messageBox.insert(tkinter.END, '欢迎进入在线聊天室!\n', "tag1")
# 消息输入框
INPUT = tkinter.StringVar()
INPUT.set('')
entryInput = tkinter.Entry(window1, textvariable=INPUT)
entryInput.place(x=5, y=360, width=580, height=115)
# 在线用户列表
userListbox = tkinter.Listbox(window1)
userListbox.place(x=510, y=0, width=130, height=360)


def send(*args):
    message = entryInput.get()  # 若私聊，msg+ ：xxx
    socket.send(message.encode())
    INPUT.set('')


sendButton = tkinter.Button(window1, text="\n发\n\n送", anchor='n', command=send, font=('Helvetica', 15), bg='white')
sendButton.place(x=585, y=360, width=55, height=120)
window1.bind('<Return>', send)


def receive():
    """接收线程：接收来自服务器的消息，并更新客户端显示。"""
    global users
    while True:
        data = socket.recv(1024).decode()
        try:  # 在线用户更新
            users = json.loads(data)
            userListbox.delete(0, tkinter.END)
            userListbox.insert(tkinter.END, "当前在线用户")
            for x in range(len(users)):
                userListbox.insert(tkinter.END, users[x])
        except:  # 聊天消息更新
            data = data.split('：', 1)
            userName = data[0]
            content = data[1]
            chatwith = ''
            # 判断是否为私聊
            if content.rfind(" ：") != -1:
                content = content.split(" ：")
                message = content[0]
                chatwith = content[1]
            else:
                message = content
            if chatwith != '':
                if userName == user:
                    messageBox.tag_config('tag2', foreground='blue')
                    messageBox.insert(tkinter.END, '\n' + userName + '->' + chatwith + '：' + message, 'tag2')
                elif chatwith == user:
                    messageBox.tag_config('tag3', foreground='red')
                    messageBox.insert(tkinter.END, '\n' + userName + '->' + chatwith + '：' + message, 'tag3')
            else:
                if userName == user:
                    messageBox.tag_config('tag2', foreground='blue')
                    messageBox.insert(tkinter.END, '\n' + userName + '：' + message, 'tag2')
                else:
                    messageBox.insert(tkinter.END, '\n' + userName + '：' + message)
            messageBox.see(tkinter.END)


# 启动接收线程
r = threading.Thread(target=receive)
r.start()

window1.mainloop()
socket.close()



