from bluetooth import UUID
from lib.hid_services import HumanInterfaceDevice
from lib.hidservices.advertiser import Advertiser
from lib.hidservices.constants import Constants
import struct

# Class that represents the Mouse service.
class GenericDevice(HumanInterfaceDevice):
    REPORT_KEYBOARD=0x01
    REPORT_MOUSE=0x02
    
    def __init__(self, name="Bluetooth GenericDevice"):
        super(GenericDevice, self).__init__(name)                                                                       # Set up the general HID services in super.
        self.device_appearance_mouse = 962                                                                                    # Device appearance ID, 962 = mouse.
        self.device_appearance_keyboard = 961                                                                                    # Device appearance ID, 961 = keyboard
        self.device_name_mouse = "RGE AsyncMouse"                                                                                    # Device appearance ID, 962 = mouse.
        self.device_name_keyboard = "RGE AsyncKeyboard"                                                                                    # Device appearance ID, 961 = keyboard

        self.HIDS = (                                                                                                   # Service description: describes the service and how we communicate.
            UUID(0x1812),                                                                                               # Human Interface Device. -> Keyboard
            (
                (UUID(0x2A4A), Constants.F_READ),                                                                                 # 0x2A4A = HID information, to be read by client.
                (UUID(0x2A4B), Constants.F_READ),                                                                                 # 0x2A4B = HID report map, to be read by client.
                (UUID(0x2A4C), Constants.F_READ_WRITE_NORESPONSE),                                                                # 0x2A4C = HID control point, to be written by client.
                (UUID(0x2A4D), Constants.F_READ_NOTIFY, (                                                                         # 0x2A4D = HID report, to be read by client after notification.
                    (UUID(0x2908), Constants.DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4D), Constants.F_READ_WRITE, (                                                                          # 0x2A4D = HID report
                    (UUID(0x2908), Constants.DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4E), Constants.F_READ_WRITE_NORESPONSE),                                                                # 0x2A4E = HID protocol mode, to be written & read by client.

                (UUID(0x2A4A), Constants.F_READ),                                                                                 # 0x2A4A = HID information, to be read by client.
                (UUID(0x2A4B), Constants.F_READ),                                                                                 # 0x2A4B = HID report map, to be read by client.
                (UUID(0x2A4C), Constants.F_READ_WRITE_NORESPONSE),                                                                # 0x2A4C = HID control point, to be written by client.
                (UUID(0x2A4D), Constants.F_READ_NOTIFY, (                                                                         # 0x2A4D = HID report, to be read by client after notification.
                    (UUID(0x2908), Constants.DSC_F_READ),                                                                         # 0x2908 = HID reference, to be read by client.
                )),
                (UUID(0x2A4E), Constants.F_READ_WRITE_NORESPONSE),                                                                # 0x2A4E = HID protocol mode, to be written & read by client.
            ),
        )

        # fmt: off
        self.HID_INPUT_REPORT = [
            0x05, 0x01,			# USAGE_PAGE (Generic Desktop)
            0x09, 0x06,			# USAGE (Keyboard)
            0xa1, 0x01,			# COLLECTION (Application)
            0x85, 0x01,			# 		REPORT_ID (1)
            0x05, 0x07,			# 		USAGE_PAGE (Keyboard)
            0x19, 0xe0,			# 		USAGE_MINIMUM (Keyboard LeftControl)
            0x29, 0xe7,			# 		USAGE_MAXIMUM (Keyboard Right GUI)
            0x15, 0x00,			# 		LOGICAL_MINIMUM (0)
            0x25, 0x01,			# 		LOGICAL_MAXIMUM (1)
            0x95, 0x08,			# 		REPORT_COUNT (8)
            0x75, 0x01,			# 		REPORT_SIZE (1)
            0x81, 0x02,			# 		INPUT (Data,Var,Abs)
            0x95, 0x01,			# 		REPORT_COUNT (1)
            0x75, 0x08,			# 		REPORT_SIZE (8)
            0x81, 0x01,			# 		INPUT (Cnst,Ary,Abs)
            0x95, 0x05,			# 		REPORT_COUNT (6)
            0x75, 0x08,			# 		REPORT_SIZE (8)
            0x15, 0x00,			# 		LOGICAL_MINIMUM (0)
            0x25, 0x65,			# 		LOGICAL_MAXIMUM (101)
            0x05, 0x07,			# 		USAGE_PAGE (Keyboard)
            0x19, 0x00,			# 		USAGE_MINIMUM (Reserved (no event indicated))
            0x29, 0x65,			# 		USAGE_MAXIMUM (Keyboard Application)
            0x81, 0x00,			# 		INPUT (Data,Ary,Abs)
            0xc0,				# END_COLLECTION
            0x05, 0x01,			# USAGE_PAGE (Generic Desktop)
            0x09, 0x02,			# USAGE (Mouse)
            0xa1, 0x01,			# COLLECTION (Application)
            0x85, 0x02,			# 		REPORT_ID (2)
            0x09, 0x01,			# 		USAGE (Pointer)
            0xA1, 0x00,			# 		COLLECTION (Physical)
            0x05, 0x09,			# 			USAGE_PAGE (Button)
            0x19, 0x01,			# 			USAGE_MINIMUM
            0x29, 0x03,			# 			USAGE_MAXIMUM
            0x15, 0x00,			# 			LOGICAL_MINIMUM (0)
            0x25, 0x01,			# 			LOGICAL_MAXIMUM (1)
            0x95, 0x03,			# 			REPORT_COUNT (3)
            0x75, 0x01,			# 			REPORT_SIZE (1)
            0x81, 0x02,			# 			INPUT (Data,Var,Abs)
            0x95, 0x01,			# 			REPORT_COUNT (1)
            0x75, 0x05,			# 			REPORT_SIZE (5)
            0x81, 0x03,			# 			INPUT (Const,Var,Abs)
            0x05, 0x01,			# 			USAGE_PAGE (Generic Desktop)
            0x09, 0x30,			# 			USAGE (X)
            0x09, 0x31,			# 			USAGE (Y)
            0x09, 0x38,			# 			USAGE (Wheel)
            0x15, 0x81,			# 			LOGICAL_MINIMUM (-127)
            0x25, 0x7F,			# 			LOGICAL_MAXIMUM (127)
            0x75, 0x08,			# 			REPORT_SIZE (8)
            0x95, 0x03,			# 			REPORT_COUNT (3)
            0x81, 0x06,			# 			INPUT (Data,Var,Rel)
            0xC0,				# 		END_COLLECTION
            0xC0,				# END COLLECTION              
        ]         
        # fmt: on

        # Define the initial mouse state.
        self.x = 0
        self.y = 0
        self.w = 0

        self.button1 = 0
        self.button2 = 0
        self.button3 = 0

        # Define the initial keyboard state.
        self.modifiers = 0                                                                                              # 8 bits signifying Right GUI(Win/Command), Right ALT/Option, Right Shift, Right Control, Left GUI, Left ALT, Left Shift, Left Control.
        self.keypresses = [0x00] * 6                                                                                    # 6 keys to hold.

        self.k_h_rep = 0
        self.k_h_repout = 0
        self.m_h_rep = 0
        
        self.adv_m = None
        self.adv_k = None
        
        self.services.append(self.HIDS)                                                                                 # Append to list of service descriptions.

    # Interrupt request callback function
    # Overwrite super to catch keyboard report write events by the central.
    def ble_irq(self, event, data):
        print(f"Event: {event} | Data: {data}")
        
        if event == Constants.IRQ_GATTS_WRITE:                                                                                   # If a client has written to a characteristic or descriptor.
            conn_handle, attr_handle = data                                                                             # Get the handle to the characteristic that was written.
            if attr_handle == self.k_h_repout:
                print("Generic changed by Central")
                report = self._ble.gatts_read(attr_handle)                                                              # Read the report.
                print(report)
                bytes = struct.unpack("B", report)                                                                      # Unpack the report.
                if self.kb_callback is not None:                                                                        # Call the callback function.
                    self.kb_callback(bytes)
                return Constants.GATTS_NO_ERROR

        return super(GenericDevice, self).ble_irq(event, data)
    
    # Overwrite super to register HID specific service.
    def start(self):
        super(GenericDevice, self).start()                                                                                      # Call super to register DIS and BAS services.

        print("Registering services")
        handles = self._ble.gatts_register_services(self.services)                                                      # Register services and get read/write handles for all services.
        self.save_service_characteristics(handles)                                                                      # Save the values for the characteristics.
        self.write_service_characteristics()

#        self.adv = Advertiser(self._ble, [UUID(0x1812)], self.device_appearance_mouse, self.device_name_mouse)                      # Create an Advertiser. Only advertise the top level service, i.e., the HIDS.
        self.adv = Advertiser(self._ble, [UUID(0x1812)], self.device_appearance_keyboard, self.device_name_keyboard)                      # Create an Advertiser. Only advertise the top level service, i.e., the HIDS.

        print("Generic server started")

    # Overwrite super to save HID specific characteristics.
    def save_service_characteristics(self, handles):
        super(GenericDevice, self).save_service_characteristics(handles)                                                        # Call super to write DIS and BAS characteristics.
        print(handles)
        
        (keyb_h_info, keyb_h_hid, keyb_h_ctrl, self.k_h_rep, keyb_h_d1, self.k_h_repout, keyb_h_d2, keyb_h_proto,
        mouse_h_info, mouse_h_hid, mouse_h_ctrl, self.m_h_rep, mouse_h_d1, mouse_h_proto) = handles[3]                                                 # Get the handles for the HIDS characteristics. These correspond directly to self.HIDS. Position 3 because of the order of self.services.

        keyb_state = struct.pack("8B", self.modifiers, 0, self.keypresses[0], self.keypresses[1], self.keypresses[2], self.keypresses[3], self.keypresses[4], self.keypresses[5])

        print("Saving keyboard HID service characteristics")
        self.characteristics[keyb_h_info] = ("HID information", b"\x01\x01\x00\x00")                                         # HID info: ver=1.1, country=0, flags=000000cw with c=normally connectable w=wake up signal
        self.characteristics[keyb_h_hid] = ("HID input report map", bytes(self.HID_INPUT_REPORT))                            # HID input report map.
        self.characteristics[keyb_h_ctrl] = ("HID control point", b"\x00")                                                   # HID control point.
        self.characteristics[self.k_h_rep] = ("HID input report", keyb_state)                                                  # HID report.
        self.characteristics[keyb_h_d1] = ("HID input reference", struct.pack("<BB", 1, 1))                                  # HID reference: id=1, type=input.
        self.characteristics[self.k_h_repout] = ("HID output report", keyb_state)                                              # HID report.
        self.characteristics[keyb_h_d2] = ("HID output reference", struct.pack("<BB", 1, 2))                                 # HID reference: id=1, type=output.
        self.characteristics[keyb_h_proto] = ("HID protocol mode", b"\x01")                                                  # HID protocol mode: report.

        b = self.button1 + self.button2 * 2 + self.button3 * 4
        mouse_state = struct.pack("Bbbb", b, self.x, self.y, self.w)                                                          # Pack the initial mouse state as described by the input report.

        print("Saving mouse HID service characteristics")
        self.characteristics[mouse_h_info] = ("HID information", b"\x01\x01\x00\x00")                                         # HID info: ver=1.1, country=0, flags=000000cw with c=normally connectable w=wake up signal
        self.characteristics[mouse_h_hid] = ("HID input report map", bytes(self.HID_INPUT_REPORT))                            # HID input report map.
        self.characteristics[mouse_h_ctrl] = ("HID control point", b"\x00")                                                   # HID control point.
        self.characteristics[self.m_h_rep] = ("HID report", mouse_state)                                                        # HID report.
        self.characteristics[mouse_h_d1] = ("HID reference", struct.pack("<BB", 1, 1))                                        # HID reference: id=1, type=input.
        self.characteristics[mouse_h_proto] = ("HID protocol mode", b"\x01")                                                  # HID protocol mode: report.

    # Overwrite super to notify central of a hid report
    def notify_hid_report_mouse(self):
        if self.is_connected():
            b = self.button1 + self.button2 * 2 + self.button3
            state = struct.pack("Bbbb", b, self.x, self.y, self.w)                                                      # Pack the mouse state as described by the input report.
            self.characteristics[self.m_h_rep] = ("HID report", state)
            self._ble.gatts_notify(self.conn_handle, self.m_h_rep, state)                                                 # Notify central by writing to the report handle.
            print("Notify with report: ", struct.unpack("Bbbb", state))

    def notify_hid_report(self):
        if self.is_connected():
            # Pack the Keyboard state as described by the input report.
            state = struct.pack("8B", self.modifiers, 0, self.keypresses[0], self.keypresses[1], self.keypresses[2], self.keypresses[3], self.keypresses[4], self.keypresses[5])
            self.characteristics[self.k_h_rep] = ("HID input report", state)
            self._ble.gatts_notify(self.conn_handle, self.k_h_rep, state)                                                 # Notify central by writing to the report handle.
            print("Notify with report: ", struct.unpack("8B", state))

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
            
    # Begin advertising the device services.
    def start_advertising_(self):
        print("--------------> start_advertising <---------------")
        if self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED and self.device_state is not HumanInterfaceDevice.DEVICE_ADVERTISING:
            self.adv_m.start_advertising()            
            self.adv_k.start_advertising()
            self.set_state(HumanInterfaceDevice.DEVICE_ADVERTISING)

    # Stop advertising the device services.
    def stop_advertising_(self):
        print("--------------> stop_advertising <---------------")
        if self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED:
            self.adv_m.stop_advertising()
            self.adv_k.stop_advertising()
            if self.device_state is not HumanInterfaceDevice.DEVICE_CONNECTED:
                self.set_state(HumanInterfaceDevice.DEVICE_IDLE)