from happi.client import from_container
import logging, time
import numpy as np
from src.layout.controls import create_control_gui, create_sensor_gui


class OphydDash:
    _highLimit = 1
    _lowLimit = -1

    def __init__(self, ophyd_item):
        # self.name = ophyd_item.name
        self.name = ophyd_item.extraneous["functional_group"]
        self.type = ophyd_item.device_class
        self.prefix = ophyd_item.prefix
        self.id = ophyd_item.extraneous["functional_group"]
        self.ophyd_item = ophyd_item
        self.status = "Offline"

        self.ophyd_obj = None
        self.gui_comp = None
        self.precision = 5

        self.connect()
        self.update_status()
        self.set_settle_time()
        self.assignGUI()

    def connect(self):
        try:
            self.ophyd_obj = from_container(self.ophyd_item, attach_md=True)
            # self.ophyObj.wait_for_connection(timeout=0.2)
            time.sleep(0.2)
            # self.update_status
        except Exception as e:
            logging.error(f"Could not connect component {self.name} due to: {e}")

    def set_settle_time(self, settleTime=0.05):
        """
        Set motor settling time 

        Parameters
        ----------
        settleTime : float, optional
            Settling time of motor, default value is 0.05 second
        """
        if self.ophyd_obj is not None:
            if self.ophyd_obj.connected:
                try:
                    self.ophyd_obj.settle_time = settleTime
                except Exception as e:
                    logging.error(
                        f"Could not connect component {self.name} due to: {e}"
                    )
            else:
                print(f"{self.name} is not connected")

    def update_status(self):
        """
        Update motor status

        """
        self.status = "Online" if self.ophyd_obj.connected else "Offline"
        if self.type == "ophyd.EpicsMotor":
            self._update_motor()
        elif self.type == "ophyd.EpicsSignal":
            self._update_signal()

    def _update_motor(self):
        if self.ophyd_obj is not None:
            self.unit = self.ophyd_obj.egu if self.ophyd_obj.connected else "None"
            self.min = (
                self.ophyd_obj.get_lim(self._lowLimit)
                if self.ophyd_obj.connected
                else 0
            )
            self.max = (
                self.ophyd_obj.get_lim(self._highLimit)
                if self.ophyd_obj.connected
                else 0
            )
            self.position = (
                self.ophyd_obj.position if self.ophyd_obj.connected else np.nan
            )

    def _update_signal(self):
        if self.ophyd_obj is not None:
            metadata = self.ophyd_obj.metadata
            self.unit = metadata["units"] if self.ophyd_obj.connected else "None"
            self.min = metadata["lower_ctrl_limit"] if self.ophyd_obj.connected else 0
            self.max = metadata["upper_ctrl_limit"] if self.ophyd_obj.connected else 0
            try:
                metadata = self.ophyd_obj.read()
                self.position = metadata[self.ophyd_item.name]["value"]
            except Exception as e:
                self.position = np.nan
                logging.error(f"Could not read component {self.name} due to: {e}")

    def assignGUI(self):
        if self.type == "ophyd.EpicsMotor":
            create_control_gui(self)
        elif self.type == "ophyd.EpicsSignal":
            create_sensor_gui(self)

    def read(self):
        """
        Getting current position 
        """
        if self.ophyd_obj.connected:
            try:
                self.update_status()
                return self.position
            except Exception as e:
                logging.error(f"Could not read component {self.name} due to: {e}")
        else:
            logging.error(
                f"Could not read component {self.name} because it is not connected"
            )

    def move(self, target_position):
        """
        Move motor to a desire position

        Parameters
        ----------
        target_position : float, required
            Target motor position
        """
        if all(
            [
                self.ophyd_obj.connected,
                target_position > self.min,
                target_position < self.max,
            ]
        ):
            try:
                self.ophyd_obj.move(target_position)
            except Exception as e:
                logging.error(f"Could not move component {self.name} due to: {e}")
        else:
            logging.error(
                f"Could not move component {self.name}. Check if component is connected or the requested position is within range"
            )

