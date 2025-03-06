from bluetooth import UUID
from lib.hid_services import HumanInterfaceDevice
from lib.hidservices.advertiser import Advertiser
from lib.hidservices.constants

# Class that represents the Keyboard service.
class Keyboard(HumanInterfaceDevice):
    def __init__(self, name="Bluetooth Keyboard"):
        super(Keyboard, self).__init__(name)                                                                            # Set up the general HID services in super.
        self.device_appearance = 961                                                                                    # Device appearance ID, 961 = keyboard.

        self.HIDS = (                                                                                                   # Service description: describes the service and how we communicate.
            UUID(0x1812),                                                                                               # Human Interface Device.
            (
                (UUID(0x2A4A), F_READ),                                                                                 # 0x2A4A = HID information, to be read by client.
                (UUID(0x2A4B), F_READ),                                                                                 # 0x2A4B = HID report map, to be read by client.
                (UUID(0x2A4C), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4C = HID control point, to be written by client.
                (UUID(0x2A4D), F_READ_NOTIFY, (                                                                         # 0x2A4D = HID report, to be read by client after notification.
                    (UUID(0x2908), DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4D), F_READ_WRITE, (                                                                          # 0x2A4D = HID report
                    (UUID(0x2908), DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4E), F_READ_WRITE_NORESPONSE),                                                                # 0x2A4E = HID protocol mode, to be written & read by client.
            ),
        )

        # fmt: off
        self.HID_INPUT_REPORT = [                                                                                       # Report Description: describes what we communicate.
            0x05, 0x01,                                                                                                 # USAGE_PAGE (Generic Desktop)
            0x09, 0x06,                                                                                                 # USAGE (Keyboard)
            0xa1, 0x01,                                                                                                 # COLLECTION (Application)
            0x85, 0x01,                                                                                                 #     REPORT_ID (1)
            0x75, 0x01,                                                                                                 #     Report Size (1)
            0x95, 0x08,                                                                                                 #     Report Count (8)
            0x05, 0x07,                                                                                                 #     Usage Page (Key Codes)
            0x19, 0xE0,                                                                                                 #     Usage Minimum (224)
            0x29, 0xE7,                                                                                                 #     Usage Maximum (231)
            0x15, 0x00,                                                                                                 #     Logical Minimum (0)
            0x25, 0x01,                                                                                                 #     Logical Maximum (1)
            0x81, 0x02,                                                                                                 #     Input (Data, Variable, Absolute); Modifier byte
            0x95, 0x01,                                                                                                 #     Report Count (1)
            0x75, 0x08,                                                                                                 #     Report Size (8)
            0x81, 0x01,                                                                                                 #     Input (Constant); Reserved byte
            0x95, 0x05,                                                                                                 #     Report Count (5)
            0x75, 0x01,                                                                                                 #     Report Size (1)
            0x05, 0x08,                                                                                                 #     Usage Page (LEDs)
            0x19, 0x01,                                                                                                 #     Usage Minimum (1)
            0x29, 0x05,                                                                                                 #     Usage Maximum (5)
            0x91, 0x02,                                                                                                 #     Output (Data, Variable, Absolute); LED report
            0x95, 0x01,                                                                                                 #     Report Count (1)
            0x75, 0x03,                                                                                                 #     Report Size (3)
            0x91, 0x01,                                                                                                 #     Output (Constant); LED report padding
            0x95, 0x06,                                                                                                 #     Report Count (6)
            0x75, 0x08,                                                                                                 #     Report Size (8)
            0x15, 0x00,                                                                                                 #     Logical Minimum (0)
            0x25, 0x65,                                                                                                 #     Logical Maximum (101)
            0x05, 0x07,                                                                                                 #     Usage Page (Key Codes)
            0x19, 0x00,                                                                                                 #     Usage Minimum (0)
            0x29, 0x65,                                                                                                 #     Usage Maximum (101)
            0x81, 0x00,                                                                                                 #     Input (Data, Array); Key array (6 bytes)
            0xc0                                                                                                        # END_COLLECTION
        ]
        # fmt: on

        # Define the initial keyboard state.
        self.modifiers = 0                                                                                              # 8 bits signifying Right GUI(Win/Command), Right ALT/Option, Right Shift, Right Control, Left GUI, Left ALT, Left Shift, Left Control.
        self.keypresses = [0x00] * 6                                                                                    # 6 keys to hold.

        self.kb_callback = None                                                                                         # Callback function for keyboard messages from client.

        self.services.append(self.HIDS)                                                                                 # Append to list of service descriptions.

    # Interrupt request callback function
    # Overwrite super to catch keyboard report write events by the central.
    def ble_irq(self, event, data):
        if event == _IRQ_GATTS_WRITE:                                                                                   # If a client has written to a characteristic or descriptor.
            conn_handle, attr_handle = data                                                                             # Get the handle to the characteristic that was written.
            if attr_handle == self.h_repout:
                print("Keyboard changed by Central")
                report = self._ble.gatts_read(attr_handle)                                                              # Read the report.
                bytes = struct.unpack("B", report)                                                                      # Unpack the report.
                if self.kb_callback is not None:                                                                        # Call the callback function.
                    self.kb_callback(bytes)
                return _GATTS_NO_ERROR

        return super(Keyboard, self).ble_irq(event, data)                                                               # Let super handle the event.

    # Overwrite super to register HID specific service.
    def start(self):
        super(Keyboard, self).start()                                                                                   # Call super to register DIS and BAS services.

        print("Registering services")
        handles = self._ble.gatts_register_services(self.services)                                                      # Register services and get read/write handles for all services.
        self.save_service_characteristics(handles)                                                                      # Save the values for the characteristics.
        self.write_service_characteristics()                                                                            # Write the values for the characteristics.
        self.adv = Advertiser(self._ble, [UUID(0x1812)], self.device_appearance, self.device_name)                      # Create an Advertiser. Only advertise the top level service, i.e., the HIDS.
        print("Server started")

    # Overwrite super to save HID specific characteristics.
    def save_service_characteristics(self, handles):
        super(Keyboard, self).save_service_characteristics(handles)                                                     # Call super to write DIS and BAS characteristics.

        (h_info, h_hid, h_ctrl, self.h_rep, h_d1, self.h_repout, h_d2, h_proto) = handles[3]                            # Get the handles for the HIDS characteristics. These correspond directly to self.HIDS. Position 3 because of the order of self.services.

        state = struct.pack("8B", self.modifiers, 0, self.keypresses[0], self.keypresses[1], self.keypresses[2], self.keypresses[3], self.keypresses[4], self.keypresses[5])

        print("Saving HID service characteristics")
        self.characteristics[h_info] = ("HID information", b"\x01\x01\x00\x00")                                         # HID info: ver=1.1, country=0, flags=000000cw with c=normally connectable w=wake up signal
        self.characteristics[h_hid] = ("HID input report map", bytes(self.HID_INPUT_REPORT))                            # HID input report map.
        self.characteristics[h_ctrl] = ("HID control point", b"\x00")                                                   # HID control point.
        self.characteristics[self.h_rep] = ("HID input report", state)                                                  # HID report.
        self.characteristics[h_d1] = ("HID input reference", struct.pack("<BB", 1, 1))                                  # HID reference: id=1, type=input.
        self.characteristics[self.h_repout] = ("HID output report", state)                                              # HID report.
        self.characteristics[h_d2] = ("HID output reference", struct.pack("<BB", 1, 2))                                 # HID reference: id=1, type=output.
        self.characteristics[h_proto] = ("HID protocol mode", b"\x01")                                                  # HID protocol mode: report.

    # Overwrite super to notify central of a hid report.
    def notify_hid_report(self):
        if self.is_connected():
            # Pack the Keyboard state as described by the input report.
            state = struct.pack("8B", self.modifiers, 0, self.keypresses[0], self.keypresses[1], self.keypresses[2], self.keypresses[3], self.keypresses[4], self.keypresses[5])
            self.characteristics[self.h_rep] = ("HID input report", state)
            self._ble.gatts_notify(self.conn_handle, self.h_rep, state)                                                 # Notify central by writing to the report handle.
            print("Notify with report: ", struct.unpack("8B", state))

    # Set the modifier bits, notify to send the modifiers to central.
    def set_modifiers(self, right_gui=0, right_alt=0, right_shift=0, right_control=0, left_gui=0, left_alt=0, left_shift=0, left_control=0):
        self.modifiers = (right_gui << 7) + (right_alt << 6) + (right_shift << 5) + (right_control << 4) + (left_gui << 3) + (left_alt << 2) + (left_shift << 1) + left_control

    # Press keys, notify to send the keys to central.
    # This will hold down the keys, call set_keys() without arguments and notify again to release.
    def set_keys(self, k0=0x00, k1=0x00, k2=0x00, k3=0x00, k4=0x00, k5=0x00):
        self.keypresses = [k0, k1, k2, k3, k4, k5]

    # Set a callback function that gets notified on keyboard changes.
    # Should take a tuple with the report bytes.
    def set_kb_callback(self, kb_callback):
        self.kb_callback = kb_callback