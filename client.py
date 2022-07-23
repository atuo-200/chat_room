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
            elif response == '用户名已存在'.encode('utf-8'):
                self.showDialog('Error', '用户名已存在!', (200, 100))
            elif response == "登录成功".encode('utf-8'):
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
    def __init__(self, parent, id, title, size):
        # 初始化，添加控件并绑定事件
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)#设置对话框的大小
        self.Center()#设置弹窗在屏幕中间               
        
        #使用尺寸器改写,改写后拉大或者缩小窗口，中间的控件会随着窗口的大小已固定的尺寸而改变
        panel=wx.Panel(self,-1,pos=(0,0),size=(750,350))

        self.emoji_list = ['🗿', '🙃', '😊',
              '🥰', '🤬', '🥶', '🥵', '😳',
              '🤮', '🤩', '🤓', '😝', '🌚',
              '🙈', '🤪', '🏩', '🚸','🤺',
              '🚾', '🉑', '㊙', '🈶','🈚', 
              '🆘', '🆗', '🤟','👊','😭', 
              '🙏', '🙌', '🦓','🦜','🦄',
              '🎃', '✔', '™']

        self.emoil_grid= wx.GridSizer(cols=15, rows=3, vgap=4, hgap=4)
        self.emoil_grid.AddMany(self.show_emoji_list(panel))
        self.chatFrame = wx.TextCtrl(panel,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_LEFT)
        self.noticeFrame = wx.TextCtrl(panel,style=wx.TE_MULTILINE | wx.TE_READONLY )
        self.message = wx.TextCtrl(panel)#设置发送消息的文本输入框的位置和尺寸
        self.sendButton = wx.Button(panel, label="Send")
        self.closeButton = wx.Button(panel, label="Close")
        
        self.box1=wx.BoxSizer()#定义横向的box2
        self.box1.Add(self.chatFrame, proportion=7,flag=wx.EXPAND | wx.ALL,border=5)
        self.box1.Add(self.noticeFrame, proportion=3,flag=wx.EXPAND | wx.ALL,border=5)
        
        self.box2=wx.BoxSizer()
        self.box2.Add(self.emoil_grid)

        self.box3=wx.BoxSizer()#定义横向的box3
        self.box3.Add(self.message, proportion=4, flag=wx.EXPAND | wx.ALL,border=5)
        self.box3.Add(self.sendButton, proportion=1,flag=wx.EXPAND | wx.ALL,border=5)
        self.box3.Add(self.closeButton, proportion=1,flag=wx.EXPAND | wx.ALL,border=5)
        
        self.v_box=wx.BoxSizer(wx.VERTICAL)#定义一个纵向的v_box
        self.v_box.Add(self.box1, proportion=6,flag=wx.EXPAND | wx.ALL,border=5)#添加box2，比例为7
        self.v_box.Add(self.box2, proportion=2,flag=wx.EXPAND | wx.ALL,border=5)#添加box3，比例为1
        self.v_box.Add(self.box3, proportion=2,flag=wx.EXPAND | wx.ALL,border=5)#添加box4，比例为1
        
        panel.SetSizer(self.v_box)
                # 发送按钮绑定发送消息方法
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        # Users按钮绑定获取在线用户数量方法
        #self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        # 关闭按钮绑定关闭方法
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
	#调用thread模块中的start_new_thread()来产生新线程负责接收服务器信息
	#第一个参数为线程要执行函数的函数名，第二个参数为需要传递给函数的实参，为tuple，若该函数不需要参数也要传入空tuple       
        thread.start_new_thread(self.receive, ())
        self.Show()

    def show_emoji_list(self,panel):
        row = 1
        col = 1
        btns = [] 
        for e in self.emoji_list:
            btn = wx.Button(panel,label=e,size=(30,30))
            btn.Bind(wx.EVT_BUTTON, self.add_emoil)
            #btn.grid(row=row, column=col, sticky='nsew')
            btns.append(btn)
            col += 1
            if col == 6:
                row += 1
                col = 1  
        return btns

    def add_emoil(self,event):
        emoil_cid = event.GetId()
        emoil_c=self.sendButton.FindWindowById(emoil_cid)

        emoil_s=emoil_c.GetLabel().encode()
        self.message.WriteText(emoil_s)

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
            result = con.read_very_eager().decode("utf-8")
            if result != "":
                print(result)
                if "用户列表" in result:
                    self.noticeFrame.SetValue("")
                    self.noticeFrame.AppendText("在线用户：\n")
                    users = result.split(" ")[0].split(";")
                    for user in users:
                        self.noticeFrame.AppendText(user+'\n')
                else:
                    self.chatFrame.AppendText(result)


if __name__ == '__main__':
    app = wx.App()
    #客户端使用telnetlib连接目标主机
    con = telnetlib.Telnet()
    #顶级窗口对象
    LoginFrame(None, -1, title="Login", size=(320, 250))
    #进入应用程序的主事件循环
    app.MainLoop()