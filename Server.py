from socket import *
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包

serverIP = ''
serverPort = 12000
messages = queue.Queue()
users = []  # 0:userName 1:connectionSocket
lock = threading.Lock()  # 线程锁
usernames = []  # 在线用户列表


def extract_ip():
    """获取当前服务器的ip地址。"""
    global serverIP
    st = socket(AF_INET, SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        serverIP = st.getsockname()[0]
    except Exception:
        serverIP = '127.0.0.1'
    finally:
        st.close()


def Load(data, addr):
    """将地址与数据存入messages队列。

    :param data: 要发送给客户端的数据
    :param addr: 用户地址（IP+端口）
    """
    lock.acquire()
    try:
        messages.put((addr, data))
    finally:
        lock.release()


def receive(connectionSocket, addr):
    """接收线程：接收用户名，或客户端消息。

    :param connectionSocket: 连接套接字（由某特定用户专用）
    :param addr: 用户地址（IP+端口）
    """
    user = connectionSocket.recv(1024).decode()  # 用户名称
    users.append((user, connectionSocket))
    usernames.append(user)
    Load(usernames, addr)

    # 获取用户名后，不断地接受用户端发送的消息，结束后关闭连接。
    try:
        while True:
            message = connectionSocket.recv(1024).decode()  # 发送消息
            message = user + '：' + message
            Load(message, addr)
        connectionSocket.close()
    # 用户断开连接，将该用户从用户列表中删除，并更新用户列表。
    except:
        j = 0
        for man in users:
            if man[0] == user:
                users.pop(j)
                usernames.pop(j)
                break
            j = j + 1
        Load(usernames, addr)
        connectionSocket.close()


def send():
    """发送线程：将接收并进行处理后的数据发送给客户端。
    对于聊天内容，直接发送；对于用户名列表，由json.dumps处理后发送。"""
    while True:
        if not messages.empty():
            message = messages.get()
            # 聊天消息
            if isinstance(message[1], str):
                for i in range(len(users)):
                    data = message[1]
                    users[i][1].send(data.encode())
                    print(data + '\n')
            # 用户名列表
            if isinstance(message[1], list):
                data = json.dumps(message[1])
                for i in range(len(users)):
                    users[i][1].send(data.encode())


class ChatServer(threading.Thread):
    """聊天室服务器。"""

    def __init__(self):
        """构造函数。"""
        threading.Thread.__init__(self)
        extract_ip()
        self.s = socket(AF_INET, SOCK_STREAM)  # 欢迎套接字，IPv4，TCP
        self.s.bind(('', serverPort))
        self.s.listen(5)

    def run(self):
        """重写run函数，实现多线程。"""
        q = threading.Thread(target=send)
        q.start()
        while True:
            conn, addr = self.s.accept()  # 连接套接字
            t = threading.Thread(target=receive, args=(conn, addr))
            t.start()
        self.socket.close()


if __name__ == '__main__':
    cServer = ChatServer()
    cServer.start()
