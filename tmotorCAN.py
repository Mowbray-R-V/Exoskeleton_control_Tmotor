import time
import canlib
import canlib.canlib as clb
import channel_config_copy
from typing import Tuple, List


class tmotor():

    channel = channel_config_copy.start_channel(0)

    motors_dict = {}

    def __init__(self, id: int, type: str, K_p: float = 10, K_d: float = 1, minpos=None, maxpos=None):
        """Function which initializes a motor

        Args:
            id (int): CAN id of motor
            type (str): Type of tmotor. Has to be one of the strings "AK10-9", "AK60-6", "AK70-10", "AK80-6", "AK80-9", "AK80-64"            
            K_p (int, optional): Default K_p value. Is overridden using the attain function. Defaults to 10.
            K_d (int, optional): Default K_d value. Is overridden using the attain function. Defaults to 1.
        """

        self.id = id

        self.K_p = K_p
        self.K_d = K_d

        self.type = type

        self.KP_MIN = 0.0
        self.KP_MAX = 500.0
        self.KD_MIN = 0.0
        self.KD_MAX = 5.0

        self.minpos = minpos
        self.maxpos = maxpos

        self.P_MIN, self.P_MAX, self.V_MIN, self.V_MAX, self.T_MIN, self.T_MAX = self.return_params(
            type)

        self.motors_dict[self.id] = self.type

    @classmethod
    def return_params(cls, type):

        P_MIN = -12.5
        P_MAX = 12.5

        if (type == "AK10-9"):
            V_MIN = -50.0
            V_MAX = +50.0
            T_MIN = -65.0
            T_MAX = 65.0
        elif (type == "AK60-6"):
            V_MIN = -45.0
            V_MAX = +45.0
            T_MIN = -15.0
            T_MAX = 15.0
        elif (type == "AK70-10"):
            V_MIN = -50.0
            V_MAX = +50.0
            T_MIN = -25.0
            T_MAX = 25.0
        elif (type == "AK80-6"):
            V_MIN = -76.0
            V_MAX = +76.0
            T_MIN = -12.0
            T_MAX = 12.0
        elif (type == "AK80-9"):
            V_MIN = -50.0
            V_MAX = +50.0
            T_MIN = -18.0
            T_MAX = 18.0
        elif (type == "AK80-64"):
            V_MIN = -8.0
            V_MAX = 8.0
            T_MIN = -144.0
            T_MAX = 144.0
        else:
            raise ValueError

        return P_MIN, P_MAX, V_MIN, V_MAX, T_MIN, T_MAX

    def start_motor(self):
        """Function which turns on MIT mode"""
        # self.go_to_origin()
        frame = canlib.Frame(
            id_=self.id, data=self.enter_motor_mode(), flags=clb.MessageFlag.STD)
        self.channel.write(frame)
        # self.attain(0,0,0,0,0)
        self.go_to_origin()
        time.sleep(0.0001)

    def stop_motor(self):
        """Function which turns off MIT mode"""
        # self.go_to_origin()
        # print()
        self.attain(0,0,0,0,0)
        frame = canlib.Frame(
            id_=self.id, data=self.exit_motor_mode(), flags=clb.MessageFlag.STD)
        self.channel.write(frame)
        time.sleep(0.0001)

    def go_to_origin(self):
        """Function which makes the motor go to origin"""

        self.attain(0, 0, 0, self.K_p, self.K_d)
        # frame = canlib.Frame(
        #     id_=self.id, data=self.zero_position(), flags=clb.MessageFlag.STD)
        # self.channel.write(frame)
        # time.sleep(1.5)
        time.sleep(0.1)

    def attain(self, p_in: float, v_in: float, t_in: float, K_p: float = None, K_d: float = None):
        """Function which makes the motor setpoint to be the given values, and supplies torque, according to the equation
        torque = t_in + K_p * (p_in - p_out) + K_d * (v_in - v_out)

        Args:
            p_in (float): Desired Position
            v_in (float): Desired Velocity
            t_in (float): Desired Input Torque
            K_p (float, optional): Desired K_p value
            K_d (float, optional): Desired K_d value

        """

        time.sleep(0.001)
        if (K_p == None):
            K_p = self.K_p
        if (K_d == None):
            K_d = self.K_d

        if (self.minpos != None and p_in < self.minpos):
            frame = canlib.Frame(id_=self.id, data=self.pack_cmd(
                self.minpos, 0, t_in, 70, 5), flags=clb.MessageFlag.STD)
        elif (self.maxpos != None and p_in > self.maxpos):
            frame = canlib.Frame(id_=self.id, data=self.pack_cmd(
                self.maxpos, 0, t_in, 70, 5), flags=clb.MessageFlag.STD)
        else:
            frame = canlib.Frame(id_=self.id, data=self.pack_cmd(
                p_in, v_in, t_in, K_p, K_d), flags=clb.MessageFlag.STD)

        self.channel.write(frame)

    def constrain(self, value: float, min_value: float, max_value: float) -> float:
        """Function which constrains the value between min_value and max_value

        Args:

            value (float): Given Value
            min_value (float): Minimum value
            max_value (float): Maximum value

        Returns:
            value (float): Value after constraining

        """

        if (value < min_value):
            return min_value
        if (value > max_value):
            return max_value
        return value

    def float_to_uint(self, x: float, x_min: float, x_max: float, bits: int) -> int:
        """Function to convert float x into its unsigned integer equivalent

        Args:
            x (float): Given input x value
            x_min (float): Minimum x value
            x_max (float): Maximum x value
            bits (int): Number of bits

        Returns:
            int: Unsigned Integer representation of Given x
        """

        span = x_max - x_min
        offset = x_min
        pgg = 0
        if (bits == 12):
            pgg = (x - offset) * 4095.0 / span
        elif (bits == 16):
            pgg = (x - offset) * 65535.0 / span

        return int(pgg)

    @classmethod
    def uint_to_float(cls, x_int: int, x_min: float, x_max: float, bits: int) -> float:
        """Function to convert unsigned integer x_int into its float x equivalent

        Args:
            x_int (int): Given input x value
            x_min (float): Minimum x value
            x_max (float): Maximum x value
            bits (int): Number of bits

        Returns:
            float: Float representation of Given x

        """

        span = x_max - x_min
        offset = x_min
        pgg = 0
        if (bits == 12):
            pgg = x_int * span / 4095.0 + offset
        elif (bits == 16):
            pgg = x_int * span / 65535.0 + offset
        return pgg

    def enter_motor_mode(self) -> List:
        """Function which creates array to turn the motor ON in MIT motor mode

        Returns:
            buf: Returns array required to implement MIT motor mode
        """

        buf = [0 for i in range(8)]
        buf[0] = 0xFF
        buf[1] = 0xFF
        buf[2] = 0xFF
        buf[3] = 0xFF
        buf[4] = 0xFF
        buf[5] = 0xFF
        buf[6] = 0xFF
        buf[7] = 0xFC

        return buf
    
    def zero_position(self):
        
        buf = [0 for i in range(8)]
        buf[0] = 0xFF
        buf[1] = 0xFF
        buf[2] = 0xFF
        buf[3] = 0xFF
        buf[4] = 0xFF
        buf[5] = 0xFF
        buf[6] = 0xFF
        buf[7] = 0xFE

        return buf

    def exit_motor_mode(self):
        """Function which creates array to turn the motor OFF in MIT motor mode

        Returns:
            buf: Returns array required to implement MIT motor mode
        """
        buf = [0 for i in range(8)]

        buf[0] = 0xFF
        buf[1] = 0xFF
        buf[2] = 0xFF
        buf[3] = 0xFF
        buf[4] = 0xFF
        buf[5] = 0xFF
        buf[6] = 0xFF
        buf[7] = 0xFD

        return buf

    def pack_cmd(self, p_in: float, v_in: float, t_in: float, kp_in: float, kd_in: float) -> List:
        """Function which creates required buffer array given p_in, v_in, t_in, k_p, k_d

        Args:
            p_in (float): Desired Position
            v_in (float): Desired Velocity
            t_in (float): Desired Input Torque
            kp_in (float): K_p value
            kd_in (float): K_d value

        Returns:
            List: Buffer array of floats converted to integer versions
        """

        p_des = self.constrain(p_in, self.P_MIN, self.P_MAX)
        v_des = self.constrain(v_in, self.V_MIN, self.V_MAX)
        kp = self.constrain(kp_in, self.KP_MIN, self.KP_MAX)
        kd = self.constrain(kd_in, self.KD_MIN, self.KD_MAX)
        t_ff = self.constrain(t_in, self.T_MIN, self.T_MAX)

        p_int = self.float_to_uint(p_des, self.P_MIN, self.P_MAX, 16)
        v_int = self.float_to_uint(v_des, self.V_MIN, self.V_MAX, 12)
        kp_int = self.float_to_uint(kp, self.KP_MIN, self.KP_MAX, 12)
        kd_int = self.float_to_uint(kd, self.KD_MIN, self.KD_MAX, 12)
        t_int = self.float_to_uint(t_ff, self.T_MIN, self.T_MAX, 12)

        buf = [0 for i in range(8)]

        buf[0] = p_int >> 8
        buf[1] = p_int & 0xFF
        buf[2] = v_int >> 4
        buf[3] = ((v_int & 0xF) << 4) | (kp_int >> 8)
        buf[4] = kp_int & 0xFF
        buf[5] = kd_int >> 4
        buf[6] = ((kd_int & 0xF) << 4) | (t_int >> 8)
        buf[7] = t_int & 0xFF

        return buf

    @classmethod
    def unpack_reply(cls, buf: List) -> Tuple[int, float, float, float]:
        """Function which converts given buffer data array into float format

        Args:
            buf (List): List obtained from motor

        Returns:
            Tuple[int, float, float, float]: Float values of Motor Position, Motor Velocity, and Motor Torque
        """

        id = buf[0]
        type = cls.motors_dict[id]

        P_MIN, P_MAX, V_MIN, V_MAX, T_MIN, T_MAX = cls.return_params(type)

        p_int = (buf[1] << 8) | buf[2]
        v_int = (buf[3] << 4) | (buf[4] >> 4)
        i_int = ((buf[4] & 0xF) << 8) | buf[5]

        p_out = cls.uint_to_float(p_int, P_MIN, P_MAX, 16)
        v_out = cls.uint_to_float(v_int, V_MIN, V_MAX, 12)
        t_out = cls.uint_to_float(i_int, T_MIN, T_MAX, 12)

        return id, p_out, v_out, t_out

    @classmethod
    def read_can(cls):
        try:
            time.sleep(0.001)
            output_msg = []
            while len(output_msg) != 8:
                output_msg = cls.channel.read().data
            id, p_out, v_out, t_out = cls.unpack_reply(output_msg)
            return id, p_out, v_out, t_out
        except IndexError:
            return None, None, None, None

    def set_minmax(self, minpos, maxpos):
        self.minpos = minpos
        self.maxpos = maxpos
