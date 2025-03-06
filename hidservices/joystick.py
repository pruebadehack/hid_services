from bluetooth import UUID
from lib.hid_services import HumanInterfaceDevice
from lib.hidservices.advertiser import Advertiser
from lib.hidservices.constants

# Class that represents the Joystick service.
class Joystick(HumanInterfaceDevice):
    def __init__(self, name="Bluetooth Joystick"):
        super(Joystick, self).__init__(name)                                                                            # Set up the general HID services in super.
        self.device_appearance = 963                                                                                    # Overwrite the device appearance ID, 963 = joystick.

        self.HIDS = (                                                                                                   # HID service description: describes the service and how we communicate.
            UUID(0x1812),                                                                                               # 0x1812 = Human Interface Device.
            (
                (UUID(0x2A4A), F_READ),                                                                                 # 0x2A4A = HID information characteristic, to be read by client.
                (UUID(0x2A4B), F_READ),                                                                                 # 0x2A4B = HID USB report map, to be read by client.
                (UUID(0x2A4C), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4C = HID control point, to be written by client.
                (UUID(0x2A4D), F_READ_NOTIFY, (                                                                         # 0x2A4D = HID report, to be read by client after notification.
                    (UUID(0x2908), DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4E), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4E = HID protocol mode, to be written & read by client.
            ),
        )

        # fmt: off
        self.HID_INPUT_REPORT = [                                                                                       # USB Report Description: describes what we communicate.
            0x05, 0x01,                                                                                                 # USAGE_PAGE (Generic Desktop)
            0x09, 0x04,                                                                                                 # USAGE (Joystick)
            0xa1, 0x01,                                                                                                 # COLLECTION (Application)
            0x85, 0x01,                                                                                                 #   REPORT_ID (1)
            0xa1, 0x00,                                                                                                 #   COLLECTION (Physical)
            0x09, 0x30,                                                                                                 #     USAGE (X)
            0x09, 0x31,                                                                                                 #     USAGE (Y)
            0x15, 0x81,                                                                                                 #     LOGICAL_MINIMUM (-127)
            0x25, 0x7f,                                                                                                 #     LOGICAL_MAXIMUM (127)
            0x75, 0x08,                                                                                                 #     REPORT_SIZE (8)
            0x95, 0x02,                                                                                                 #     REPORT_COUNT (2)
            0x81, 0x02,                                                                                                 #     INPUT (Data,Var,Abs)
            0x05, 0x09,                                                                                                 #     USAGE_PAGE (Button)
            0x29, 0x08,                                                                                                 #     USAGE_MAXIMUM (Button 8)
            0x19, 0x01,                                                                                                 #     USAGE_MINIMUM (Button 1)
            0x95, 0x08,                                                                                                 #     REPORT_COUNT (8)
            0x75, 0x01,                                                                                                 #     REPORT_SIZE (1)
            0x25, 0x01,                                                                                                 #     LOGICAL_MAXIMUM (1)
            0x15, 0x00,                                                                                                 #     LOGICAL_MINIMUM (0)
            0x81, 0x02,                                                                                                 #     Input (Data, Variable, Absolute)
            0xc0,                                                                                                       #   END_COLLECTION
            0xc0                                                                                                        # END_COLLECTION
        ]
        # fmt: on

        # Define the initial joystick state.
        self.x = 0
        self.y = 0

        self.button1 = 0
        self.button2 = 0
        self.button3 = 0
        self.button4 = 0
        self.button5 = 0
        self.button6 = 0
        self.button7 = 0
        self.button8 = 0

        self.services.append(self.HIDS)                                                                                 # Append to list of service descriptions.

    # Overwrite super to register HID specific service.
    def start(self):
        super(Joystick, self).start()                                                                                   # Start super to register DIS and BAS services.

        print("Registering services")
        handles = self._ble.gatts_register_services(self.services)                                                      # Register services and get read/write handles for all services.
        self.save_service_characteristics(handles)                                                                      # Save the values for the characteristics.
        self.write_service_characteristics()                                                                            # Write the values for the characteristics.
        self.adv = Advertiser(self._ble, [UUID(0x1812)], self.device_appearance, self.device_name)                      # Create an Advertiser. Only advertise the top level service, i.e., the HIDS.
        print("Server started")

    # Overwrite super to save HID specific characteristics.
    def save_service_characteristics(self, handles):
        super(Joystick, self).save_service_characteristics(handles)                                                     # Call super to save DIS and BAS characteristics.

        (h_info, h_hid, h_ctrl, self.h_rep, h_d1, h_proto) = handles[3]                                                 # Get the handles for the HIDS characteristics. These correspond directly to self.HIDS. Position 3 because of the order of self.services.

        b = self.button1 + self.button2 * 2 + self.button3 * 4 + self.button4 * 8 + self.button5 * 16 + self.button6 * 32 + self.button7 * 64 + self.button8 * 128
        state = struct.pack("bbB", self.x, self.y, b)                                                                   # Pack the initial joystick state as described by the input report.

        print("Saving HID service characteristics")
        # Save service characteristics
        self.characteristics[h_info] = ("HID information", b"\x01\x01\x00\x00")                                         # HID info: ver=1.1, country=0, flags=000000cw with c=normally connectable w=wake up signal
        self.characteristics[h_hid] = ("HID input report map", bytes(self.HID_INPUT_REPORT))                            # HID input report map.
        self.characteristics[h_ctrl] = ("HID control point", b"\x00")                                                   # HID control point.
        self.characteristics[self.h_rep] = ("HID report", state)                                                        # HID report.
        self.characteristics[h_d1] = ("HID reference", struct.pack("<BB", 1, 1))                                        # HID reference: id=1, type=input.
        self.characteristics[h_proto] = ("HID protocol mode", b"\x01")                                                  # HID protocol mode: report.

    # Overwrite super to notify central of a hid report.
    def notify_hid_report(self):
        if self.is_connected():
            b = self.button1 + self.button2 * 2 + self.button3 * 4 + self.button4 * 8 + self.button5 * 16 + self.button6 * 32 + self.button7 * 64 + self.button8 * 128
            state = struct.pack("bbB", self.x, self.y, b)                                                               # Pack the joystick state as described by the input report.
            self.characteristics[self.h_rep] = ("HID report", state)
            self._ble.gatts_notify(self.conn_handle, self.h_rep, state)                                                 # Notify client by writing to the report handle.
            print("Notify with report: ", struct.unpack("bbB", state))

    # Set the joystick axes values.
    def set_axes(self, x=0, y=0):
        if x > 127:
            x = 127
        elif x < -127:
            x = -127

        if y > 127:
            y = 127
        elif y < -127:
            y = -127

        self.x = x
        self.y = y

    # Set the joystick button values.
    def set_buttons(self, b1=0, b2=0, b3=0, b4=0, b5=0, b6=0, b7=0, b8=0):
        self.button1 = b1
        self.button2 = b2
        self.button3 = b3
        self.button4 = b4
        self.button5 = b5
        self.button6 = b6
        self.button7 = b7
        self.button8 = b8
