import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox,QLabel
from PyQt5.QtWidgets import QListWidget,QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem



import time
import socket
import threading
from threading import Thread

lock=threading.Lock()

form_class=uic.loadUiType("CS.ui")[0]

class ClientInterface(QMainWindow, form_class):
    def __init__(self):
        
        super().__init__()
        
        self.HOST='127.0.0.1'
        self.PORT=9009
        self.title='Title'
        self.left=100
        self.top = 100
        self.width = 1280
        self.height = 800
        
        self.MsgReceive=[]
        self.MsgSend=[]


        self.initUI()


    def rcvMsg(self,sock):
        
        while True:
            print(1)
            try:
                data=sock.recv(1024)
                if not data:
                    break
                print('r: ',data.decode())

            except:
                pass

    def rcvMsgReturn(self,sock):
        while True:
            data=sock.recv(1024).decode()
            if not data:
                break
            lock.acquire()
            self.MsgReceive.append(data)
            lock.release()
            
            print(self.MsgReceive)

    def initUI(self):

        x=60
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, \
        self.width, self.height)

        self.IDbox=QLineEdit(self)
        self.IDbox.move(x,20)
        self.IDbox.resize(280,40)
        
        self.PWbox=QLineEdit(self)
        self.PWbox.move(x,20+40+10)
        self.PWbox.resize(280,40)
        self.PWbox.setEchoMode(QLineEdit.Password)

        self.button_LogIn=QPushButton("Log In",self)
        self.button_LogIn.move(x,70+60)
        self.button_LogIn.clicked.connect(self.on_click_LogIn)

        self.button_SignIn=QPushButton('Sign In',self)
        self.button_SignIn.move(x+30+150,70+60)
        self.button_SignIn.clicked.connect(self.on_click_SignIn)

        self.label1=QLabel(self)
        self.label1.setGeometry(15,30,20,20)
        self.label1.setText('ID')

        self.label2=QLabel(self)
        self.label2.setGeometry(15,90,20,20)
        self.label2.setText('PW')

    @pyqtSlot() 
    def on_click_LogIn(self):

        self.ID=self.IDbox.text()
        self.PW=self.PWbox.text()
        
        self.LogIn(self.ID,self.PW)

    @pyqtSlot()
    def on_click_SignIn(self):

        self.ID=self.IDbox.text()
        self.PW=self.PWbox.text()
        
        self.SignIn(self.ID,self.PW)

    def SignIn(self,ID,PW):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            mode="SignIn"
            sock.connect((self.HOST,self.PORT))
            data=ID+':'+PW+':'+mode 
            
            sock.send(data.encode())

            MsgRcv=sock.recv(1024).decode()

            msgb=QMessageBox(self)
            msgb.setWindowTitle('SignInAlert')
            msgb.setText(MsgRcv)
            msgb.show()


    def LogIn(self,ID,PW):
                        
        def delUI():
            self.IDbox.hide()
            self.PWbox.hide()
            self.button_LogIn.hide()
            self.button_SignIn.hide()
            self.label1.hide()
            self.label2.hide()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            
            mode="LogIn"
            sock.connect((self.HOST,self.PORT))
            data=ID+':'+PW+':'+mode
            sock.send(data.encode())

            MsgRcv=sock.recv(1024)
            
            b=MsgRcv.decode()

            if b:
                msgb=QMessageBox(self)
                msgb.setWindowTitle('LogInAlert')
                msg="Hello "+ID
                msgb.setText(msg)
                msgb.show()
                delUI()
                self.Enter(ID)
                
            if not b:
                msgb=QMessageBox(self)
                msgb.setWindowTitle('LogInAlert')
                msg="Incorrect ID or Password"
                msgb.setText(msg)
                msgb.show()

                
    def Enter(self,ID):

        m='c'
        lock.acquire()
        self.MsgSend.append(m)
        lock.release()

        lock.acquire()
        self.MsgSend.append(ID)
        lock.release()


        def on_press_Enter():
            msg=self.ChattingLineEdit.text()

            if msg!='':
                lock.acquire()
                data=ID+':'+msg
                self.MsgSend.append(data)
                lock.release()
                
            self.ChattingLineEdit.clear()

        def rcvMsg(sock):
            while True:
                try:
                    data=sock.recv(1024)
                    if not data:
                        break
                    print('r: ',data.decode())

                except Exception as e:
                    print(e)

        def LWappend(lw,i,data): #ListWidet Append

            lw.insertItem(i,data)
            



        def MsgHandling(): 
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.connect((self.HOST,self.PORT))

                t=Thread(target=self.rcvMsgReturn,args=(sock,))
                t.daemon=True
                t.start()
                
                i=0

                while True:
                    if self.MsgSend:
                        msg=self.MsgSend.pop(0)
                        print('s: ', msg)
                        sock.send(msg.encode())

                    if self.MsgReceive:
                        LWappend(self.listWidget_Chat,i,self.MsgReceive.pop(0))
                        i+=1
                        if i%2==0:
                            self.listWidget_Chat.scrollToBottom()
                        
                        
                        
                    else:
                        continue
            
        def setUI():
                
            self.setupUi(self)
            self.IDLabel.setText(ID)
            self.ChattingMenuLabel.setText('Main Chatting')
            self.MenuLabel.setText('Menu')
            self.ChattingLineEdit.returnPressed.connect\
                (on_press_Enter)
             
        setUI()

        t_m=Thread(target=MsgHandling,args=())
        t_m.daemon=True
        t_m.start()


def main():
    if __name__ =="__main__" : 
        app=QApplication(sys.argv)
        
        ci=ClientInterface()
        ci.show()
        
        sys.exit(app.exec_())
        
main()
