import tmotorCAN
import numpy as np
import trajectory
import time
motor = tmotorCAN.tmotor(1, "AK10-9")
motor_2 = tmotorCAN.tmotor(2, "AK10-9")
motor_3 = tmotorCAN.tmotor(3, "AK10-9")
motor_4 = tmotorCAN.tmotor(4, "AK10-9")

motor.start_motor()
motor.go_to_origin()
motor_2.start_motor()
motor_2.go_to_origin()
motor_3.start_motor()
motor_3.go_to_origin()
motor_4.start_motor()
motor_4.go_to_origin()

time.sleep(1)
start_time = time.time()
lis=[]
om=np.pi/2
t = 2*np.pi/om
right_delay = (2*np.pi/om)*0.75/1.39
try:
    i=0
    ## sin wave
    # while True:
    #     i+=0.1
    #     t = time.time() - start_time
    #     desired_pos = np.sin(om*i)/3
    #     desired_vel = om* np.cos(om*i)/3
    #     motor.attain(desired_pos,desired_vel,0,10,2)

    #     time.sleep(0.1)

    ##set point
    # motor.attain(-np.pi/3,0,0,10,2)
    # time.sleep(2)
    # motor.go_to_origin()
    # motor.stop_motor()



    ##trajectory

    while True:

        t = time.time() - start_time
        motor.attain(-trajectory.theta_5(om,t+right_delay,0,1),-trajectory.omega_5(om,t,0,1),0,20,2)
        motor_2.attain(-trajectory.theta_6_rel(om,t+right_delay,0,1),-trajectory.omega_6_rel(om,t,0,1),0,20,2)
        motor_3.attain(trajectory.theta_5(om,t,0,1),trajectory.omega_5(om,t,0,1),0,10,2)
        motor_4.attain(trajectory.theta_6_rel(om,t,0,1),trajectory.omega_6_rel(om,t,0,1),0,10,2)
        print(t)
        time.sleep(0.1)

except:

    motor.go_to_origin()
    motor.stop_motor()
    motor_2.go_to_origin()
    motor_2.stop_motor()
    motor_3.go_to_origin()
    motor_3.stop_motor()
    motor_4.go_to_origin()
    motor_4.stop_motor()