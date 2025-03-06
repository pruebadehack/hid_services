import bluetooth
from micropython import const

class Constants(object):
    F_READ = bluetooth.FLAG_READ
    F_WRITE = bluetooth.FLAG_WRITE
    F_READ_WRITE = bluetooth.FLAG_READ | bluetooth.FLAG_WRITE
    F_READ_NOTIFY = bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY
    F_READ_WRITE_NORESPONSE = bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE

    DSC_F_READ = 0x02
    DSC_F_WRITE = 0x03

    # Advertising payloads are repeated packets of the following form:
    #   1 byte data length (N + 1)
    #   1 byte type (see constants below)
    #   N bytes type-specific data
    ADV_TYPE_FLAGS = const(0x01)
    ADV_TYPE_NAME = const(0x09)
    ADV_TYPE_UUID16_COMPLETE = const(0x3)
    ADV_TYPE_UUID32_COMPLETE = const(0x5)
    ADV_TYPE_UUID128_COMPLETE = const(0x7)
    ADV_TYPE_UUID16_MORE = const(0x2)
    ADV_TYPE_UUID32_MORE = const(0x4)
    ADV_TYPE_UUID128_MORE = const(0x6)
    ADV_TYPE_APPEARANCE = const(0x19)

    # IRQ peripheral role event codes
    IRQ_CENTRAL_CONNECT = const(1)
    IRQ_CENTRAL_DISCONNECT = const(2)
    IRQ_GATTS_WRITE = const(3)
    IRQ_GATTS_READ_REQUEST = const(4)
    IRQ_SCAN_RESULT = const(5)
    IRQ_SCAN_DONE = const(6)
    IRQ_PERIPHERAL_CONNECT = const(7)
    IRQ_PERIPHERAL_DISCONNECT = const(8)
    IRQ_GATTC_SERVICE_RESULT = const(9)
    IRQ_GATTC_SERVICE_DONE = const(10)
    IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
    IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
    IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
    IRQ_GATTC_DESCRIPTOR_DONE = const(14)
    IRQ_GATTC_READ_RESULT = const(15)
    IRQ_GATTC_READ_DONE = const(16)
    IRQ_GATTC_WRITE_DONE = const(17)
    IRQ_GATTC_NOTIFY = const(18)
    IRQ_GATTC_INDICATE = const(19)
    IRQ_GATTS_INDICATE_DONE = const(20)
    IRQ_MTU_EXCHANGED = const(21)
    IRQ_L2CAP_ACCEPT = const(22)
    IRQ_L2CAP_CONNECT = const(23)
    IRQ_L2CAP_DISCONNECT = const(24)
    IRQ_L2CAP_RECV = const(25)
    IRQ_L2CAP_SEND_READY = const(26)
    IRQ_CONNECTION_UPDATE = const(27)
    IRQ_ENCRYPTION_UPDATE = const(28)
    IRQ_GET_SECRET = const(29)
    IRQ_SET_SECRET = const(30)
    IRQ_PASSKEY_ACTION = const(31)

    IO_CAPABILITY_DISPLAY_ONLY = const(0)
    IO_CAPABILITY_DISPLAY_YESNO = const(1)
    IO_CAPABILITY_KEYBOARD_ONLY = const(2)
    IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
    IO_CAPABILITY_KEYBOARD_DISPLAY = const(4)

    PASSKEY_ACTION_INPUT = const(2)
    PASSKEY_ACTION_DISP = const(3)
    PASSKEY_ACTION_NUMCMP = const(4)

    GATTS_NO_ERROR = const(0x00)
    GATTS_ERROR_INVALID_HANDLE = const(0x01)
    GATTS_ERROR_READ_NOT_PERMITTED = const(0x02)
    GATTS_ERROR_WRITE_NOT_PERMITTED = const(0x03)
    GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(0x05)
    GATTS_ERROR_REQ_NOT_SUPPORTED = const(0x06)
    GATTS_ERROR_INSUFFICIENT_AUTHORIZATION = const(0x08)
    GATTS_ERROR_ATTR_NOT_FOUND = const(0x0a)
    GATTS_ERROR_INSUFFICIENT_ENCRYPTION = const(0x0f)
    GATTS_ERROR_WRITE_REQ_REJECTED = const(0xFC)
