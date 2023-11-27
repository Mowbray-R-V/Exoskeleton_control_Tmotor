
# Control Algorithms for Lower Limb Exosksleton
Contributions

* The project involves to design a controller to track a predefined gait trajectory. 

*  We are using Tmotor for actuating the joints of the exoskeleton.

*  Control algorithms tested 
        * PID
        b) Torque based PD
        c) iLQR
        d) MPC
        d) SAC
        


## Tmotor CAN read/write 

* A Python module for controlling the AK-series Tmotor Actuator AK10-9 and AK 80-64 through the CAN bus. 

* TmotorCAN: Python framework for CAN read/write.

* Channel_config: To initialize the CAN communication with Kvaser USB to CAN.

The commands will be updated soon.
## GUI using PyQt


![](https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor/blob/main/GUI.png)
* A working video will be updated soon

## Arduino/Jetson Nano
*  Code for control using these two boards will be updated soon


## Issuses addressed using the Tmotor

* The motor sudenly jerks after the first CAN start command, a inherent problem in the Tmotor firmware.
* Zero positioning of the motor fails at random instants.
* Establishing a robust CAN communcation with the motors. 
* Increasing sampling time with optimizing memory access of the python code.



## Deployment

To deploy this project run

*  Clone the github repo
*  Run the final_app file for GUI interface to control the motors
*  To use python motor control API use TmotorCAN

 ## Working Video
 * https://drive.google.com/file/d/1Qqa_X8OW9ycl6pjRpOjA-hDKQnT3ETVF/view?usp=sharing
 * https://drive.google.com/file/d/1yswbQRFnBGRXAdPrOnonQIoeQ4WLLH7M/view?usp=sharing

## Authors

If you use this code in your research project please cite us as:
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
