
# Control algorithms for lower limb exosksleton

1. The project involves to design a controller to track a predefined gait trajectory. 

2. We are using Tmotor for actuating the joinst of the exoskeleton.

3. Control algorithms tested 
        a) PID
        b) Torque based PID
        c) iLQR
        d) MPC



A GUI for  The project is geared towards the control of the AK80-9 actuator using a raspberry pi CAN hat or serial bus, but could eaisly be adapted for use with a different CAN/serial interface. The API files are in the src/TMotorCANControl folder in this repository. The main interface is in the file TMotorManager_mit_can.py for MIT mode, TMotorManager_servo_can.py for Servo mode (over CAN), and TMotorManager_servo_serial for Servo mode (over serial). Sample scripts can be found in the demos folder.






1. The project involves to design a controller to track a predefined gait trajectory. 

2. We are using Tmotor for actuating the joinst of the exoskeleton.

3. Control algorithms tested 
        a) PID
        b) Torque based PID
        c) iLQR
        d) MPC
        d) SAC
        e) SLBO


4. We have developed a 

## API 

* A Python API for controlling the AK-series Tmotor Actuator AK10-9 and AK 80-64 through the CAN bus. 

* TmotorCAN: Python framework for CAN read/write.

* Channel_config: To initialize the CAN communication with Kvaser USB to CAN.


## GUI using PyQt


![bvnh](https://drive.google.com/drive/my-drive)

## Issuses faced and solution

Any additional information goes here


## Authors

- [@octokatherine](https://www.github.com/octokatherine)

