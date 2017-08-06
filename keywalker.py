import usb.core

dev = usb.core.find(idVendor=0x0483, idProduct=0x4021)
if dev is None:
    raise ValueError('Our device is not connected')
