import as7058_macros as m

def uint8(value: int) -> bytes:
    return int.to_bytes(value, m.UINT8, byteorder="little")
def uint16(value: int) -> bytes:
    return int.to_bytes(value, m.UINT16, byteorder="little")
def uint24(value: int) -> bytes:
    return int.to_bytes(value, m.UINT24, byteorder="little")
def uint32(value: int) -> bytes:
    return int.to_bytes(value, m.UINT32, byteorder="little")
def array_type(array: list) -> bytes:
    return_type = bytes([])
    for byte in array:
        return_type += uint8(byte)
    return return_type
def custom_type(value: int, size: int) -> bytes:
    return value.to_bytes(size, byteorder="little")