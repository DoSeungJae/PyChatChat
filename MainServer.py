import socketserver
import threading



HOST='127.0.0.1'
PORT=9009
lock= threading.Lock()

class UserManager:

    def __init__(self):
        self.users={} #CurrentUsers

        f=open('data.txt','r')

        lines=f.readlines()

        self.UserData={}
        self.UserData_temp={}

        if lines:
            for i in range(len(lines)):
                line=lines[i].strip().split(':')
                lock.acquire()
                self.UserData[line[0]]=line[1]
                lock.release()
        
        f.close()
        
        
    def isID(self,ID):
        if ID in self.UserData.keys() or ID in self.UserData_temp.keys():
            return True
            
        else:
            return False

    def isPW(self,ID,PW):
        if ID in self.UserData.keys():
            if self.UserData[ID]==PW:
                return True
            else:
                return False

        elif ID in self.UserData_temp.keys():
            if self.UserData_temp[ID]==PW:
                return True
            else:
                return False
        else:
            return False
        
    def addUser(self,username,conn,addr):
                
        lock.acquire()
        self.users[username]=(conn,addr)
        lock.release()
        print(self.users)

        self.sendMessageToAll(('[%s] connected' %username),username)
        print('+++ participant(s) : [%d]' %len(self.users))

        #return username

    def removeUser(self,username):
        if username not in self.users:
            return None 

        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll(('[%s] quit' %username),username)
        print('--- participant(s) : [%d]' %len(self.users))

    def messageHandler(self,username,msg):
        if msg[0]!='/':
            self.sendMessageToAll('[%s] : %s' %(username, msg),username)
            return None 

        if msg.strip() =='/quit':

            self.removeUser(username)
            return -1

    def sendMessageToAll(self,msg,username):
        for conn, addr in self.users.values():
            if not msg=='c':
                
                conn.send(msg.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman=UserManager()
    global state
    state=0

    def handle(self):
    
        m=self.request.recv(1024).decode() ##
         
        if state==1 and m=='c': ## 
            
            ID=self.request.recv(1024).decode()
            self.userman.addUser(ID,self.request, self.client_address)
            

            try:                
                while True:
                    msg=self.request.recv(1024).decode()
                    print(msg)
     
                    self.userman.sendMessageToAll(msg,ID)

            except Exception as e:
                print(e)
                print('[%s] quit' %self.client_address[0])
                self.userman.removeUser(ID)

        else:
                
            #data=self.request.recv(1024)
            data=m
            
            try:
                ID,PW,mode=data.split(":")   

            except Exception as e:
                print(e)
                mode='Enter'


            if mode=='SignIn':
                self.SignIn(ID,PW)

            elif mode=='LogIn':
                self.LogIn(ID,PW)


    def LogIn(self,ID,PW):
        global state
        
        if UserManager().isPW(ID,PW)==True:
            msg=ID
            self.request.send(msg.encode())
            state=1


        else:
            msg=''
            self.request.send(msg.encode())

            state=0

    def SignIn(self,ID,PW):
        bExist=UserManager().isID(ID)
        if bExist==True:
            msg='ID Already Exist. Retry'
            self.request.send(msg.encode())


        if bExist==False:
            msg='ID Created'
            self.request.send(msg.encode())
            f1=open('data.txt','a')
            UserManager().UserData_temp[ID]=PW
            ID=ID+':'
            f1.write(ID)
            f1.write(PW)
            f1.write('\n')
            f1.close()


    def ChattingServer(self,m): #username == ID

        m=self.request.recv(1024).decode()
        print(m)

        self.request.send(m.encode())


class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def runServer():
    print('+++ server started')
    print('Press "Ctrl + C" to close the server ')
    
    try:
        server=ChatingServer((HOST,PORT), MyTcpHandler)
        server.serve_forever()
    
    except KeyboardInterrupt:
        print('--- chatting server closed')
        server.shutdown()
        server.server_close()


runServer()


        