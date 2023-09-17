print("Python starting......")
from datetime import datetime
import matplotlib.style
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import numpy as np
from scipy import interpolate
from csv import writer

import trajectory
import channel_config_copy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt

import tmotorCAN

from functools import lru_cache

from matplotlib import rcParams
rcParams['path.simplify'] = False

matplotlib.style.use('fast')
START = 0
START_MOTOR = [0,0,0,0]

# RELATIVE
MINPOSHIP = -90 * np.pi / 180
MAXPOSHIP = 180 * np.pi / 180
MINPOSKNEE = -90 * np.pi / 180
MAXPOSKNEE = 180 * np.pi / 180
# MAXVEL = -15
# MAXPOS = 15

traj_max_hip = 25
traj_min_hip = -7
traj_max_knee = -7
traj_min_knee = -65

KP = 10
KD = 1

TIMES = [0, 1, 2, 3, 4]

# MOTOR has reverse sign conventions

OMEGAS = {5: 2 * np.pi / 2.5, 4: 2 * np.pi / 3.5, 3: 2 *
          np.pi / 4.5, 2: 2 * np.pi / 5.5, 1: 2 * np.pi / 6.5}

HIP_VALUES = [30, 15, 0, -15, 5]
KNEE_VALUES = [30, 10, 0, -15, 5]

LEFT_HIP_LINK_TORQUE = 10
LEFT_KNEE_LINK_TORQUE = 10
RIGHT_HIP_LINK_TORQUE = 10
RIGHT_KNEE_LINK_TORQUE = 10

NUMS = 50
out_lis=[]

class Heading(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        font = self.font()
        font.setBold(True)
        font.setPointSize(23)
        self.setFont(font)


class Plot(QDialog):

    def __init__(self):
        super().__init__()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.selection = 0
        self.hip_traj_selection = trajectory.theta_5
        self.knee_traj_selection = trajectory.theta_6_rel

    def plot(self):

        # x = TIMES

        # self.figure.clear()
        # ax1 = self.figure.add_subplot(211)
        # y = self.data1

        # x_new = np.linspace(min(x), max(x), 50)
        # bspline = interpolate.make_interp_spline(x, y)
        # y_new = bspline(x_new)

        # ax1.axhline(y=0, color='k')
        # ax1.axvline(x=0, color='k')

        # ax1.plot(x_new, y_new, '-')
        # ax1.plot(x, y, 's')
        # ax1.set_title("Hip")

        # ax2 = self.figure.add_subplot(212)
        # y = self.data2

        # x_new = np.linspace(min(x), max(x), 50)
        # bspline = interpolate.make_interp_spline(x, y)
        # y_new = bspline(x_new)

        # ax2.axhline(y=0, color='k')
        # ax2.axvline(x=0, color='k')

        # ax2.plot(x_new, y_new, '-')
        # ax2.plot(x, y, 's')
        # ax2.set_title("Knee")

        # self.canvas.draw()
        
        # Selecting trajectories
        x = TIMES

        self.figure.clear()
        ax1 = self.figure.add_subplot(211)

        x_new = np.linspace(min(x), max(x), 50)
        
        if self.selection == 2:
            y = lambda x:(1+10*np.pi/180)*self.hip_traj_selection(4,x,0,1)*180/np.pi
        elif self.selection == 3:
            y = lambda x:(1+20*np.pi/180)*self.hip_traj_selection(4,x,0,1)*180/np.pi
        else:
            y = lambda x:self.hip_traj_selection(4,x,0,1)*180/np.pi
        y_new = y(x_new)

        ax1.axhline(y=0, color='k')
        ax1.axvline(x=0, color='k')

        ax1.plot(x_new, y_new, '-')
        ax1.set_title("Hip - Flexion / Extension")
        ax1.set_ylabel("Angle(degrees)")
        ax1.set_xlabel("Time(seconds)")

        ax2 = self.figure.add_subplot(212)

        x_new = np.linspace(min(x), max(x), 50)
        if self.selection == 0:
            y = lambda x:self.knee_traj_selection(4,x,0,1)*180/np.pi
        else:
            y = lambda x:self.knee_traj_selection(4,x,0,1)*180/np.pi + 5
        y_new = y(x_new)
        
        ax2.axhline(y=0, color='k')
        ax2.axvline(x=0, color='k')

        ax2.plot(x_new, y_new, '-')
        ax2.set_title("Knee - Flexion / Extension")
        ax2.set_ylabel("Angle(degrees)")
        ax2.set_xlabel("Time(seconds)")

        self.figure.tight_layout()
        self.canvas.draw()


class PlotData(QObject):
    def __init__(self):
        super().__init__()

        self.times = np.arange(-NUMS/10, 0, 0.1)
        self.data1 = np.arange(0, NUMS, 1)
        self.data2 = np.arange(0, NUMS, 1)
        self.data3 = np.arange(0, NUMS, 1)
        self.data4 = np.arange(0, NUMS, 1)


class PlotScreen(QDialog):

    def __init__(self):
        super().__init__()
        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.data_object = PlotData()

    def plot(self):

        self.figure.clear()
        ax1 = self.figure.add_subplot(221)
        ax1.plot(self.data_object.times[-NUMS:],
                self.data_object.data1[-NUMS:], '-')
        ax1.set_title("Left Hip")
        ax1.set_xlim(
            self.data_object.times[-1] - 5, self.data_object.times[-1])
        ax1.set_ylim(-100, 100)

        ax2 = self.figure.add_subplot(222)
        ax2.plot(self.data_object.times[-NUMS:],
                self.data_object.data2[-NUMS:], '-')
        ax2.set_title("Left Knee")
        ax2.set_xlim(
            self.data_object.times[-1] - 5, self.data_object.times[-1])
        ax2.set_ylim(-100, 100)

        ax3 = self.figure.add_subplot(223)
        ax3.plot(self.data_object.times[-NUMS:],
                self.data_object.data3[-NUMS:], '-')
        ax3.set_title("Right Hip")
        ax3.set_xlim(
            self.data_object.times[-1] - 5, self.data_object.times[-1])
        ax3.set_ylim(-100, 100)

        ax4 = self.figure.add_subplot(224)
        ax4.plot(self.data_object.times[-NUMS:],
                self.data_object.data4[-NUMS:], '-')
        ax4.set_title("Right Knee")
        ax4.set_xlim(
            self.data_object.times[-1] - 5, self.data_object.times[-1])
        ax4.set_ylim(-100, 100)

        self.figure.tight_layout(pad=3)
        self.canvas.draw()


class MotorInteract(QObject):
    def __init__(self):
        super().__init__() 
        self.mode = None
        self.on = False
        self.data = []
        self.trajectory = 0

        self.minimum_position_hip = MINPOSHIP
        self.maximum_position_hip = MAXPOSHIP
        self.minimum_position_knee = MINPOSKNEE
        self.maximum_position_knee = MAXPOSKNEE

        self.left_hip = True
        self.left_knee = True
        self.right_hip = True
        self.right_knee = True

        self.left_hip_motor = tmotorCAN.tmotor(
            3, "AK10-9", 5, 2, MINPOSHIP, MAXPOSHIP)
        self.left_knee_motor = tmotorCAN.tmotor(
            4, "AK10-9", 5, 2, MINPOSKNEE, MAXPOSKNEE)
        self.right_hip_motor = tmotorCAN.tmotor(
            1, "AK10-9", 5, 2, MINPOSHIP, MAXPOSHIP)
        self.right_knee_motor = tmotorCAN.tmotor(
            2, "AK10-9", 5, 2, MINPOSKNEE, MAXPOSKNEE)

        # self.left_hip_motor = tmotorCAN.tmotor(1, "AK80-64")
        # self.left_knee_motor = tmotorCAN.tmotor(2, "AK80-64")
        # self.right_hip_motor = tmotorCAN.tmotor(3, "AK80-64")
        # self.right_knee_motor = tmotorCAN.tmotor(4, "AK80-64")

        self.left_hip_pos = 0
        self.left_knee_pos = 0
        self.right_hip_pos = 0
        self.right_knee_pos = 0

        self.left_hip_vel = 0
        self.left_knee_vel = 0
        self.right_hip_vel = 0
        self.right_knee_vel = 0
        
        self.hip_kp = 70
        self.knee_kp = 50
        self.kd = 2

        self.left_hip_trajectory = trajectory.theta_5
        self.right_hip_trajectory = trajectory.theta_5
        self.left_knee_trajectory = trajectory.theta_6_rel
        self.right_knee_trajectory = trajectory.theta_6_rel
        self.left_hip_trajectory_vel = trajectory.omega_5
        self.right_hip_trajectory_vel = trajectory.omega_5
        self.left_knee_trajectory_vel = trajectory.omega_6_rel
        self.right_knee_trajectory_vel = trajectory.omega_6_rel

        self.left_hip_link_weight = LEFT_HIP_LINK_TORQUE
        self.left_knee_link_weight = LEFT_KNEE_LINK_TORQUE
        self.right_hip_link_weight = RIGHT_HIP_LINK_TORQUE
        self.right_knee_link_weight = RIGHT_KNEE_LINK_TORQUE

        self.w = OMEGAS[1]
        self.right_delay = (2*np.pi/self.w)*0.75/1.39
        
        if(self.trajectory == 0):
            self.hip_amp = 1
            self.knee_amp = 1
            self.hip_offset = 5*np.pi/180
            self.knee_offset = 0*np.pi/180
        elif(self.trajectory == 1):
            self.hip_amp = 1
            self.knee_amp = 1
            self.hip_offset = 5*np.pi/180
            self.knee_offset = 4*np.pi/180
        elif(self.trajectory == 2):
            self.hip_amp = (1+10*np.pi/180)
            self.knee_amp = 1
            self.hip_offset = 5*np.pi/180
            self.knee_offset = 4*np.pi/180
        elif(self.trajectory == 3):
            self.hip_amp = (1+20*np.pi/180)
            self.knee_amp = 1
            self.hip_offset = 5*np.pi/180
            self.knee_offset = 4*np.pi/180
        

    def run_motor(self):
        global START, START_MOTOR
        while True:
            
            if (self.on):
                if START==1:
                    start_time = time.time()
                START=0
                current_time = time.time()
                delta_time = current_time - start_time
                if (self.mode == 1):
                    if 0 in START_MOTOR:
                        if(np.abs(self.hip_amp*self.left_hip_trajectory(self.w, delta_time, 0,1)+self.hip_offset)<0.5*(np.pi/180)):
                            START_MOTOR[2] = 1 
                        if(np.abs(self.knee_amp*self.left_knee_trajectory(self.w, delta_time, 0,1)+self.knee_offset)<7*(np.pi/180) and np.abs(self.knee_amp*self.left_knee_trajectory(self.w, delta_time, 0,1)+self.knee_offset)>5*(np.pi/180)):
                            START_MOTOR[3] = 1
                        if(np.abs(self.hip_amp*self.right_hip_trajectory(self.w, delta_time + self.right_delay, 0,1)+self.hip_offset)<0.5*(np.pi/180)):
                            START_MOTOR[0] = 1
                            print(delta_time)
                        if(np.abs(self.knee_amp*self.right_knee_trajectory(self.w, delta_time + self.right_delay, 0,1)+self.knee_offset)<7*(np.pi/180) and np.abs(self.knee_amp*self.right_knee_trajectory(self.w, delta_time + self.right_delay, 0, 1)+self.knee_offset)>5*(np.pi/180)):
                            START_MOTOR[1] = 1

                    if (self.left_hip and START_MOTOR[2] == 1):
                            self.left_hip_motor.attain(
                                self.hip_amp*self.left_hip_trajectory(self.w, delta_time, 0, 1)+self.hip_offset, self.hip_amp*self.left_hip_trajectory_vel(self.w, delta_time, 0, 1), 0, self.hip_kp, self.kd)
                    if (self.left_knee and START_MOTOR[3] == 1):
                            self.left_knee_motor.attain(
                                self.knee_amp*self.left_knee_trajectory(self.w, delta_time, 0, 1)+self.knee_offset + 3*np.pi/180, self.knee_amp*self.left_knee_trajectory_vel(self.w, delta_time, 0, 1), 0, self.knee_kp, self.kd)
                    if (self.right_hip and START_MOTOR[0] == 1):
                            self.right_hip_motor.attain(
                                        -self.hip_amp*self.right_hip_trajectory(self.w, delta_time + self.right_delay, 0, 1)+self.hip_offset, -self.hip_amp*self.right_hip_trajectory_vel(self.w, delta_time + self.right_delay, 0, 1), 0, self.hip_kp, self.kd)
                                        # self.hip_amp*self.right_hip_trajectory(self.w, delta_time + self.right_delay, 0, 1)-self.hip_offset, self.hip_amp*self.right_hip_trajectory_vel(self.w, delta_time + self.right_delay, 0, 1), 0, self.hip_kp, self.kd)
                    if (self.right_knee and START_MOTOR[1] == 1):
                            self.right_knee_motor.attain(
                                -self.knee_amp*self.right_knee_trajectory(self.w, delta_time + self.right_delay, 0, 1)-self.knee_offset, -self.knee_amp*self.right_knee_trajectory_vel(self.w, delta_time + self.right_delay, 0, 1), 0, self.knee_kp, self.kd)

                # elif (self.mode == 2):
                #     # gravity compensation mode
                #     time.sleep(0.08)
                #     if (self.left_hip):
                #         self.left_hip_motor.attain(
                #             self.left_hip_pos, self.left_hip_vel, LEFT_HIP_LINK_TORQUE * np.sin(self.left_hip_pos), 5, 0.5)
                #     if (self.left_knee):
                #         self.left_knee_motor.attain(
                #             self.left_knee_pos, self.left_knee_vel, LEFT_KNEE_LINK_TORQUE * np.sin(self.left_hip_pos + self.left_knee_pos), 1, 0.3)
                #     if (self.right_hip):
                #         self.right_hip_motor.attain(
                #             self.right_hip_pos, self.right_hip_vel, RIGHT_HIP_LINK_TORQUE * np.sin(self.right_hip_pos), 1, 1)
                #     if (self.right_knee):
                #         self.right_knee_motor.attain(
                #             self.right_knee_pos, self.right_knee_vel, -RIGHT_KNEE_LINK_TORQUE * np.sin(self.right_hip_pos + self.right_knee_pos), 10, 1)

                current_time = time.time()
                delta_time = current_time - start_time
                try:
                    self.data.append([delta_time,*tmotorCAN.tmotor.read_can()])
                except:
                    pass

    def start_motors(self):
        tmotorCAN.tmotor.channel = channel_config_copy.start_channel(0)
        if (self.left_hip):
            self.left_hip_motor.start_motor()
        if (self.left_knee):
            self.left_knee_motor.start_motor()
        if (self.right_hip):
            self.right_hip_motor.start_motor()
        if (self.right_knee):
            self.right_knee_motor.start_motor()
        self.left_hip_motor.attain(0,0,0,0,0)
        self.left_knee_motor.attain(0,0,0,0,0)
        self.right_hip_motor.attain(0,0,0,0,0)
        self.right_knee_motor.attain(0,0,0,0,0)
        time.sleep(0.03)
        # self.go_to_origin()

    def go_to_origin(self):
        if (self.left_hip):
            self.left_hip_motor.go_to_origin()
        if (self.left_knee):
            self.left_knee_motor.go_to_origin()
        if (self.right_hip):
            self.right_hip_motor.go_to_origin()
        if (self.right_knee):
            self.right_knee_motor.go_to_origin()

    def turn_off(self):
        # self.go_to_origin()
        global START_MOTOR
        START_MOTOR = [0,0,0,0]
#         time.sleep(1)
        if (self.left_hip):
            self.left_hip_motor.stop_motor()
        if (self.left_knee):
            self.left_knee_motor.stop_motor()
        if (self.right_hip):
            self.right_hip_motor.stop_motor()
        if (self.right_knee):
            self.right_knee_motor.stop_motor()
        time.sleep(0.1)
        tmotorCAN.tmotor.channel.busOff()
        tmotorCAN.tmotor.channel.close()



class InputPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.label1 = QLabel("Maximum position (hip)")
        self.input1 = QLineEdit()
        self.input1.setText(str(traj_max_hip))
        self.label2 = QLabel("Minimum position (hip)")
        self.input2 = QLineEdit()
        self.input2.setText(str(traj_min_hip))
        self.label3 = QLabel("Maximum position (knee)")
        self.input3 = QLineEdit()
        self.input3.setText(str(traj_max_knee))
        self.label4 = QLabel("Minimum position (knee)")
        self.input4 = QLineEdit()
        self.input4.setText(str(traj_min_knee))

        self.button = QPushButton("Save Data")

        for line in self.input1, self.input2, self.input3, self.input4:
            line.setMaxLength(3)

        layout = QGridLayout()
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(0, 1)

        layout.addWidget(self.label1, 0, 0)
        layout.addWidget(self.input1, 0, 1)
        layout.addWidget(self.label2, 1, 0)
        layout.addWidget(self.input2, 1, 1)
        layout.addWidget(self.label3, 2, 0)
        layout.addWidget(self.input3, 2, 1)
        layout.addWidget(self.label4, 3, 0)
        layout.addWidget(self.input4, 3, 1)
        layout.addWidget(self.button, 4, 1)

        self.setLayout(layout)


class InitialScreenLeftPanel(QWidget):
    def __init__(self):
        super().__init__()

        # self.heading1 = Heading("Modes Available")

        # self.button1 = QRadioButton("Automatic")
        # self.button2 = QRadioButton("Physiotherapist Guided")
        
        self.heading = Heading("Exoskeleton")

        self.label0 = QLabel("Patient Name")
        self.line0 = QLineEdit()
        # self.line0.setMaxLength(3)

        self.heading2 = Heading("Motors activated")
        self.checkbox1 = QCheckBox("Left Hip Motor")
        self.checkbox2 = QCheckBox("Left Knee Motor")
        self.checkbox3 = QCheckBox("Right Hip Motor")
        self.checkbox4 = QCheckBox("Right Knee Motor")

        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(True)
        self.checkbox3.setChecked(True)
        self.checkbox4.setChecked(True)
        
        self.button = QPushButton("Save Patient Data")

        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.label0)
        layout.addWidget(self.line0)
        layout.addWidget(self.heading2)
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)
        layout.addWidget(self.checkbox4)
        layout.addStretch(1)
        layout.addWidget(self.button)

        self.setLayout(layout)


# class InitialScreenMiddlePanel(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.heading = Heading("Patient Details")

#         self.label0 = QLabel("Patient Name")
#         self.line0 = QLineEdit()
#         self.label1 = QLabel("Patient Weight (in kilograms)")
#         self.line1 = QLineEdit()
#         self.label2 = QLabel("Link 1 Length (in metre)")
#         self.line2 = QLineEdit()
#         self.label3 = QLabel("Link 2 Length (in metre)")
#         self.line3 = QLineEdit()

#         for line in self.line1, self.line2, self.line3:
#             line.setMaxLength(3)

#         self.button = QPushButton("Save Patient Data")

#         layout = QVBoxLayout()
#         layout.addWidget(self.heading)
#         layout.addWidget(self.label0)
#         layout.addWidget(self.line0)
#         layout.addWidget(self.label1)
#         layout.addWidget(self.line1)
#         layout.addWidget(self.label2)
#         layout.addWidget(self.line2)
#         layout.addWidget(self.label3)
#         layout.addWidget(self.line3)
#         layout.addStretch(1)
#         layout.addWidget(self.button)

#         self.setLayout(layout)


class InitialScreenRightPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.heading = Heading("Instructions for Usage")
        self.list = QListWidget()
        self.list.setFixedHeight(300)
        self.list.addItems(["1. Enter Patient Details",
                        "2. Select The Motors to be activated", "3. Handle Device Carefully"])
        self.list.setWordWrap(True)
        self.button = QPushButton("Continue")

        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.list)
        layout.addStretch(1)
        layout.addWidget(self.button)
        self.setLayout(layout)


class InitialScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.left_panel = InitialScreenLeftPanel()
    #    left_panel.setStyleSheet("background-color: white;")
        # self.middle_panel = InitialScreenMiddlePanel()
        self.right_panel = InitialScreenRightPanel()

        initial_screen_layout = QHBoxLayout()
        initial_screen_layout.addWidget(self.left_panel)

        # initial_screen_layout.addWidget(self.middle_panel)
        initial_screen_layout.addWidget(self.right_panel)

        self.setLayout(initial_screen_layout)


# class GravityCompensationScreenLeftPanel(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.state = False

#         self.heading = Heading("Maximum and Minimum Values")
#         self.input_panel = InputPanel()

#         self.label = QLabel("")

#         self.button0 = QPushButton("Start Motor")
#         self.button1 = QPushButton("Start Therapy")
#         self.button2 = QPushButton("Stop Therapy")
#         self.button3 = QPushButton("Go to Origin")

#         self.button0.setDisabled(False)
#         self.button1.setDisabled(True)
#         self.button2.setDisabled(True)
#         self.button3.setDisabled(True)

#         layout = QVBoxLayout()
#         layout.addWidget(self.heading)
#         layout.addWidget(self.input_panel)
#         layout.addWidget(self.label)
#         layout.addWidget(self.button0)
#         layout.addWidget(self.button1)
#         layout.addWidget(self.button2)
#         layout.addWidget(self.button3)
#         layout.addStretch(1)
#         self.setLayout(layout)


# class GravityCompensationScreenRightPanel(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.heading = Heading("Plotting Data")
#         # self.list = QListWidget()
#         # self.list.addItems(["1. Gravity Compensation Mode: Weight of patient will be provided by motor", "2. Physiotherapist Supervision is required"])
#         # self.list.setWordWrap(True)

#         self.graph = PlotScreen()
#         self.button = QPushButton("Back")

#         layout = QVBoxLayout()
#         layout.addWidget(self.heading)
#         # layout.addWidget(self.list)
#         layout.addWidget(self.graph)
#         layout.addStretch(1)
#         layout.addWidget(self.button)
#         self.setLayout(layout)


# class GravityCompensationScreen(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.left_panel = GravityCompensationScreenLeftPanel()
#         self.right_panel = GravityCompensationScreenRightPanel()

#         layout = QHBoxLayout()
#         layout.addWidget(self.left_panel)
#         layout.addWidget(self.right_panel)

#         self.setLayout(layout)


class TrajectoryInput(QWidget):
    def __init__(self):
        super().__init__()

        # layout = QGridLayout()
        # layout.setColumnStretch(0, 1)
        # layout.setColumnStretch(1, 0)
        # layout.setColumnStretch(2, 1)
        # layout.setColumnStretch(3, 0)

        # self.texts1 = []
        # self.texts2 = []
        # self.texts3 = []
        # self.inputs1 = []
        # self.inputs2 = []

        # for i in range(1, 6):

        #     self.texts1.append(QLabel(f"t {TIMES[i - 1]}"))
        #     self.texts2.append(QLabel(f"hip angle {i}"))
        #     self.inputs1.append(QLineEdit())
        #     self.texts3.append(QLabel(f"knee angle {i}"))
        #     self.inputs2.append(QLineEdit())

        #     layout.addWidget(self.texts1[-1], i - 1, 0)
        #     layout.addWidget(self.texts2[-1], i - 1, 1)
        #     layout.addWidget(self.inputs1[-1], i - 1, 2)
        #     layout.addWidget(self.texts3[-1], i - 1, 3)
        #     layout.addWidget(self.inputs2[-1], i - 1, 4)

        # for i in range(0, 5):
        #     self.inputs1[i].setText(str(HIP_VALUES[i]))
        #     self.inputs2[i].setText(str(KNEE_VALUES[i]))

        # self.setLayout(layout)
        
        
        # Selecting trajectories from options
        self.button1 = QRadioButton("Normal Trajectory")
        self.button2 = QRadioButton("Marching Trajectory")
        self.button3 = QRadioButton("PBWST Trajectory 1")
        self.button4 = QRadioButton("PBWST Trajectory 2")
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        
        self.button1.setChecked(True)
        
        self.setLayout(layout)


class PositionControlScreenLeftPanel(QWidget):
    def __init__(self):
        super().__init__()

        heading = Heading("Trajectory")

        self.trajectory_input = TrajectoryInput()
        
        self.heading2 = Heading("Force applied")
        
        self.buttona = QRadioButton("Low")
        self.buttonb = QRadioButton("Medium")
        self.buttonc = QRadioButton("High")
        
        self.buttona.setChecked(True)
        
        self.button = QPushButton("Update")

        self.label = QLabel("Note: Select options \n and press Update")

        layout = QVBoxLayout()

        
        layout.addWidget(self.heading2)
        layout.addWidget(self.buttona)
        layout.addWidget(self.buttonb)
        layout.addWidget(self.buttonc)
        
        layout.addWidget(heading)
        layout.addWidget(self.trajectory_input)
        layout.addWidget(self.button)
        
        layout.addStretch(1)
        layout.addWidget(self.label)

        self.setLayout(layout)

# class PositionControlScreenMiddlePanel(QWidget):
#     def __init__(self):
#         self.layout = QVBoxLayout()
#         self.layout.addStretch(1)
#         self.setLayout(self.layout)
#         super().__init__()
        
#         self.heading2 = Heading("Force applied")
        
#         self.button1 = QRadioButton("Low")
#         self.button2 = QRadioButton("Medium")
#         self.button3 = QRadioButton("High")
        
#         layout = QVBoxLayout()
#         layout.addWidget(self.heading2)
#         layout.addWidget(self.button1)
#         layout.addWidget(self.button2)
#         layout.addWidget(self.button3)
#         layout.addStretch(1)
#         self.setLayout(layout)
        

class PositionControlScreenRightPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.heading = Heading("Plotting Data")
        self.graph = Plot()
        self.button1 = QPushButton("Continue")
        self.button2 = QPushButton("Back")

        self.button1.setDisabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.graph)
        layout.addStretch(1)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.setLayout(layout)


class PositionContolScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.right_panel = PositionControlScreenRightPanel()
        # self.middle_panel = PositionControlScreenMiddlePanel()
        self.left_panel = PositionControlScreenLeftPanel()
        layout = QHBoxLayout()
        layout.addWidget(self.left_panel)
        # layout.addWidget(self.middle_panel)
        layout.addWidget(self.right_panel)

        self.setLayout(layout)


class PositionControlFinalScreenRightPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.heading = Heading("Maximum and Minimum Values")

        # self.input_panel = InputPanel()
        self.label = QLabel("")

        self.button0 = QPushButton("Start Motor")
        self.button1 = QPushButton("Start Therapy")
        self.button2 = QPushButton("Stop Therapy")
        self.button3 = QPushButton("Go to Origin")
        
        self.button = QPushButton("Back")

        layout = QVBoxLayout()

        self.button0.setDisabled(False)
        self.button1.setDisabled(True)
        self.button2.setDisabled(True)
        self.button3.setDisabled(True)

        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setMinimum(1)
        # self.slider.setMaximum(5)
        # self.slider.setTickInterval(5)
        # self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        # label1 = QLabel("High Speed")
        # label2 = QLabel("Low Speed")
        # layout1 = QHBoxLayout()
        # layout1.addWidget(label1)
        # layout1.addStretch(1)
        # layout1.addWidget(label2)
        # unit = QWidget()
        # unit.setLayout(layout1)
        self.label = QLabel("Speed")

        # layout.addWidget(self.heading)
        # layout.addWidget(self.input_panel)
        # layout.addWidget(self.label)
        # layout.addWidget(self.slider)
        # layout.addWidget(unit)
        layout.addWidget(self.button0)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addStretch(1)
        layout.addWidget(self.button)

        self.setLayout(layout)


class PositionControlFinalScreenLeftPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.heading = Heading("Speed")
        self.button1 = QRadioButton("1 kmph")
        self.button2 = QRadioButton("1.5 kmph")
        self.button3 = QRadioButton("2 kmph")
        self.button4 = QRadioButton("2.5 kmph")
        self.button5 = QRadioButton("3 kmph")

        # self.graph = PlotScreen()
        

        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.button5)
        layout.addStretch(1)
        # layout.addWidget(self.graph)
        
        self.setLayout(layout)


class PositionControlFinalScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.left_panel = PositionControlFinalScreenLeftPanel()
        self.right_panel = PositionControlFinalScreenRightPanel()
        
        layout = QHBoxLayout()
        layout.addWidget(self.left_panel)
        layout.addWidget(self.right_panel)
        self.setLayout(layout)


class PositionContolWithGravityScreenLeftPanel(QWidget):
    def __init__(self):
        super().__init__()

class PositionContolWithGravityScreenRightPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.heading = Heading("Instructions for Usage")
        self.list = QListWidget()
        self.list.addItems(["1. Instruction1", "2. Instruction2", "3. Instruction3"])
        self.list.setWordWrap(True)
        self.button = QPushButton("Back")

        layout = QVBoxLayout()
        layout.addWidget(self.heading)
        layout.addWidget(self.list)
        layout.addStretch(1)
        layout.addWidget(self.button)
        self.setLayout(layout)


class PositionContolWithGravityScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.left_panel = PositionContolWithGravityScreenLeftPanel()
        self.right_panel = PositionContolWithGravityScreenRightPanel()

        layout = QHBoxLayout()
        layout.addWidget(self.left_panel)
        layout.addWidget(self.right_panel)

        self.setLayout(layout)

class PatientDetailsMessage(QMessageBox):
    def __init__(self):

        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Patient Details Error")
        self.setText("Please Fill Patient Details!")
        self.setStandardButtons(QMessageBox.Ok)


class TrajectoryMessage(QMessageBox):
    def __init__(self):

        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Trajectory Error")
        self.setText("Please Enter Required Trajectory!")
        self.setStandardButtons(QMessageBox.Ok)
        
        
class ForceMessage(QMessageBox):
    def __init__(self):

        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Force Error")
        self.setText("Please Select Required Force!")
        self.setStandardButtons(QMessageBox.Ok)


class SpeedMessage(QMessageBox):
    def __init__(self):

        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Speed Error")
        self.setText("Please Select Required Speed!")
        self.setStandardButtons(QMessageBox.Ok)


class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        self.patient_ll1 = None
        self.patient_ll2 = None
        self.patient_name = None
        self.patient_weight = None

        font = self.font()
        font.setPointSize(18)
        font.setFamily("Courier New")
        self.setFont(font)
        self.setWindowTitle("Rehab Exoskeleton App: Home")
        self.resize(500, 500)

        self.screens = QStackedWidget()

        self.initial_screen = InitialScreen()
        # self.initial_screen.middle_panel.button.clicked.connect(
        #     self.button_press_patient_data)
        self.initial_screen.right_panel.button.clicked.connect(
            self.button_press_fwd)

        self.position_control_screen = PositionContolScreen()
        self.position_control_screen.right_panel.button1.clicked.connect(
            self.button_press_continue)
        self.position_control_screen.right_panel.button2.clicked.connect(
            self.button_press_bwd)
        self.position_control_screen.left_panel.button.clicked.connect(
            self.button_press_update)

        # self.gravity_compensation_screen = GravityCompensationScreen()
        # self.gravity_compensation_screen.right_panel.button.clicked.connect(
        #     self.button_press_bwd)
        # self.gravity_compensation_screen.left_panel.button0.clicked.connect(
        #     self.gravity_compensation_start_motor)
        # self.gravity_compensation_screen.left_panel.button1.clicked.connect(
        #     self.gravity_compensation_start_therapy)
        # self.gravity_compensation_screen.left_panel.button2.clicked.connect(
        #     self.gravity_compensation_stop)
        # self.gravity_compensation_screen.left_panel.button3.clicked.connect(
        #     self.gravity_compensation_go_to_origin)
        # self.gravity_compensation_screen.left_panel.input_panel.button.clicked.connect(
        #     self.input_panel_button_pressed)

        self.position_control_final_screen = PositionControlFinalScreen()
        self.position_control_final_screen.right_panel.button.clicked.connect(
            self.button_press_bwd)
        # self.position_control_final_screen.left_panel.input_panel.button.clicked.connect(
        #     self.save_amps)
        self.position_control_final_screen.right_panel.button0.clicked.connect(
            self.position_control_start_motor)
        self.position_control_final_screen.right_panel.button1.clicked.connect(
            self.position_control_start_therapy)
        self.position_control_final_screen.right_panel.button2.clicked.connect(
            self.position_control_stop)
        self.position_control_final_screen.right_panel.button3.clicked.connect(
            self.position_control_go_to_origin)
        # self.position_control_final_screen.left_panel.input_panel.button.clicked.connect(
        #     self.input_panel_button_pressed)
        # self.position_control_final_screen.left_panel.slider.valueChanged.connect(
        #     self.function)

        # self.position_control_with_gravity_screen = PositionContolWithGravityScreen()
        # self.position_control_with_gravity_screen.right_panel.button.clicked.connect(self.button_press_bwd)

        self.motor_interact = MotorInteract()
        self.worker_thread = QThread()
        self.motor_interact.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.motor_interact.run_motor)
        # self.worker_thread.finished.connect()

        self.plot_thread = QThread()
        # self.position_control_final_screen.right_panel.graph.data_object.moveToThread(
        #     self.plot_thread)
        # self.gravity_compensation_screen.right_panel.graph.data_object.moveToThread(
        #     self.plot_thread)

        self.screens.addWidget(self.initial_screen)
        self.screens.addWidget(self.position_control_screen)
        # self.screens.addWidget(self.gravity_compensation_screen)
        self.screens.addWidget(self.position_control_final_screen)
        # self.screens.addWidget(self.position_control_with_gravity_screen)

        self.screen_mode = 0
        self.screens.setCurrentIndex(self.screen_mode)
        self.setCentralWidget(self.screens)
        self.show()

    def function(self):
        # self.motor_interact.w = OMEGAS[self.position_control_final_screen.left_panel.slider.value(
        # )]
        if self.position_control_final_screen.left_panel.button1.isChecked(): self.motor_interact.w = OMEGAS[1]
        elif self.position_control_final_screen.left_panel.button2.isChecked(): self.motor_interact.w = OMEGAS[2]
        elif self.position_control_final_screen.left_panel.button3.isChecked(): self.motor_interact.w = OMEGAS[3]
        elif self.position_control_final_screen.left_panel.button4.isChecked(): self.motor_interact.w = OMEGAS[4]
        elif self.position_control_final_screen.left_panel.button5.isChecked(): self.motor_interact.w = OMEGAS[5]
        else:
            message = SpeedMessage()
            message.exec_()
        self.motor_interact.right_delay = (2*np.pi/self.motor_interact.w)*0.75/1.39
        # self.motor_interact.right_delay = 2.8
        

    # def save_amps(self):
        # global traj_max_hip, traj_min_hip, traj_max_knee, traj_min_knee
    #     traj_max_hip = self.position_control_final_screen.left_panel.input_panel.input1
    #     traj_min_hip = self.position_control_final_screen.left_panel.input_panel.input2
    #     traj_max_knee = self.position_control_final_screen.left_panel.input_panel.input3
    #     traj_min_knee = self.position_control_final_screen.left_panel.input_panel.input4

    def button_press_continue(self):
        self.screen_mode = 2
        self.screens.setCurrentIndex(self.screen_mode)

    def button_press_update(self):

        # data1 = []
        # data2 = []

        # for i in range(0, 5):
        #     data1.append(
        #         float(self.position_control_screen.left_panel.trajectory_input.inputs1[i].text()))
        #     data2.append(
        #         float(self.position_control_screen.left_panel.trajectory_input.inputs2[i].text()))

        # data1 = np.array(data1)
        # data2 = np.array(data2)

        # self.position_control_screen.right_panel.graph.data1 = data1
        # self.position_control_screen.right_panel.graph.data2 = data2
        
        # Option for choosing trajectory inputs
        
        if self.position_control_screen.left_panel.buttona.isChecked(): 
            self.motor_interact.hip_kp = 100
            self.motor_interact.knee_kp = 70
        elif self.position_control_screen.left_panel.buttonb.isChecked(): 
            self.motor_interact.hip_kp = 120
            self.motor_interact.knee_kp = 100
        elif self.position_control_screen.left_panel.buttonc.isChecked(): 
            self.motor_interact.hip_kp = 150
            self.motor_interact.knee_kp = 120
        else:
            message = ForceMessage()
            message.exec_()
        
        if self.position_control_screen.left_panel.trajectory_input.button1.isChecked(): 
            self.position_control_screen.right_panel.graph.selection = 0
            self.motor_interact.trajectory = 0
        elif self.position_control_screen.left_panel.trajectory_input.button2.isChecked(): 
            self.position_control_screen.right_panel.graph.selection = 1
            self.motor_interact.trajectory = 0
            # self.position_control_final_screen.left_panel.input_panel.input3.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input4.setEnabled(False)
        elif self.position_control_screen.left_panel.trajectory_input.button3.isChecked(): 
            self.position_control_screen.right_panel.graph.selection = 2
            self.motor_interact.trajectory = 2
            # self.position_control_final_screen.left_panel.input_panel.input1.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input2.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input3.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input4.setEnabled(False)
        elif self.position_control_screen.left_panel.trajectory_input.button4.isChecked(): 
            self.position_control_screen.right_panel.graph.selection = 3
            self.motor_interact.trajectory = 3
            # self.position_control_final_screen.left_panel.input_panel.input1.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input2.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input3.setEnabled(False)
            # self.position_control_final_screen.left_panel.input_panel.input4.setEnabled(False)
        else:
            message1 = TrajectoryMessage()
            message1.exec_()
        
        self.position_control_screen.right_panel.graph.plot()
        self.position_control_screen.right_panel.button1.setDisabled(False)

    # def input_panel_button_pressed(self):
    #     self.motor_interact.minimum_position_hip = self.gravity_compensation_screen.left_panel.input_panel.input1.text()
    #     self.motor_interact.maximum_position_hip = self.gravity_compensation_screen.left_panel.input_panel.input2.text()
    #     self.motor_interact.minimum_position_knee = self.gravity_compensation_screen.left_panel.input_panel.input3.text()
    #     self.motor_interact.maximum_position_knee = self.gravity_compensation_screen.left_panel.input_panel.input4.text()

    def position_control_start_motor(self):
        self.motor_interact.start_motors()
        self.function()
        self.motor_interact.on = False
        self.worker_thread.start()

        self.position_control_final_screen.right_panel.button0.setDisabled(True)
        self.position_control_final_screen.right_panel.button1.setDisabled(
            False)
        self.position_control_final_screen.right_panel.button2.setDisabled(
            False)
        self.position_control_final_screen.right_panel.button3.setDisabled(
            False)

    def position_control_start_therapy(self):
        global START

        START=1
        self.motor_interact.on = True

        self.position_control_final_screen.right_panel.button0.setDisabled(True)
        self.position_control_final_screen.right_panel.button1.setDisabled(True)
        self.position_control_final_screen.right_panel.button2.setDisabled(
            False)
        self.position_control_final_screen.right_panel.button3.setDisabled(True)
        self.position_control_final_screen.right_panel.button.setDisabled(True)
        # self.position_control_final_screen.left_panel.slider.setDisabled(True)

        # self.position_control_final_screen.left_panel.input_panel.button.setDisabled(
        #     True)

    def position_control_stop(self):

        self.position_control_final_screen.right_panel.button0.setDisabled(
            False)
        self.position_control_final_screen.right_panel.button1.setDisabled(
            True)
        self.position_control_final_screen.right_panel.button2.setDisabled(True)
        self.position_control_final_screen.right_panel.button3.setDisabled(
            True)
        self.position_control_final_screen.right_panel.button.setDisabled(
            False)

        # self.position_control_final_screen.left_panel.input_panel.button.setDisabled(
        #     False)

        # self.position_control_final_screen.left_panel.slider.setDisabled(False)

        self.motor_interact.on = False
        self.motor_interact.turn_off()
        self.worker_thread.exit(0)

    def position_control_go_to_origin(self):
        self.motor_interact.go_to_origin()
        return

    # def gravity_compensation_start_motor(self):

    #     self.motor_interact.minimum_position_hip = self.gravity_compensation_screen.left_panel.input_panel.input1.text()
    #     self.motor_interact.maximum_position_hip = self.gravity_compensation_screen.left_panel.input_panel.input2.text()
    #     self.motor_interact.minimum_position_knee = self.gravity_compensation_screen.left_panel.input_panel.input3.text()
    #     self.motor_interact.minimum_position_knee = self.gravity_compensation_screen.left_panel.input_panel.input4.text()

    #     self.motor_interact.start_motors()

    #     self.motor_interact.on = False
    #     self.worker_thread.start()

    #     self.gravity_compensation_screen.left_panel.button0.setDisabled(True)
    #     self.gravity_compensation_screen.left_panel.button1.setDisabled(False)
    #     self.gravity_compensation_screen.left_panel.button2.setDisabled(False)
    #     self.gravity_compensation_screen.left_panel.button3.setDisabled(False)

    #     self.gravity_compensation_screen.right_panel.button.setDisabled(True)

    # def gravity_compensation_start_therapy(self):

    #     self.motor_interact.on = True
    #     # self.gravity_compensation_screen.right_panel.graph.plot()

    #     self.gravity_compensation_screen.left_panel.button0.setDisabled(True)
    #     self.gravity_compensation_screen.left_panel.button1.setDisabled(True)
    #     self.gravity_compensation_screen.left_panel.button2.setDisabled(False)
    #     self.gravity_compensation_screen.left_panel.button3.setDisabled(True)

    #     self.gravity_compensation_screen.left_panel.input_panel.button.setDisabled(
    #         True)

    # def gravity_compensation_stop(self):

    #     self.gravity_compensation_screen.left_panel.button0.setDisabled(False)
    #     self.gravity_compensation_screen.left_panel.button1.setDisabled(True)
    #     self.gravity_compensation_screen.left_panel.button2.setDisabled(True)
    #     self.gravity_compensation_screen.left_panel.button3.setDisabled(True)
    #     self.gravity_compensation_screen.right_panel.button.setDisabled(False)
    #     self.gravity_compensation_screen.left_panel.input_panel.button.setDisabled(
    #         False)

    #     self.motor_interact.turn_off()
    #     self.motor_interact.on = False
    #     self.worker_thread.exit(0)

    # def gravity_compensation_go_to_origin(self):

    #     self.motor_interact.go_to_origin()
    #     return

    def button_press_fwd(self):

        self.motor_interact.left_hip = self.initial_screen.left_panel.checkbox1.isChecked()
        self.motor_interact.left_knee = self.initial_screen.left_panel.checkbox2.isChecked()
        self.motor_interact.right_hip = self.initial_screen.left_panel.checkbox3.isChecked()
        self.motor_interact.right_knee = self.initial_screen.left_panel.checkbox4.isChecked()

        self.patient_name = (self.initial_screen.left_panel.line0.text())
        # self.patient_weight = float(
        #     self.initial_screen.middle_panel.line1.text())
        # self.patient_ll1 = float(self.initial_screen.middle_panel.line2.text())
        # self.patient_ll2 = float(self.initial_screen.middle_panel.line3.text())

        # self.motor_interact.left_hip_link_weight = LEFT_HIP_LINK_TORQUE + \
        #     (0.1 * self.patient_weight) * (self.patient_ll1 * 0.54) * 9.8
        # self.motor_interact.left_knee_link_weight = LEFT_HIP_LINK_TORQUE + ((0.0465 * self.patient_weight) * (
        #     self.patient_ll1 * 0.528) + (0.0145 * self.patient_weight) * (self.patient_ll1)) * 9.8
        # self.motor_interact.right_hip_link_weight = self.motor_interact.left_hip_link_weight
        # self.motor_interact.right_knee_link_weight = self.motor_interact.left_knee_link_weight

        # if self.patient_weight == None or self.patient_ll1 == None or self.patient_ll2 == None or self.patient_name == None:
        #     message = PatientDetailsMessage()
        #     message.exec_()
        if self.patient_name == "":
            message = PatientDetailsMessage()
            message.exec_()
        # else:
        #     if self.initial_screen.left_panel.button1.isChecked():
        #         self.motor_interact.mode = 1
        #         self.screen_mode = 1
        #         self.setWindowTitle("Rehab Exoskeleton App: Automatic Mode")
        #     elif self.initial_screen.left_panel.button2.isChecked():
        #         self.motor_interact.mode = 2
        #         self.screen_mode = 2
        #         self.setWindowTitle(
        #             "Rehab Exoskeleton App: Physiotherapist-guided Mode")
        #     else:
        #         message = ModeMessage()
        #         message.exec_()
        else:
            self.motor_interact.mode = 1
            self.screen_mode = 1
            self.setWindowTitle("Rehab Exoskeleton App: Automatic Mode")
        self.screens.setCurrentIndex(self.screen_mode)
        print

    def button_press_bwd(self):
        if (self.screen_mode <= 1):
            self.screen_mode = 0
        elif (self.screen_mode == 2):
            self.screen_mode = 1
        self.screens.setCurrentIndex(self.screen_mode)
        self.setWindowTitle("Rehab Exoskeleton App: Home")

    # def button_press_patient_data(self):
    #     self.patient_weight = self.initial_screen.middle_panel.line1.text()
    #     self.patient_height = self.initial_screen.middle_panel.line2.text()
    #     self.gravity_compensation_screen.left_panel.label.setText(
    #         f"Patient Weight: {self.patient_weight} kg\nPatient Height: {self.patient_height} m")

    def closeEvent(self, *args, **kwargs):
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        # self.motor_interact.turn_off()

        time.sleep(0.1)

        # obj = self.position_control_final_screen.right_panel.graph.data_object
        # objj = self.gravity_compensation_screen.right_panel.graph.data_object

        today = datetime.now()

        date_time = today.strftime("%d-%m-%y___%H-%M")
        date = today.strftime("%d-%m-%y")
        
        out = np.array(self.motor_interact.data)
        if (self.patient_name != None):
            np.savetxt(f"data_collection/{self.patient_name}-{date_time}.csv", out, delimiter=",") 
        

        # if (self.patient_name != None):
            # np.savetxt(f"{self.patient_name}_{date}.txt", np.array(
            #     [obj.times, obj.data1, obj.data2, obj.data3, obj.data4, objj.times, objj.data1, objj.data2, objj.data3, objj.data4]))
            # lis = [obj.times, obj.data1, obj.data2, obj.data3, obj.data4, objj.times, objj.data1, objj.data2, objj.data3, objj.data4]
            # print(lis)
            # np.savetxt("{self.patient_name}_{date}.csv", lis, delimiter=",")

app = QApplication(sys.argv)
window = MainWindow()
# window.setFixedWidth(1000)



# def function(data):

#     if window.motor_interact.mode == 1:
#         window.position_control_final_screen.right_panel.graph.data_object.times = np.concatenate((window.position_control_final_screen.right_panel.graph.data_object.times,
#                                                                                                 [data[0]]))
#         window.position_control_final_screen.right_panel.graph.data_object.data1 = np.concatenate((
#             window.position_control_final_screen.right_panel.graph.data_object.data1, [data[1] * 180/np.pi]))
#         window.position_control_final_screen.right_panel.graph.data_object.data2 = np.concatenate((
#             window.position_control_final_screen.right_panel.graph.data_object.data2, [data[2] * 180/np.pi]))
#         window.position_control_final_screen.right_panel.graph.data_object.data3 = np.concatenate((
#             window.position_control_final_screen.right_panel.graph.data_object.data3, [data[3] * 180/np.pi]))
#         window.position_control_final_screen.right_panel.graph.data_object.data4 = np.concatenate((
#             window.position_control_final_screen.right_panel.graph.data_object.data4, [data[4] * 180/np.pi]))

#         window.position_control_final_screen.right_panel.graph.plot()

#     elif window.motor_interact.mode == 2:

#         window.gravity_compensation_screen.right_panel.graph.data_object.times = np.concatenate((window.gravity_compensation_screen.right_panel.graph.data_object.times,
#                                                                                                 [data[0]]))
#         window.gravity_compensation_screen.right_panel.graph.data_object.data1 = np.concatenate((window.gravity_compensation_screen.right_panel.graph.data_object.data1,
#                                                                                                 [data[1] * 180/np.pi]))
#         window.gravity_compensation_screen.right_panel.graph.data_object.data2 = np.concatenate((window.gravity_compensation_screen.right_panel.graph.data_object.data2,
#                                                                                                 [data[2] * 180/np.pi]))
#         window.gravity_compensation_screen.right_panel.graph.data_object.data3 = np.concatenate((window.gravity_compensation_screen.right_panel.graph.data_object.data3,
#                                                                                                 [data[3] * 180/np.pi]))
#         window.gravity_compensation_screen.right_panel.graph.data_object.data4 = np.concatenate((window.gravity_compensation_screen.right_panel.graph.data_object.data4,
#                                                                                                 [data[4] * 180/np.pi]))

#         window.gravity_compensation_screen.right_panel.graph.plot()


sys.exit(app.exec_())
