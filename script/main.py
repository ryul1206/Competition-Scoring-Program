#################################
# ROBOT COMPETITION of SKKU ME
# Version    : 2018-05-21 Rulebook
# Last updte : 2018-06-04
# Maintainer : Hong-ryul Jung (jung.hr.1206@gmail.com)
#################################
# -*- coding: utf-8 -*-
import threading
import time
from PyQt4 import QtCore, QtGui
import RPi.GPIO as GPIO

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import skku_gui_small

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

########################################
# $ gpio readall

EVENT = ['Game Start!',
         'Olympus mons IN', 
         'Olympus mons OUT',
         'Hill of mars IN',
         'Hill of mars OUT',
         'Line Tracing IN',
         'Finish Line!']

PIN = {EVENT[0]: 6,
       EVENT[1]: 13,
       EVENT[2]: 19,
       EVENT[3]: 26,
       EVENT[4]: 16,
       EVENT[5]: 20,
       EVENT[6]: 21}

type_SWITCH = GPIO.PUD_DOWN
type_IR = GPIO.PUD_UP

PIN_TYPE = type_IR

GPIO.setmode(GPIO.BCM)
for event in EVENT:
    GPIO.setup(PIN[event], GPIO.IN, pull_up_down=PIN_TYPE)

########################################
def this_sensor_pushed(id):
    if PIN_TYPE == type_SWITCH:
        return (GPIO.input(id) != 0)  # type_SWITCH
    else:
        return (GPIO.input(id) == 0)  # type_IR


class SKKU_robot(QtGui.QDialog, skku_gui_small.Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.init_time = 210
        self.init_hp = 50
        # var
        self.total_time = self.init_time
        self.hp = self.init_hp
        self.minus_score = 0
        self.num_collision = 0
        self.num_fall_obs = 0
        self.num_hand = 0
        self.num_fall_robot = 0
        self.not_pause = False
        self.event_time = 0
        self.start_time = 0
        self.save_time = 0
        # mission check
        self.check_box = [self.checkBox,
                          self.checkBox_2,
                          self.checkBox_3,
                          self.checkBox_4]
        for i in range(4):
            self.check_box[i].setChecked(False)
        # sensors
        self.sensor = {}
        for event in EVENT:
            self.sensor[event] = False
        # timer        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.data_update)
        self.timer.start(100)
        # file
        self.textbox = ""

    def bt_reset(self):
        # var
        self.total_time = self.init_time
        self.hp = self.init_hp
        self.minus_score = 0
        self.num_collision = 0
        self.num_fall_obs = 0
        self.num_hand = 0
        self.num_fall_robot = 0
        self.not_pause = False
        self.event_time = 0
        self.start_time = 0
        self.save_time = 0
        # mission check
        for i in range(4):
            self.check_box[i].setChecked(False)
        # sensors
        for event in EVENT:
            self.sensor[event] = False
        self.retranslateUi(QtGui.QDialog())
        # file
        self.textbox = ""

    def bt_pause(self):
        #if self.sensor_start:
        if self.not_pause:
            self.pushButton_2.setText(_translate("Dialog", "Resume", None))
            self.not_pause = False
            self.save_time = self.event_time
        else:
            self.pushButton_2.setText(_translate("Dialog", "Pause", None))
            self.not_pause = True
            self.start_time = time.time()
    
    def bt_force_start(self):
        self.not_pause = True
        # self.sensor_start = True
        self.sensor[EVENT[0]] = True
        self.start_time = time.time()
        self.append_log("> 0 sec : Game Start!")
    
    def bt_1st(self):
        self.num_collision += 1
    
    def bt_1st_cancel(self):
        if self.num_collision > 0:
            self.num_collision -= 1
    
    def bt_2nd(self):
        self.num_fall_obs += 1
    
    def bt_2nd_cancel(self):
        if self.num_fall_obs > 0:
            self.num_fall_obs -= 1
    
    def bt_3rd(self):
        self.num_hand += 1
    
    def bt_3rd_cancel(self):
        if self.num_hand > 0:
            self.num_hand -= 1
    
    def bt_4th(self):
        self.num_fall_robot += 1
    
    def bt_4th_cancel(self):
        if self.num_fall_robot > 0:
            self.num_fall_robot -= 1

    def bt_txt_save(self):
        # log
        self.append_log('__________ Summary __________')
        self.append_log('Time remaining:  '+str(self.total_time))
        self.append_log('Time lapse:      '+str(self.init_time-self.total_time))
        self.append_log('HP:              '+str(self.hp))
        self.append_log('Minus score:     -'+str(self.minus_score))
        for i in range(4):
            tmp = 'Mission '+str(i+1)+' was [ '
            tmp += ('Skipped ]' if self.check_box[i].isChecked() else 'Pass ]')
            self.append_log(tmp)
        self.append_log('# of collision:  '+str(self.num_collision))
        self.append_log('# of fallen obs: '+str(self.num_fall_obs))
        self.append_log('# of hand touch: '+str(self.num_hand))
        self.append_log('# of robot fall: '+str(self.num_fall_robot))
        # create file
        
        now = time.localtime()
        date = '%04d%02d%02d %02d-%02d-%02d' % (now.tm_year,
                                                now.tm_mon,
                                                now.tm_mday,
                                                now.tm_hour,
                                                now.tm_min,
                                                now.tm_sec)
        # cd ~/Competition-Scoring-Program; python main.py
        try:
            f = open('/home/pi/Desktop/'+date+'.txt', 'w')
            self.append_log('\n===== The file was safely saved! =====\n')
            f.write(self.textbox)
            f.close()
        except Exception as e:
            self.append_log('\n[ERROR] Something is wrong. T_T'+str(e)+'\n')

    def append_log(self, text):
        self.textbox += text
        self.textbox += '\n'
        self.textBrowser_log.append(_translate("Dialog", "<span>"+text+"</span>", None))

    def data_update(self):
        if self.not_pause:
            self.event_time = self.save_time + (time.time() - self.start_time)
        # data
        self.total_time = int(self.init_time-self.event_time)
        self.hp = self.init_hp
        self.hp -= 5 * (self.num_collision + self.num_fall_obs + self.num_fall_robot)
        self.hp -= 15 * self.num_hand
        for i in range(4):  # mission giveup
            if self.check_box[i].isChecked():
                self.hp -= 20
        self.minus_score = 5*self.num_collision + 10*self.num_fall_obs
        # lcd style
        if self.hp > 0:
            self.lcd_green.setStyleSheet(_fromUtf8("QLCDNumber{\n"
            "    color: rgb(0, 210, 0);    \n"
            "    background-color: rgb(255, 255, 255\n"
            ");\n"
            "}"))
        else:
            self.lcd_green.setStyleSheet(_fromUtf8("QLCDNumber{\n"
            "    color: rgb(255, 255, 255);    \n"
            "    background-color: rgb(255, 0, 0\n"
            ");\n"
            "}"))
        # lcd data
        self.lcd_blue.display(self.total_time)
        self.lcd_green.display(self.hp)
        self.lcd_red.display(self.minus_score)
        self.lcd_black_1.display(self.num_collision)
        self.lcd_black_2.display(self.num_fall_obs)
        self.lcd_black_3.display(self.num_hand)
        self.lcd_black_4.display(self.num_fall_robot)
        # log
        if not self.sensor[EVENT[0]]:
            if this_sensor_pushed(PIN[EVENT[0]]): # pushed
                self.bt_force_start()
        else:
            # only when start
            for event in EVENT[1:]:
                if (not self.sensor[event]) and this_sensor_pushed(PIN[event]):
                    self.sensor[event] = True
                    self.append_log("> "+str(self.event_time)+" sec : "+event)
                elif (not this_sensor_pushed(PIN[event])):
                    self.sensor[event] = False
        # print time.time()
        
    

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = SKKU_robot()
    dialog.show()
    sys.exit(app.exec_())
