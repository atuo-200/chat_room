import asynchat
import asyncore
import time

# 定义端口
PORT = 6666

# 定义结束异常类
class EndSession(Exception):
    pass


class ChatServer(asyncore.dispatcher):
    """
    创建一个支持多用户连接的聊天服务器
    """
    #重写构造方法
    def __init__(self, port):
	#显式调用父类构造方法
        asyncore.dispatcher.__init__(self)
        # 创建socket
        self.create_socket()
        # 设置 socket 为可重用
        self.set_reuse_addr()
        # 监听端口
        self.bind(('', port))
	#设置最大连接数为5,超出排队
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
	#阻塞式监听，等待客户端的连接，生成连接对象(SSL通道，客户端地址)
        conn, addr = self.accept()
	#建立会话
        ChatSession(self, conn)

class ChatSession(asynchat.async_chat):
    """
    负责和客户端通信的会话类
    """

    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
	#设置数据终止符
        self.set_terminator(b'\n')
	#设置数据列表
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        # 从当前房间移除自身，然后添加到指定房间
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)
    #重写处理客户端发来数据的方法
    def collect_incoming_data(self, data):
        # 接收客户端的数据并解码
        self.data.append(data.decode("utf-8"))
    #重写发现数据中终止符号时的处理方法
    def found_terminator(self):
        #将数据列表中的内容整合为一行
        line = ''.join(self.data)
	#清理数据列表
        self.data = []
        try:
            self.room.handle(self, line.encode("utf-8"))
        # 退出聊天室的处理
        except EndSession:
            self.handle_close()

    def handle_close(self):
        # 当 session 关闭时，将进入 LogoutRoom
        asynchat.async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))

class CommandHandler:
    """
    命令处理类
    """
    #定义未知命令的处理方法
    def unknown(self, session, cmd):
        # 通过 aynchat.async_chat.push 方法发送消息，向客户端发送错误提示
        session.push(('不知名命令 {} \n'.format(cmd)).encode("utf-8"))

    def handle(self, session, line):
	#解码
        line = line.decode("utf-8")
        print(line)
        #判断去掉空格后是否还有数据
        if not line.strip():
            return
	#把数据以空格分隔符分割生成列表，最大分割数为1
        parts = line.split(' ', 1)
	#分割的第一部分为命令
        cmd = parts[0]
	#将分割后的第二部分去除空格保存到变量
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        #获取指定名称的方法对象
        method = getattr(self, 'do_' + cmd, None)
	#调用获取到的方法对象
        try:
            method(session, line)
        except TypeError:
            self.unknown(session, cmd)
class Room(CommandHandler):
    """
    包含多个用户的环境，负责基本的命令处理和广播
    """

    def __init__(self, server):
        self.server = server
	#会话列表
        self.sessions = []

    def add(self, session):
        # 一个用户进入房间
        self.sessions.append(session)

    def remove(self, session):
        # 一个用户离开房间
        self.sessions.remove(session)
    #定义广播信息的处理方法
    def broadcast(self, line):
        #遍历所有用户会话，再使用 asynchat.asyn_chat.push 方法发送数据
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        # 退出房间
        raise EndSession


class LoginRoom(Room):
    """
    处理登录用户
    """

    def add(self, session):
        # 用户连接成功的回应
        Room.add(self, session)
        # 使用 asynchat.asyn_chat.push 方法发送数据到客户端
        session.push('连接成功'.encode('utf-8'))

    def do_login(self, session, line):
        # 用户登录逻辑
        name = line.strip()
        # 获取用户名称
        if not name:
            session.push('用户名为空'.encode('utf-8'))
        # 检查是否有同名用户
        elif name in self.server.users:
            session.push('用户名已存在'.encode('utf-8'))
        # 用户名检查成功后，进入主聊天室
        else:
            session.name = name
            session.enter(self.server.main_room)


class LogoutRoom(Room):
    """
    处理退出用户
    """

    def add(self, session):
        # 从服务器中用户字典中移除相关记录
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatRoom(Room):
    """
    聊天用的房间
    """

    def add(self, session):
        # 广播新用户进入
        session.push('登录成功'.encode('utf-8'))
        #self.broadcast((session.name + ' 进入房间\n').encode("utf-8"))
	#向服务器的用户字典添加与会话的用户名相对应的会话
        self.server.users[session.name] = session
        Room.add(self, session)
        #----------------------添加-------------------
        users = ";".join(self.ls_users())
        self.broadcast((users+" 用户列表\n").encode("utf-8"))

    def remove(self, session):
        # 广播用户离开
        Room.remove(self, session)
        users = ";".join(self.ls_users())
        self.broadcast((users+" 用户列表\n").encode("utf-8"))
        #self.broadcast((session.name + ' 离开房间\n').encode("utf-8"))

    def do_say(self, session, line):
        # 客户端发送消息
        print(line)
        self.broadcast(('time:'+time.strftime('%H:%M:%S',time.localtime(time.time()))+ '\n'+session.name + ': ' + line + '\n').encode("utf-8"))

    def ls_users(self):
        # 查看在线用户
        # session.push('在线用户:\n'.encode('utf-8'))
        # for other in self.sessions:
        #     session.push((other.name + '\n').encode("utf-8"))
        #-------------------修改------------------
        users = []
        for other in self.sessions:
            users.append(other.name)
        return users       

if __name__ == '__main__':

    s = ChatServer(PORT)
    try:
        print("chat serve run at '47.100.186.96:{0}'".format(PORT))
	#开启循环监听网络事件
        asyncore.loop()
    except KeyboardInterrupt:
        print("chat server exit")
