from bluetooth import UUID
from lib.hid_services import HumanInterfaceDevice
from lib.advertiser import Advertiser
from lib.hidservices.constants


# Class that represents the Mouse service.
class Mouse(HumanInterfaceDevice):
    def __init__(self, name="Bluetooth Mouse"):
        super(Mouse, self).__init__(name)                                                                               # Set up the general HID services in super.
        self.device_appearance = 962                                                                                    # Device appearance ID, 962 = mouse.

        self.HIDS = (                                                                                                   # Service description: describes the service and how we communicate.
            UUID(0x1812),                                                                                               # 0x1812 = Human Interface Device.
            (
                (UUID(0x2A4A), F_READ),                                                                                 # 0x2A4A = HID information, to be read by client.
                (UUID(0x2A4B), F_READ),                                                                                 # 0x2A4B = HID report map, to be read by client.
                (UUID(0x2A4C), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4C = HID control point, to be written by client.
                (UUID(0x2A4D), F_READ_NOTIFY, (                                                                         # 0x2A4D = HID report, to be read by client after notification.
                    (UUID(0x2908), DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4E), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4E = HID protocol mode, to be written & read by client.
            ),
        )

        # fmt: off
        self.HID_INPUT_REPORT = [                                                                                       # Report Description: describes what we communicate.
            0x05, 0x01,                                                                                                 # USAGE_PAGE (Generic Desktop)
            0x09, 0x02,                                                                                                 # USAGE (Mouse)
            0xa1, 0x01,                                                                                                 # COLLECTION (Application)
            0x85, 0x01,                                                                                                 #   REPORT_ID (1)
            0x09, 0x01,                                                                                                 #   USAGE (Pointer)
            0xa1, 0x00,                                                                                                 #   COLLECTION (Physical)
            0x05, 0x09,                                                                                                 #         Usage Page (Buttons)
            0x19, 0x01,                                                                                                 #         Usage Minimum (1)
            0x29, 0x03,                                                                                                 #         Usage Maximum (3)
            0x15, 0x00,                                                                                                 #         Logical Minimum (0)
            0x25, 0x01,                                                                                                 #         Logical Maximum (1)
            0x95, 0x03,                                                                                                 #         Report Count (3)
            0x75, 0x01,                                                                                                 #         Report Size (1)
            0x81, 0x02,                                                                                                 #         Input(Data, Variable, Absolute); 3 button bits
            0x95, 0x01,                                                                                                 #         Report Count(1)
            0x75, 0x05,                                                                                                 #         Report Size(5)
            0x81, 0x03,                                                                                                 #         Input(Constant);                 5 bit padding
            0x05, 0x01,                                                                                                 #         Usage Page (Generic Desktop)
            0x09, 0x30,                                                                                                 #         Usage (X)
            0x09, 0x31,                                                                                                 #         Usage (Y)
            0x09, 0x38,                                                                                                 #         Usage (Wheel)
            0x15, 0x81,                                                                                                 #         Logical Minimum (-127)
            0x25, 0x7F,                                                                                                 #         Logical Maximum (127)
            0x75, 0x08,                                                                                                 #         Report Size (8)
            0x95, 0x03,                                                                                                 #         Report Count (3)
            0x81, 0x06,                                                                                                 #         Input(Data, Variable, Relative); 3 position bytes (X,Y,Wheel)
            0xc0,                                                                                                       #   END_COLLECTION
            0xc0                                                                                                        # END_COLLECTION
        ]
        # fmt: on

        # Define the initial mouse state.
        self.x = 0
        self.y = 0
        self.w = 0

        self.button1 = 0
        self.button2 = 0
        self.button3 = 0

        self.services.append(self.HIDS)                                                                                 # Append to list of service descriptions.

    # Overwrite super to register HID specific service.
    def start(self):
        super(Mouse, self).start()                                                                                      # Call super to register DIS and BAS services.

        print("Registering services")
        handles = self._ble.gatts_register_services(self.services)                                                      # Register services and get read/write handles for all services.
        self.save_service_characteristics(handles)                                                                      # Save the values for the characteristics.
        self.write_service_characteristics()                                                                            # Write the values for the characteristics.
        self.adv = Advertiser(self._ble, [UUID(0x1812)], self.device_appearance, self.device_name)                      # Create an Advertiser. Only advertise the top level service, i.e., the HIDS.

        print("Server started")

    # Overwrite super to save HID specific characteristics.
    def save_service_characteristics(self, handles):
        super(Mouse, self).save_service_characteristics(handles)                                                        # Call super to write DIS and BAS characteristics.

        (h_info, h_hid, h_ctrl, self.h_rep, h_d1, h_proto) = handles[3]                                                 # Get the handles for the HIDS characteristics. These correspond directly to self.HIDS. Position 3 because of the order of self.services.

        b = self.button1 + self.button2 * 2 + self.button3 * 4
        state = struct.pack("Bbbb", b, self.x, self.y, self.w)                                                          # Pack the initial mouse state as described by the input report.

        print("Saving HID service characteristics")
        self.characteristics[h_info] = ("HID information", b"\x01\x01\x00\x00")                                         # HID info: ver=1.1, country=0, flags=000000cw with c=normally connectable w=wake up signal
        self.characteristics[h_hid] = ("HID input report map", bytes(self.HID_INPUT_REPORT))                            # HID input report map.
        self.characteristics[h_ctrl] = ("HID control point", b"\x00")                                                   # HID control point.
        self.characteristics[self.h_rep] = ("HID report", state)                                                        # HID report.
        self.characteristics[h_d1] = ("HID reference", struct.pack("<BB", 1, 1))                                        # HID reference: id=1, type=input.
        self.characteristics[h_proto] = ("HID protocol mode", b"\x01")                                                  # HID protocol mode: report.

    # Overwrite super to notify central of a hid report
    def notify_hid_report(self):
        if self.is_connected():
            b = self.button1 + self.button2 * 2 + self.button3
            state = struct.pack("Bbbb", b, self.x, self.y, self.w)                                                      # Pack the mouse state as described by the input report.
            self.characteristics[self.h_rep] = ("HID report", state)
            self._ble.gatts_notify(self.conn_handle, self.h_rep, state)                                                 # Notify central by writing to the report handle.
            print("Notify with report: ", struct.unpack("Bbbb", state))

    # Set the mouse axes values.
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

    # Set the mouse scroll wheel value.
    def set_wheel(self, w=0):
        if w > 127:
            w = 127
        elif w < -127:
            w = -127

        self.w = w

    # Set the mouse button values.
    def set_buttons(self, b1=0, b2=0, b3=0):
        self.button1 = b1
        self.button2 = b2
        self.button3 = b3
