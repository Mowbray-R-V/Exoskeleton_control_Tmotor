import matplotlib.pyplot as plt
import numpy as np
import csv
import trajectory

data =[]
motor_1 = []
motor_2 = []
motor_3 = []
motor_4 = []
motor_1_2 = []
motor_2_2 = []
motor_3_2 = []
motor_4_2 = []
data = np.loadtxt("data_collection\WORKKKK-14-07-23___17-59.csv","float",delimiter=",")
data_1 = np.loadtxt("data_collection\erghreth-14-07-23___20-32.csv","float",delimiter=",")
print(data_1)
# print(data)
for line in data:
    if line[1] == 1:
        motor_1.append(line)
    elif line[1] == 2:
        motor_2.append(line)
    elif line[1] == 3:
        motor_3.append(line)
    elif line[1] == 4:
        motor_4.append(line)
for line in data_1:
    if line[1] == 1:
        motor_1_2.append(line)
    elif line[1] == 2:
        motor_2_2.append(line)
    elif line[1] == 3:
        motor_3_2.append(line)
    elif line[1] == 4:
        motor_4_2.append(line)
# print("motor begins here \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
# print(motor_1)
time=[]
position=[]
vel=[]
current=[]
time_2=[]
position_2=[]
vel_2=[]
current_2=[]
# print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
# print(motor_1)
for lin in motor_1:
    # print(lin)
    time.append(lin[0])
    position.append(lin[2])
    
    vel.append(lin[3])
    current.append(lin[4])
# print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
# print(position)
for lin in motor_2_2:
    # print(lin)
    time_2.append(lin[0])
    position_2.append(lin[2]*(180/np.pi))
    
    vel_2.append(lin[3])
    current_2.append(lin[4])
req_pos = []
for t in time:
    req_pos.append(-trajectory.theta_5(0.96615, t + 3.507,0,1)*(180/np.pi)+5)
plt.plot(np.array(time),np.array(current))
plt.plot(time_2,current_2)
# plt.plot(np.array(time),req_pos,'r')
plt.show()



