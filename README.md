# Control Algorithms for Lower Limb Exosksleton
Contributions

* The project involves to design a controller to track a predefined gait trajectory. 

*  We are using Tmotor for actuating the joints of the exoskeleton.

*  Control algorithms tested on:
  
        a) PID
        b) Torque based PD
        c) iLQR
        d) MPC
  
        


## Tmotor CAN bus read/write 

* A Python module for controlling the AK-series Tmotor Actuator AK10-9 and AK 80-64 through the CAN bus. 

* TmotorCAN: Python framework for CAN read/write.

* Channel_config: To initialize the CAN communication with Kvaser USB to CAN.

The commands will be updated soon.

## GUI using PyQt

![](https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor/blob/main/GUI.png)


## Arduino/Jetson Nano
*  Code for control using these two boards will be updated soon


## Issuses addressed in the Tmotor firmware

* The motor sudenly jerks after the first CAN start command, a inherent problem in the Tmotor firmware.
* Zero positioning of the motor fails at random instants, build a safety filter to address it.

* Establishing a robust CAN communcation with the motors. 




## Deployment

1. clone the repository
   
 ``` 
 https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor.git
 ```
2. For GUI based control

 ```
  python3 final_app.py 
 ```
3. To control your Tmotor using python use the below as module

 ```
  tmotorCAN.py
 ```
## GUI Instructions
refer

## Phase 1

## Phase 2

## Phase 3



## Authors

If you use this code in your project please cite us as:
```
@misc{Exoskeleton_control_Tmotors,
  author = {Mowbray RV, Satvik, Haricharan},
  title = {Control Algorithms for Lower Limb Exosksleton},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor/tree/main}},
}

```
