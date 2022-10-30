
import PyQt5 as qt5
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys,os
import time
from PIL import Image
import random
import math
class DesktopPet(QWidget):


    def __init__(self,parent=None,**kwargs):
        ######################################初始化窗口###########################
        super(DesktopPet,self).__init__(parent)
        self.common_change_time=10000#10s
        self.rest_time=300000#5min
        self.walk_time=30000#30s
        self.resize(50,100)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.customContextMenuRequested.connect(self.RightClick)  # 绑定事件
        self.is_follow_mouse=False
        self.is_game_mod=False
        self.is_rest=True
        self.in_rest=False
        ######################读取路径信息#######################################
        f=open('path.txt','r',encoding="utf-8")
        self.path=f.readline()
        self.path=self.path.replace('\n','')
        f.close()
        f=open(self.path+'常态.txt','r',encoding="utf-8")
        str_num=f.readline()
        self.common_num=int(str_num)
        self.common_name=['' for i in range(self.common_num)]
        self.common_para = [1 for i in range(self.common_num)]
        for i in range(self.common_num):
            str_num = f.readline()
            self.common_para[i]=float(str_num)
            self.common_name[i]=f.readline()
            self.common_name[i] = self.common_name[i].replace('\n', '')
        f.close()
        f = open(self.path + '走动.txt', 'r', encoding="utf-8")
        str_num = f.readline()
        self.walk_num = int(str_num)
        str_num=f.readline()
        self.walk_para=float(str_num)
        self.walk_name = ['' for i in range(self.walk_num)]
        for i in range(self.walk_num):
            self.walk_name[i] = f.readline()
            self.walk_name[i] = self.walk_name[i].replace('\n', '')
        f.close()
        f=open(self.path + '抖动.txt', 'r', encoding="utf-8")
        self.drag_name=f.readline()
        self.drag_name = self.drag_name.replace('\n', '')
        f.close()
        f = open(self.path + '休息.txt', 'r', encoding="utf-8")
        str_num = f.readline()
        self.rest_num = int(str_num)
        self.rest_name = ['' for i in range(self.rest_num)]
        for i in range(self.rest_num):
            self.rest_name[i] = f.readline()
            self.rest_name[i] = self.rest_name[i].replace('\n', '')
        f.close()
        #####################################加载图片以及计时器################################
        self.actpath=self.path+self.common_name[0]
        self.show_image=self.LoadPetImages(self.actpath)
        self.show()
        self.img = QLabel(self)
        self.layer = QVBoxLayout()
        self.layer.addWidget(self.img)
        self.setLayout(self.layer)
        self.actTimer=QTimer()
        self.actTimer.timeout.connect(self.act)
        self.actTimer.start(40*len(self.show_image))
        self.commonTimer=QTimer()
        self.commonTimer.timeout.connect(self.changecommon)
        self.commonTimer.start(self.common_change_time)
        self.restTimer=QTimer()
        self.restTimer.timeout.connect(self.rest)
        #self.restTimer.start(self.rest_time)
        self.walkTimer=QTimer()
        self.walkTimer.timeout.connect(self.walk)
        self.walkTimer.start(self.walk_time)
        ######################################初始调整#######################################
        self.randomPosition()
        #######################################test area#####################################

    def walk(self):
        if random.random()>0.8:
            screen_geo=QDesktopWidget().screenGeometry()
            self.walk_act_and_move(int((screen_geo.width()-self.width())*(random.random()*0.2+random.randint(0,1)*0.8)),int( (screen_geo.height()-self.height())*(random.random()*0.2+random.randint(0,1)*0.8)))
        return
    def walk_act_and_move(self,x,y):
        self.commonTimer.stop()
        print(x,y)
        dis=(x-self.pos().x())*(x-self.pos().x())+(y-self.pos().y())*(y-self.pos().y())
        dis=math.sqrt(dis)
        sinx = (x - self.pos().x())/dis
        siny=(y-self.pos().y())/dis

        self.actpath = self.path + self.walk_name[random.randint(0, self.walk_num - 1)]
        self.show_image = self.LoadPetImages(self.actpath)
        move_speed = 100*self.walk_para/len(self.show_image)
        move_time = round(dis / move_speed)
        screen_geo = QDesktopWidget().screenGeometry()
        i=0
        while i<move_time:
            self.move(self.pos().x()+sinx*move_speed,self.pos().y()+siny*move_speed)
            self.SetImage(self.actpath + '\\' + self.show_image[i % len(self.show_image)])
            i+=1
            time.sleep(0.03)
            if self.pos().x()<0 or self.pos().y()<0:
                print(self.pos())
                break
            if self.pos().x()>=screen_geo.width()-self.width()or self.pos().y()>=screen_geo.height()-self.height():
                print(self.pos())
                break
        self.actpath = self.path + self.common_name[random.randint(0, self.common_num - 1)]
        self.show_image = self.LoadPetImages(self.actpath)
        self.commonTimer.start(self.common_change_time)
    def rest(self):
        if self.is_rest==True:
            self.commonTimer.stop()
            self.restTimer.stop()
            self.walkTimer.stop()
            self.actpath = self.path + self.rest_name[random.randint(0, self.rest_num - 1)]
            self.show_image = self.LoadPetImages(self.actpath)
            self.in_rest=True
        else:
            self.is_rest=True
    def rest_recover(self):
        self.in_rest = False
        self.commonTimer.start(self.common_change_time)
        self.restTimer.start(self.rest_time)
        self.walkTimer.start(self.walk_time)
        self.actpath = self.path + self.common_name[random.randint(0, self.common_num - 1)]
        self.show_image = self.LoadPetImages(self.actpath)
    def changecommon(self):
        if (self.is_follow_mouse==True) and (self.drag_name!=''):
            return
        if random.random()>=0.7:
            self.actpath = self.path + self.common_name[random.randint(0,self.common_num-1)]
            self.show_image = self.LoadPetImages(self.actpath)
            self.commonTimer.start(self.common_change_time)
        else:
            self.commonTimer.start(1000)
        return
    def act(self):
        for i in range(len(self.show_image)):
            self.SetImage(self.actpath + '\\' + self.show_image[i])
            time.sleep(0.03)
        return
    def randomPosition(self):
        #just for test
        screen_geo=QDesktopWidget().screenGeometry()
        width=(screen_geo.width()-self.width())*random.random()
        height=(screen_geo.height()-self.height())*(random.random()*0.2+0.8)
        self.move(width,height)

    def SetImage(self,path):
        self.img.setPixmap(QPixmap(path))
        self.repaint()
        return
    def LoadPetImages(self,path):
        file_list=os.listdir(path)
        file_list.sort()
        return file_list

    def quit(self):
        app=QApplication.instance()
        app.quit()

    def GameMod(self):

        self.is_game_mod = True
        self.restTimer.stop()
    def quitGameMod(self):
        if self.is_game_mod==True:
            self.is_game_mod = False
            self.restTimer.start(self.rest_time)
    ######################################events################################
    def mousePressEvent(self,event):
        if self.is_game_mod==True:
            return

        if self.in_rest==True:
            self.is_rest=True
            self.rest_recover()
        elif self.is_rest==True:
            self.is_rest=False

        if event.button()==Qt.LeftButton:
            self.is_follow_mouse=True
            if self.drag_name!='':
                self.actpath = self.path + self.drag_name
                self.show_image = self.LoadPetImages(self.actpath)
                self.commonTimer.stop()
            self.mouse_drag_pos=event.globalPos()-self.pos()
            event.accept()
            return


    def mouseMoveEvent(self,event):
        if self.is_game_mod==True:
            return

        if self.in_rest==True:
            self.is_rest=True
            self.rest_recover()
        elif self.is_rest==True:
            self.is_rest=False
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos()-self.mouse_drag_pos)
            event.accept()
            return

    def mouseReleaseEvent(self, event):
        if self.is_game_mod==True:
            return
        self.is_follow_mouse=False
        self.actpath = self.path + self.common_name[random.randint(0,self.common_num-1)]
        self.show_image = self.LoadPetImages(self.actpath)
        self.commonTimer.start(self.common_change_time)
    def RightClick(self,pos):
        menu = QMenu(self)
        if self.is_game_mod==False:
            action = menu.addAction('游戏模式')
            action.triggered.connect(self.GameMod)
        if self.is_game_mod==True:
            action = menu.addAction('退出游戏模式')
            action.triggered.connect(self.quitGameMod)
        action = menu.addAction('退出')
        action.triggered.connect(self.quit)
        action = menu.addAction('test')
        action.triggered.connect(self.walk)
        #action = menu.addAction('delete')
        #action.triggered.connect(...)
        menu.exec_(QCursor.pos())

if __name__=='__main__':
    app = QApplication(sys.argv)
    a=DesktopPet()
    sys.exit(app.exec_())
