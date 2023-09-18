
# Control Algorithms for Lower Limb Exosksleton
Contributions

* The project involves to design a controller to track a predefined gait trajectory. 

*  We are using Tmotor for actuating the joints of the exoskeleton.

*  Control algorithms tested 
        a) PID
        b) Torque based PID
        c) iLQR
        d) MPC
        d) SAC
        e) SLBO




## API 

* A Python API for controlling the AK-series Tmotor Actuator AK10-9 and AK 80-64 through the CAN bus. 

* TmotorCAN: Python framework for CAN read/write.

* Channel_config: To initialize the CAN communication with Kvaser USB to CAN.

The commands will be updated soon.
## GUI using PyQt


![](https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor/blob/main/GUI.png)


## Issuses faced and solution

* The motor sudenly jerks afetr the first CAN start command
* Zero positioning of the motor.
* Establishing a robust CAN communcation needed multiple iterations. 
* Increasing sampling time with optimizing memory access of the python code.
* SOLUTIONS WILL BE UPDATED SOON


## Deployment

To deploy this project run

*  Clone the github repo
*  Run the final_app file for GUI interface to control the motors
*  To use python motor control API use TmotorCAN

## Authors

If you use this code in your research project please cite us as:
```
@misc{pytorch_sac,
  author = {Mowbray RV, Satvik, Haricharan},
  title = {Control Algorithms for Lower Limb Exosksleton},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Mowbray-R-V/Exoskeleton_control_Tmotor/tree/main}},
}

```
