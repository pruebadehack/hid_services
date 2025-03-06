# MicroPython Human Interface Device library
# Copyright (C) 2021 H. Groefsema
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from micropython import const
import struct
import bluetooth
import json
import binascii
from bluetooth import UUID
from lib.hidservices.constants import Constants

# Class that represents a general HID device services.
class HumanInterfaceDevice(object):
    # Define device states
    DEVICE_STOPPED = const(0)
    DEVICE_IDLE = const(1)
    DEVICE_ADVERTISING = const(2)
    DEVICE_CONNECTED = const(3)

    def __init__(self, device_name="Generic HID Device"):
        self._ble = bluetooth.BLE()                                                                                     # The BLE.
        self.adv = None                                                                                                 # The advertiser.
        self.device_state = HumanInterfaceDevice.DEVICE_STOPPED                                                         # The initial device state.
        self.conn_handle = None                                                                                         # The handle of the connected client. HID devices can only have a single connection.
        self.state_change_callback = None                                                                               # The user defined callback function which gets called when the device state changes.
        self.io_capability = Constants.IO_CAPABILITY_NO_INPUT_OUTPUT                                                             # The IO capability of the device. This is used to allow for different ways of identification during pairing.
        self.bond = True                                                                                                # Do we wish to bond with connecting clients? Normally True. Not supported by older Micropython versions.
        self.le_secure = True                                                                                           # Do we wish to use a secure connection? Normally True. Not supported by older Micropython versions.

        self.encrypted = False                                                                                          # Is our connection encrypted?
        self.authenticated = False                                                                                      # Is the connected client authenticated?
        self.bonded = False                                                                                             # Are we bonded with the connected client?
        self.key_size = 0                                                                                               # The encryption key size.

        self.passkey = 1234                                                                                             # The standard passkey for pairing. Only used when io capability allows so. Use the set_passkey(passkey) function to overwrite.
        self.secrets = {}                                                                                               # The key store for bonding

        self.load_secrets()                                                                                             # Call the function to load the known keys for bonding into the key store.

        # General characteristics.
        self.device_name = device_name                                                                                  # The device name.
        self.service_uuids = [UUID(0x180A), UUID(0x180F), UUID(0x1200), UUID(0x1812)]                                   # Service UUIDs: DIS, BAS, DID, HIDS (Device Information Service, BAttery Service, Device Identification service, Human Interface Device Service). These are required for a HID.
        self.device_appearance = 960                                                                                    # The device appearance: 960 = Generic HID.

        # Device Information Service (DIS) characteristics.
        self.model_number = "1"                                                                                         # The model number characteristic.
        self.serial_number = "1"                                                                                        # The serial number characteristic.
        self.firmware_revision = "1"                                                                                    # The firmware revision characteristic.
        self.hardware_revision = "1"                                                                                    # The hardware revision characteristic.
        self.software_revision = "2"                                                                                    # The software revision characteristic.
        self.manufacture_name = "Homebrew"                                                                              # The manufacturer name characteristic.

        # DIS plug and play (PnP) characteristics.
        self.pnp_manufacturer_source = 0x01                                                                             # The manufacturer source. 0x01 = Bluetooth uuid list.
        self.pnp_manufacturer_uuid = 0xFFFF                                                                             # The manufacturer id, e.g., 0xFEB2 for Microsoft, 0xFE61 for Logitech, 0xFD65 for Razer, 0xFFFF = default.
        self.pnp_product_id = 0x01                                                                                      # The product id. 0x01 = 1.
        self.pnp_product_version = 0x0123                                                                               # The product version. 0x0123 = 1.23.

        # BAttery Service (BAS) characteristics.
        self.battery_level = 100                                                                                        # The battery level characteristic (percentages).


        self.DIS = (                                                                                                    # Device Information Service (DIS) description.
            UUID(0x180A),                                                                                               # 0x180A = Device Information.
            (
                (UUID(0x2A24), Constants.F_READ),                                                                                 # 0x2A24 = Model number string, to be read by client.
                (UUID(0x2A25), Constants.F_READ),                                                                                 # 0x2A25 = Serial number string, to be read by client.
                (UUID(0x2A26), Constants.F_READ),                                                                                 # 0x2A26 = Firmware revision string, to be read by client.
                (UUID(0x2A27), Constants.F_READ),                                                                                 # 0x2A27 = Hardware revision string, to be read by client.
                (UUID(0x2A28), Constants.F_READ),                                                                                 # 0x2A28 = Software revision string, to be read by client.
                (UUID(0x2A29), Constants.F_READ),                                                                                 # 0x2A29 = Manufacturer name string, to be read by client.
                (UUID(0x2A50), Constants.F_READ),                                                                                 # 0x2A50 = PnP ID, to be read by client.
            ),
        )

        self.BAS = (                                                                                                    # Battery Service (BAS) description.
            UUID(0x180F),                                                                                               # 0x180F = Battery Information.
            (
                (UUID(0x2A19), Constants.F_READ_NOTIFY, (                                                                         # 0x2A19 = Battery level, to be read by client after being notified of change.
                    (UUID(0x2904), Constants.DSC_F_READ),                                                                         # 0x2904 = Characteristic Presentation Format.
                )),
            ),
        )

        self.DID = (                                                                                                    # Device Identification Profile (DID) description.
            UUID(0x1200),                                                                                               # 0x1200 = PnPInformation.
            (
                (UUID(0x0200), Constants.F_READ),                                                                                 # 0x0200 = SpecificationID.
                (UUID(0x0201), Constants.F_READ),                                                                                 # 0x0201 = VendorID.
                (UUID(0x0202), Constants.F_READ),                                                                                 # 0x0202 = ProductID.
                (UUID(0x0203), Constants.F_READ),                                                                                 # 0x0203 = Version.
                (UUID(0x0204), Constants.F_READ),                                                                                 # 0x0204 = PrimaryRecord.
                (UUID(0x0205), Constants.F_READ),                                                                                 # 0x0205 = VendorIDSource.
            ),
        )

        self.services = [self.DIS, self.BAS, self.DID]                                                                  # List of service descriptions. We will append HIDS in their respective subclasses.

        self.HID_INPUT_REPORT = None                                                                                    # The HID USB input report. We will specify these in their respective subclasses.

        self.characteristics = {}                                                                                       # List which maps handles to (description, value) tuple.

        print("Server created")

    # Interrupt request callback function.
    def ble_irq(self, event, data):
        if event == Constants.IRQ_CENTRAL_CONNECT:                                                                               # Central connected.
            self.conn_handle, _, _ = data                                                                               # Save the handle. HIDS specification only allow one central to be connected.
            self.set_state(HumanInterfaceDevice.DEVICE_CONNECTED)                                                       # Set the device state to connected.
            print("Central connected:", self.conn_handle)
        elif event == Constants.IRQ_CENTRAL_DISCONNECT:                                                                          # Central disconnected.
            conn_handle, addr_type, addr = data
            self.conn_handle = None                                                                                     # Discard old handle.
            self.set_state(HumanInterfaceDevice.DEVICE_IDLE)
            self.encrypted = False
            self.authenticated = False
            self.bonded = False
            print("Central disconnected:", conn_handle)
        elif event == Constants.IRQ_GATTS_WRITE:                                                                                 # Write operation from client.
            conn_handle, attr_handle = data
            value = self._ble.gatts_read(attr_handle)
            description, _val = self.characteristics.get(attr_handle, (None, None))
            if description is None:
                print("Client initiated write on unknown handle:", attr_handle, "with value", value)
                return Constants.GATTS_ERROR_ATTR_NOT_FOUND
            else:
                self.characteristics[attr_handle] = (description, value)
                print("Client initiated write on", description, "with value", value)
                return Constants.GATTS_NO_ERROR
        elif event == Constants.IRQ_GATTS_READ_REQUEST:                                                                          # Read request from client.
            conn_handle, attr_handle = data
            description, val = self.characteristics.get(attr_handle, (None, None))
            print("Read request:", description if description else attr_handle, "with value" if val else "", val if val else "")
            if conn_handle != self.conn_handle:                                                                         # If different connection, return no permission.
                return Constants.GATTS_ERROR_READ_NOT_PERMITTED
            elif description == None:                                                                                   # If the handle is unknown, return invalid handle.
                return Constants.GATTS_ERROR_INVALID_HANDLE
            elif self.bond and not self.bonded:                                                                         # If we wish to bond but are not bonded, return insufficient authorization.
                return Constants.GATTS_ERROR_INSUFFICIENT_AUTHORIZATION
            elif self.io_capability > Constants.IO_CAPABILITY_NO_INPUT_OUTPUT and not self.authenticated:                        # If we can authenticate but the client hasn't authenticated, return insufficient authentication.
                return Constants.GATTS_ERROR_INSUFFICIENT_AUTHENTICATION
            elif self.le_secure and (not self.encrypted or self.key_size < 16):                                         # If we wish for a secure connection but it is unencrypted or not strong enough, return insufficient encryption.
                return Constants.GATTS_ERROR_INSUFFICIENT_ENCRYPTION
            else:                                                                                                       # Otherwise, return no error.
                return Constants.GATTS_NO_ERROR
        elif event == Constants.IRQ_GATTS_INDICATE_DONE:                                                                         # A sent indication was done. (We don't use indications currently. If needed, define a callback function and override this function.)
            conn_handle, value_handle, status = data
            print("Indicate done:", data)
        elif event == Constants.IRQ_MTU_EXCHANGED:                                                                               # MTU was exchanged, set it.
            conn_handle, mtu = data
            self._ble.config(mtu=mtu)
            print("MTU exchanged:", mtu)
        elif event == Constants.IRQ_CONNECTION_UPDATE:                                                                           # Connection parameters were updated.
            self.conn_handle, conn_interval, conn_latency, supervision_timeout, status = data                           # The new parameters.
            print("Connection update. Interval=", conn_interval, "latency=", conn_latency, "timeout=", supervision_timeout, "status=", status)
            return None                                                                                                 # Return an empty packet.
        elif event == Constants.IRQ_ENCRYPTION_UPDATE:                                                                           # Encryption was updated.
            conn_handle, self.encrypted, self.authenticated, self.bonded, self.key_size = data                          # Update the values.
            print("Encryption update:", conn_handle, self.encrypted, self.authenticated, self.bonded, self.key_size)
        elif event == Constants.IRQ_PASSKEY_ACTION:                                                                              # Passkey actions: accept connection or show/enter passkey.
            conn_handle, action, passkey = data
            print("Passkey action:", conn_handle, action, passkey)
            if action == Constants.PASSKEY_ACTION_NUMCMP:                                                                        # Do we accept this connection?
                accept = False
                if self.passkey_callback is not None:                                                                   # Is callback function set?
                    accept = self.passkey_callback()                                                                    # Call callback for input.
                self._ble.gap_passkey(conn_handle, action, accept)
            elif action == Constants.PASSKEY_ACTION_DISP:                                                                        # Show our passkey.
                print("Displaying passkey")
                self._ble.gap_passkey(conn_handle, action, self.passkey)
            elif action == Constants.PASSKEY_ACTION_INPUT:                                                                       # Enter passkey.
                print("Prompting for passkey")
                pk = None
                if self.passkey_callback is not None:                                                                   # Is callback function set?
                    pk = self.passkey_callback()                                                                        # Call callback for input.
                self._ble.gap_passkey(conn_handle, action, pk)
            else:
                print("Unknown passkey action")
        elif event == Constants.IRQ_SET_SECRET:                                                                                  # Set secret for bonding.
            sec_type, key, value = data
            key = (sec_type, bytes(key))
            value = bytes(value) if value else None
            if value is None:                                                                                           # If value is empty, and
                if key in self.secrets:                                                                                 # If key is known then
                    del self.secrets[key]                                                                               # Forget key
                    self.save_secrets()
                    print("Removing secret:", key)
                    return True
                else:
                    print("Secret not found:", key)
                    return False
            else:
                self.secrets[key] = value                                                                               # Remember key/value
                self.save_secrets()
                print("Saving secret:", key, value)
            return True
        elif event == Constants.IRQ_GET_SECRET:                                                                                  # Get secret for bonding
            sec_type, index, key = data
            _key = (sec_type, bytes(key) if key else None)
            value = None
            if key is None:
                i = 0
                for (t, _k), _val in self.secrets.items():
                    if t == sec_type:
                        if i == index:
                            value = _val
                        i += 1
            else:
                value = self.secrets.get(_key, None)
            print("Returning secret:", bytes(value) if value else None, "for", "key" if key else "index", _key if key else index, "with type", sec_type)
            return value
        else:
            print("Unhandled IRQ event:", event)

    # Start the service.
    # Must be overwritten by subclass, and called in
    # the overwritten function by using super(Subclass, self).start().
    def start(self):
        if self.device_state is HumanInterfaceDevice.DEVICE_STOPPED:
            self._ble.irq(self.ble_irq)                                                                                 # Set interrupt request callback function.
            self._ble.active(1)                                                                                         # Turn on BLE radio.

            # Configure BLE interface
            self._ble.config(gap_name=self.device_name)                                                                 # Set GAP device name.
            self._ble.config(mtu=23)                                                                                    # Configure MTU.
            self._ble.config(bond=self.bond)                                                                            # Allow bonding.
            self._ble.config(le_secure=self.le_secure)                                                                  # Require secure pairing.
            self._ble.config(mitm=self.le_secure)                                                                       # Require man in the middle protection.
            self._ble.config(io=self.io_capability)                                                                     # Set our input/output capabilities. Determines whether and how passkeys are used.

            self.set_state(HumanInterfaceDevice.DEVICE_IDLE)                                                            # Update the device state.

            (addr_type, addr) = self._ble.config('mac')                                                                 # Get our address type and mac address.

            print("BLE on with", "random" if addr_type else "public", "mac address", addr)

    # After registering the DIS and BAS services, write their characteristic values.
    # Must be overwritten by subclass, and called in
    # the overwritten function by using
    # super(Subclass, self).save_service_characteristics(handles).
    def save_service_characteristics(self, handles):
        print("Writing service characteristics")

        (h_mod, h_ser, h_fwr, h_hwr, h_swr, h_man, h_pnp) = handles[0]                                                  # Get handles to DIS service characteristics. These correspond directly to its definition in self.DIS. Position 0 because of the order of self.services.
        (self.h_bat, h_bfmt,) = handles[1]                                                                              # Get handles to BAS service characteristics. These correspond directly to its definition in self.BAS. Position 1 because of the order of self.services.
        (h_sid, h_vid, h_pid, h_ver, h_rec, h_vs) = handles[2]                                                          # Get handles to DID service characteristics. These correspond directly to its definition in self.DID. Position 2 because of the order of self.services.

        # Simplify packing strings into byte arrays.
        def string_pack(in_str, nr_bytes):
            return struct.pack(str(nr_bytes)+"s", in_str.encode('UTF-8'))

        print("Saving device information service characteristics")
        self.characteristics[h_mod] = ("Model number", string_pack(self.model_number, 24))
        self.characteristics[h_ser] = ("Serial number", string_pack(self.serial_number, 16))
        self.characteristics[h_fwr] = ("Firmware revision", string_pack(self.firmware_revision, 8))
        self.characteristics[h_hwr] = ("Hardware revision", string_pack(self.hardware_revision, 16))
        self.characteristics[h_swr] = ("Software revision", string_pack(self.software_revision, 8))
        self.characteristics[h_man] = ("Manufacturer name", string_pack(self.manufacture_name, 36))
        self.characteristics[h_pnp] = ("PnP information", struct.pack(">BHHH", self.pnp_manufacturer_source, self.pnp_manufacturer_uuid, self.pnp_product_id, self.pnp_product_version))

        print("Saving battery service characteristics")
        self.characteristics[self.h_bat] = ("Battery level", struct.pack("<B", self.battery_level))
        self.characteristics[h_bfmt] = ("Battery format", b'\x04\x00\xad\x27\x01\x00\x00')

        print("Saving device identification service characteristics")
        self.characteristics[h_sid] = ("Specification ID", b'0x0103')
        self.characteristics[h_vid] = ("Vendor ID", struct.pack(">H", self.pnp_manufacturer_uuid))
        self.characteristics[h_pid] = ("Product ID", struct.pack(">H", self.pnp_product_id))
        self.characteristics[h_ver] = ("Version", struct.pack(">H", self.pnp_product_version))
        self.characteristics[h_rec] = ("Primary record", b'0x01')
        self.characteristics[h_vs] = ("Vendor source", struct.pack(">H", self.pnp_manufacturer_source))

    # Stop the service.
    def stop(self):
        if self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED:
            if self.device_state is HumanInterfaceDevice.DEVICE_ADVERTISING:
                self.adv.stop_advertising()

            if self.conn_handle is not None:
                self._ble.gap_disconnect(self.conn_handle)
                self.conn_handle = None

            self._ble.active(0)

            self.set_state(HumanInterfaceDevice.DEVICE_STOPPED)
            print("Server stopped")

    # Write service characteristics
    def write_service_characteristics(self):
        print("Writing service characteristics")

        for handle, (name, value) in self.characteristics.items():
            self._ble.gatts_write(handle, value)

    # Load bonding keys from json file.
    def load_secrets(self):
        try:
            with open("keys.json", "r") as file:
                entries = json.load(file)
                for sec_type, key, value in entries:
                    self.secrets[sec_type, binascii.a2b_base64(key)] = binascii.a2b_base64(value)
        except:
            print("No secrets available")

    # Save bonding keys to json file.
    def save_secrets(self):
        try:
            with open("keys.json", "w") as file:
                json_secrets = [
                    (sec_type, binascii.b2a_base64(key, newline=False), binascii.b2a_base64(value, newline=False))
                    for (sec_type, key), value in self.secrets.items()
                ]
                json.dump(json_secrets, file)
        except:
            print("Failed to save secrets")

    # Returns whether the device is not stopped.
    def is_running(self):
        return self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED

    # Returns whether the device is connected with a client.
    def is_connected(self):
        return self.device_state is HumanInterfaceDevice.DEVICE_CONNECTED

    # Returns whether the device services are being advertised.
    def is_advertising(self):
        return self.device_state is HumanInterfaceDevice.DEVICE_ADVERTISING

    # Set a new state and notify the user's callback function.
    def set_state(self, state):
        self.device_state = state
        if self.state_change_callback is not None:
            self.state_change_callback()

    # Returns the state of the device, i.e.
    # - DEVICE_STOPPED,
    # - DEVICE_IDLE,
    # - DEVICE_ADVERTISING, or
    # - DEVICE_CONNECTED.
    def get_state(self):
        return self.device_state

    # Set a callback function to get notifications of state changes, i.e.
    # - DEVICE_STOPPED,
    # - DEVICE_IDLE,
    # - DEVICE_ADVERTISING, or
    # - DEVICE_CONNECTED.
    def set_state_change_callback(self, callback):
        self.state_change_callback = callback

    # Begin advertising the device services.
    def start_advertising(self):
        if self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED and self.device_state is not HumanInterfaceDevice.DEVICE_ADVERTISING:
            self.adv.start_advertising()
            self.set_state(HumanInterfaceDevice.DEVICE_ADVERTISING)

    # Stop advertising the device services.
    def stop_advertising(self):
        if self.device_state is not HumanInterfaceDevice.DEVICE_STOPPED:
            self.adv.stop_advertising()
            if self.device_state is not HumanInterfaceDevice.DEVICE_CONNECTED:
                self.set_state(HumanInterfaceDevice.DEVICE_IDLE)

    # Returns the device name.
    def get_device_name(self):
        return self.device_name

    # Returns the service id's.
    def get_services_uuids(self):
        return self.service_uuids

    # Returns the device appearance.
    def get_appearance(self):
        return self.device_appearance

    # Returns the battery level (percentage).
    def get_battery_level(self):
        return self.battery_level

    # Sets the value for the battery level (percentage).
    def set_battery_level(self, level):
        if level > 100:
            self.battery_level = 100
        elif level < 0:
            self.battery_level = 0
        else:
            self.battery_level = level

    # Set device information.
    # Must be called before calling Start().
    # Variables must be Strings.
    def set_device_information(self, manufacture_name="Homebrew", model_number="1", serial_number="1"):
        self.manufacture_name = manufacture_name
        self.model_number = model_number
        self.serial_number = serial_number

    # Set device revision.
    # Must be called before calling Start().
    # Variables must be Strings.
    def set_device_revision(self, firmware_revision="1", hardware_revision="1", software_revision="1"):
        self.firmware_revision = firmware_revision
        self.hardware_revision = hardware_revision
        self.software_revision = software_revision

    # Set device pnp information.
    # Must be called before calling Start().
    # Must use the following format:
    #   pnp_manufacturer_source: 0x01 for manufacturers uuid from the Bluetooth uuid list OR 0x02 from the USBs id list.
    #   pnp_manufacturer_uuid: 0xFEB2 for Microsoft, 0xFE61 for Logitech, 0xFD65 for Razer with source 0x01.
    #   pnp_product_id: One byte, user defined.
    #   pnp_product_version: Two bytes, user defined, format as 0xJJMN which corresponds to version JJ.M.N.
    def set_device_pnp_information(self, pnp_manufacturer_source=0x01, pnp_manufacturer_uuid=0xFE61, pnp_product_id=0x01, pnp_product_version=0x0123):
        self.pnp_manufacturer_source = pnp_manufacturer_source
        self.pnp_manufacturer_uuid = pnp_manufacturer_uuid
        self.pnp_product_id = pnp_product_id
        self.pnp_product_version = pnp_product_version

    # Set whether to use Bluetooth bonding.
    def set_bonding(self, bond=True):
        self.bond = bond

    # Set whether to use LE secure pairing.
    def set_le_secure(self, le_secure=True):
        self.le_secure = le_secure

    # Set input/output capability of this device.
    # Determines the pairing procedure, e.g., accept connection/passkey entry/just works.
    # Must be called before calling Start().
    # Must use the following values:
    #   _IO_CAPABILITY_DISPLAY_ONLY,
    #   _IO_CAPABILITY_DISPLAY_YESNO,
    #   _IO_CAPABILITY_KEYBOARD_ONLY,
    #   _IO_CAPABILITY_NO_INPUT_OUTPUT, or
    #   _IO_CAPABILITY_KEYBOARD_DISPLAY.
    def set_io_capability(self, io_capability):
        self.io_capability = io_capability

    # Set callback function for pairing events.
    # Depending on the I/O capability used, the callback function should return either a
    # - boolean to accept or deny a connection, or a
    # - passkey that was displayed by the main.
    def set_passkey_callback(self, passkey_callback):
        self.passkey_callback = passkey_callback

    # Set the passkey used during pairing when entering a passkey at the main.
    def set_passkey(self, passkey):
        self.passkey = passkey

    # Notifies the client by writing to the battery level handle.
    def notify_battery_level(self):
        if self.is_connected():
            print("Notify battery level: ", self.battery_level)
            value = struct.pack("<B", self.battery_level)
            self.characteristics[self.h_bat] = ("Battery level", value)
            self._ble.gatts_notify(self.conn_handle, self.h_bat, value)

    # Notifies the client of the HID state.
    # Must be overwritten by subclass.
    def notify_hid_report(self):
        return
