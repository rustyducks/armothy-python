from smbus2 import SMBus
from enum import Enum
import bitstring

# Commands
START_CALIBRATION_CMD = 0x00
DIRECT_AXIS_1_CMD = 0x01  # Expects a 4 bytes float with this command
DIRECT_AXIS_2_CMD = 0x02  # Expects a 4 bytes float with this command
DIRECT_AXIS_3_CMD = 0x03  # Expects a 4 bytes float with this command
STOP_PUMP_CMD = 0x04
START_PUMP_CMD = 0x05
CLOSE_VALVE_CMD = 0x06
OPEN_VALVE_CMD = 0x07
EMERGENCY_STOP_CMD = 0x08

# Request commands(answer length specified in comment)
CALIBRATION_ENDED_RQST = 0x09  # 1 byte(0: ended; 1: running)
AXIS_1_POSITION_RQST = 0x0A  # 4 bytes(float)
AXIS_2_POSITION_RQST = 0x0B  # 4 bytes(float)
AXIS_3_POSITION_RQST = 0x0C  # 4 bytes(float)
PUMP_STATE_RQST = 0x0D  # 1 byte(0: stopped; 1: started)
VALVE_STATE_RQST = 0x0E  # 1 byte(0: closed; 1: opened)
PRESSURE_RQST = 0x0F  # 4 bytes(float)


class Communication:

    def __init__(self, armothy_address):
        self.i2c = SMBus(0)
        self.armothy_address = armothy_address

    def start_calibration(self):
        self.i2c.write_byte(self.armothy_address, START_CALIBRATION_CMD)

    def send_axis_command(self, axis, value):
        stream_value = bitstring.pack('float:32', value)
        if axis == 0:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_1_CMD, stream_value.bytes)
        elif axis == 1:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_2_CMD, stream_value.bytes)
        elif axis == 2:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_3_CMD, stream_value.bytes)

    def stop_pump(self):
        self.i2c.write_byte(self.armothy_address, STOP_PUMP_CMD)

    def start_pump(self):
        self.i2c.write_byte(self.armothy_address, START_PUMP_CMD)

    def close_valve(self):
        self.i2c.write_byte(self.armothy_address, CLOSE_VALVE_CMD)

    def open_valve(self):
        self.i2c.write_byte(self.armothy_address, OPEN_VALVE_CMD)

    def emergency_stop(self):
        self.i2c.write_byte(self.armothy_address, EMERGENCY_STOP_CMD)

    def is_calibration_running(self):
        block = self.i2c.read_i2c_block_data(self.armothy_address, CALIBRATION_ENDED_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def get_axis_value(self, axis):
        block = []
        if axis == 0:
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_1_POSITION_RQST, 4)
        elif axis == 1:
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_2_POSITION_RQST, 4)
        elif axis == 2:
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_3_POSITION_RQST, 4)
        value = bitstring.pack('4*uint:8', *block)
        return value.float  # Maybe replace with floatle (depends on the Teensy)

    def is_pump_on(self):
        block = self.i2c.read_i2c_block_data(self.armothy_address, PUMP_STATE_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def is_valve_open(self):
        block = self.i2c.read_i2c_block_data(self.armothy_address, VALVE_STATE_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def get_pressure_value(self):
        block = self.i2c.read_i2c_block_data(self.armothy_address, PRESSURE_RQST, 4)
        value = bitstring.pack('4*uint:8', *block)
        return value.float
