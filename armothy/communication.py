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
MACRO_CMD = 0x08          # Expects 1 byte integer with this command
EMERGENCY_STOP_CMD = 0x09

# Request commands(answer length specified in comment)
CALIBRATION_ENDED_RQST = 0x0A  # 1 byte(0: ended; 1: running)
AXIS_1_POSITION_RQST = 0x0B  # 4 bytes(float)
AXIS_2_POSITION_RQST = 0x0C  # 4 bytes(float)
AXIS_3_POSITION_RQST = 0x0D  # 4 bytes(float)
PUMP_STATE_RQST = 0x0E  # 1 byte(0: stopped; 1: started)
VALVE_STATE_RQST = 0x0F  # 1 byte(0: closed; 1: opened)
ERROR_BYTE_RQST = 0x10  # 1byte ?????
MACRO_STATUS_RQST = 0x11   # 1 byte
PRESSURE_RQST = 0x12  # 4 bytes(float)


class Communication:

    def __init__(self, armothy_address):
        self.i2c = SMBus(1)
        self.armothy_address = armothy_address

    def start_calibration(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, START_CALIBRATION_CMD, stream_value.bytes)

    def send_axis_command(self, axis, value):
        stream_value = bitstring.pack('uint:8, floatle:32', 1, value)
        if axis == 0:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_1_CMD, stream_value.bytes)
        elif axis == 1:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_2_CMD, stream_value.bytes)
        elif axis == 2:
            self.i2c.write_i2c_block_data(self.armothy_address, DIRECT_AXIS_3_CMD, stream_value.bytes)

    def stop_pump(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, STOP_PUMP_CMD, stream_value.bytes)

    def start_pump(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, START_PUMP_CMD, stream_value.bytes)

    def close_valve(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, CLOSE_VALVE_CMD, stream_value.bytes)

    def open_valve(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, OPEN_VALVE_CMD, stream_value.bytes)
    
    def send_macro_command(self, macroNb, args):
        """
        expect as args a list of tuples with the type, then the value of the argument.
        ex : args = [('float', 14.2), ('int', -45), ('uint', 72)]
        """
        bitstring_format = 'uint:8, uintle:32'
        if len(args)>0:
             bitstring_format += ", " + ", ".join(t+"le:32" for t,value in args)
        values = [value for t, value in args]
        stream_value = bitstring.pack(bitstring_format, len(args)+1,  macroNb, *values)
        self.i2c.write_i2c_block_data(self.armothy_address, MACRO_CMD, stream_value.bytes)

    def emergency_stop(self):
        stream_value = bitstring.pack('uint:8', 0)
        self.i2c.write_i2c_block_data(self.armothy_address, EMERGENCY_STOP_CMD, stream_value.bytes)

    def is_calibration_running(self):
        self.i2c.write_byte(self.armothy_address, CALIBRATION_ENDED_RQST)
        block = self.i2c.read_i2c_block_data(self.armothy_address, CALIBRATION_ENDED_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def get_axis_value(self, axis):
        block = []
        if axis == 0:
            self.i2c.write_byte(self.armothy_address, AXIS_1_POSITION_RQST)
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_1_POSITION_RQST, 4)
        elif axis == 1:
            self.i2c.write_byte(self.armothy_address, AXIS_2_POSITION_RQST)
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_2_POSITION_RQST, 4)
        elif axis == 2:
            self.i2c.write_byte(self.armothy_address, AXIS_3_POSITION_RQST)
            block = self.i2c.read_i2c_block_data(self.armothy_address, AXIS_3_POSITION_RQST, 4)
        value = bitstring.pack('4*uint:8', *block)
        return value.floatle

    def is_pump_off(self):
        self.i2c.write_byte(self.armothy_address, PUMP_STATE_RQST)
        block = self.i2c.read_i2c_block_data(self.armothy_address, PUMP_STATE_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def is_valve_closed(self):
        self.i2c.write_byte(self.armothy_address, VALVE_STATE_RQST)
        block = self.i2c.read_i2c_block_data(self.armothy_address, VALVE_STATE_RQST, 1)
        value = bitstring.pack('uint:8', *block)
        return value.int

    def get_pressure_value(self):
        self.i2c.write_byte(self.armothy_address, PRESSURE_RQST)  # Needed because we need to specify twice the command
        block = self.i2c.read_i2c_block_data(self.armothy_address, PRESSURE_RQST, 4)
        value = bitstring.pack('4*uint:8', *block)
        return value.floatle
    
    def get_macro_status(self):
        try:
            self.i2c.write_byte(self.armothy_address, MACRO_STATUS_RQST)
            block = self.i2c.read_i2c_block_data(self.armothy_address, MACRO_STATUS_RQST, 1)
            value = bitstring.pack('uint:8', *block)
            return value.int
        except OSError:
            print("I2C Error !!!!!!")
            return 5    #I2C_ERROR
    
    def get_error_byte(self):
        self.i2c.write_byte(self.armothy_address, ERROR_BYTE_RQST)
        block = self.i2c.read_i2c_block_data(self.armothy_address, ERROR_BYTE_RQST, 1)
        value = bitstring.pack('uint:8',* block)
        return value.int
