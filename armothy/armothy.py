from enum import Enum
from .communication import Communication


class ePumpState(Enum):
    ON = 0
    OFF = 1


class eValveState(Enum):
    OPENED = 0
    CLOSED = 1


class eDoF(Enum):
    PRISMATIC_Z_AXIS = 0
    REVOLUTE_Z_AXIS = 1
    REVOLUTE_Y_AXIS = 2

class eMacros(Enum):
    CATCH = 0
    TAKE_AND_STORE = 1
    HOME = 2
    PUT_DOWN = 3

class eMacroStatus(Enum):
    FINISHED = 1
    RUNNING = 2
    ERROR = 4
    RUNNING_SAFE = 8
    I2C_ERROR = 16

class eStack(Enum):
    LEFT_STACK = 0
    RIGHT_STACK = 1

class Armothy:
    def __init__(self, armothy_i2c_address=0x74):
        self._pump_state = None
        self._valve_state = None
        self._axis_values = [0.0, 0.0, 0.0]
        self._pressure = 0.0
        self._is_moving = False
        self.communication = Communication(armothy_i2c_address)
        #self.rotate_y_axis(0)
        #self.rotate_z_axis(315)
        self.home()


    def home(self):
        self.execute_macro(eMacros.HOME)

    @property
    def pump_state(self):
        self._pump_state = ePumpState(self.communication.is_pump_off())
        return self._pump_state

    @property
    def valve_state(self):
        self._valve_state = eValveState(self.communication.is_valve_closed())
        return self._valve_state

    @property
    def prismatic_z_axis(self):
        return self.get_dof(eDoF.PRISMATIC_Z_AXIS.value)

    @property
    def revolute_z_axis(self):
        return self.get_dof(eDoF.REVOLUTE_Z_AXIS.value)

    @property
    def revolute_y_axis(self):
        return self.get_dof(eDoF.REVOLUTE_Y_AXIS.value)

    @property
    def is_moving(self):
        self._is_moving = bool(self.communication.is_calibration_running())
        return self._is_moving

    @property
    def pressure(self):
        self._pressure = self.communication.get_pressure_value()
        return self._pressure

    def get_dof(self, dof):
        self._axis_values[dof] = self.communication.get_axis_value(dof)
        return self._axis_values[dof]

    def __getitem__(self, item):
        if isinstance(item, eDoF):
            return self.get_dof(item.value)
        elif isinstance(item, int):
            return self.get_dof(item)

    def translate_z_axis(self, goal):
        self.communication.send_axis_command(0, goal)

    def rotate_z_axis(self, goal):
        self.communication.send_axis_command(1, goal)

    def rotate_y_axis(self, goal):
        self.communication.send_axis_command(2, goal)

    def set_dof(self, axis, goals):
        for i, ax in enumerate(axis):
            self.communication.send_axis_command(ax, goals[i])

    def close_valve(self):
        self.communication.close_valve()

    def open_valve(self):
        self.communication.open_valve()

    def stop_pump(self):
        self.communication.stop_pump()

    def start_pump(self):
        self.communication.start_pump()
    
    def take_and_store(self, height, stack):
        self.execute_macro(eMacros.TAKE_AND_STORE, [('float', height), ('uint', stack.value)])
    
    def put_down(self, height, stack, angle, drop_height=300):
        self.execute_macro(eMacros.PUT_DOWN, [('float', height), ('uint', stack.value), ('int', angle), ('float', drop_height)])
    
    def execute_macro(self, macro, args=[]):
        self.communication.send_macro_command(macro.value, args)
    
    def get_macro_status(self):
        return eMacroStatus(self.communication.get_macro_status())
    
    def get_error_byte(self):
        return self.communication.get_error_byte()

    def update(self):
        self._pump_state = ePumpState(self.communication.is_pump_on())
        self._valve_state = eValveState(self.communication.is_valve_open())
        for dof in range(3):
            self._axis_values[dof] = self.communication.get_axis_value(dof)
        self._is_moving = bool(self.communication.is_calibration_running())
        self._pressure = self.communication.get_pressure_value()

