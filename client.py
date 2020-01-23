import wx
import telnetlib
from time import sleep
import _thread as thread

class LoginFrame(wx.Frame):
    """
    登录窗口类，继承wx.Frame类
    """
    #初始化，添加控件
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
	#设置窗体大小        
        self.SetSize(size)
	#放置正中央
        self.Center()
	#服务器地址框标签
        self.serverAddressLabel = wx.StaticText(self, label="服务器地址", pos=(10, 50), size=(120, 25))
	#用户名框标签        	
        self.userNameLabel = wx.StaticText(self, label="用户名", pos=(40, 100), size=(120, 25))
	#服务器地址框        
        self.serverAddress = wx.TextCtrl(self, pos=(120, 47), size=(150, 25))
	#用户名框        
        self.userName = wx.TextCtrl(self, pos=(120, 97), size=(150, 25))
	#登录按钮        
        self.loginButton = wx.Button(self, label='登录', pos=(80, 145), size=(130, 30))
        #登录按钮上绑定登录方法
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
	#显示组件        
        self.Show()

    def login(self, event):
        # 登录处理
        try:
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            con.open(serverAddress[0], port=int(serverAddress[1]), timeout=10)
            response = con.read_some()
            if response != '连接成功'.encode('utf-8'):
                self.showDialog('Error', '连接失败!', (200, 100))
                return
            con.write(('login ' + str(self.userName.GetLineText(0)) + '\n').encode("utf-8"))
            response = con.read_some()
            if response == '用户名为空'.encode('utf-8'):
                self.showDialog('Error', '用户名为空!', (200, 100))
            elif response == '用户名已存在':
                self.showDialog('Error', '用户名已存在!', (200, 100))
            else:
                self.Close()
                ChatFrame(None, 2, title='阿坨聊天室', size=(500, 400))
        except Exception:
            self.showDialog('Error', '连接失败!', (195, 120))

    def showDialog(self, title, content, size):
        # 显示错误信息对话框
        dialog = wx.Dialog(self, title=title, size=size)
        dialog.Center()
        wx.StaticText(dialog, label=content)
	#显示对话窗口
        dialog.ShowModal()
class ChatFrame(wx.Frame):
    """
    聊天窗口类，继承wx.Frame类
    """

    def __init__(self, parent, id, title, size):
        # 初始化，添加控件
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
	#显示对话文本框，style设置其文本高亮显示和只读
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(300, 25))
        self.sendButton = wx.Button(self, label="Send", pos=(310, 320), size=(58, 25))
        self.usersButton = wx.Button(self, label="Users", pos=(373, 320), size=(58, 25))
        self.closeButton = wx.Button(self, label="Close", pos=(436, 320), size=(58, 25))
        # 发送按钮绑定发送消息方法
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        # Users按钮绑定获取在线用户数量方法
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        # 关闭按钮绑定关闭方法
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
	#调用thread模块中的start_new_thread()来产生新线程负责接收服务器信息
	#第一个参数为线程要执行函数的函数名，第二个参数为需要传递给函数的实参，为tuple，若该函数不需要参数也要传入空tuple       
        thread.start_new_thread(self.receive, ())
        self.Show()

    def send(self, event):
        # 发送消息
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
	    #这里的'say '不可随意变动，为呼应server.py中命令处理类定义的handle(),实现文字聊天协议而存在
            con.write(('say ' + message + '\n').encode("utf-8"))
            self.message.Clear()

    def lookUsers(self, event):
        #查看当前在线用户
        con.write(b'look\n')

    def close(self, event):
        # 关闭窗口
        con.write(b'logout\n')
        con.close()
        self.Close()

    def receive(self):
        # 接受服务器的消息
        while True:
            sleep(0.6)
	    #在I/O中读取数据，存在result变量中
            result = con.read_very_eager()
            if result != '':
                self.chatFrame.AppendText(result)

if __name__ == '__main__':
    #应用程序对象
    app = wx.App()
    #客户端使用telnetlib连接目标主机
    con = telnetlib.Telnet()
    #顶级窗口对象
    LoginFrame(None, -1, title="Login", size=(320, 250))
    #进入应用程序的主事件循环
    app.MainLoop()

