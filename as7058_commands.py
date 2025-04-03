# ALLE DISSE KOMMANDOENE ER UFORMATERTE FOR RPC-PROTOKOLLEN
# DISSE MÅ KJØRES GJENNOM RPC_format(command) (Skjer automatisk i funksjonen write())

# OPPSETT (Før syncbyte og checksum):
#   1 BYTE        1 BYTE      1 BYTE      4 BYTES          X-BYTES
# | KOMMANDO-ID | TARGET-ID | ERRORKODE | PAYLOAD LENGTH | PAYLOAD |
#
# BRUKER "LITTLE-ENDIAN ORDER": 
# BIG ENDIAN:       12 34
# LITTLE ENDIAN :   34 12
#

import struct

COMMAND_ID_OFFSET   = 0     # Offsettet til kommando-IDen UTEN SYNCBYTE
TARGET_ID_OFFSET    = 1     # Offsettet til target-IDen UTEN SYNCBYTE
ERROR_CODE_OFFSET   = 2     # Offsettet til errorkoden UTEN SYNCBYTE
PAYLOAD_LEN_OFFSET  = 3     # Offsettet fra begynnelsen til lengden av payloaden UTEN SYNCBYTE
PAYLOAD_OFFSET      = 7     # Offsettet fra begynnelsen av responsen til selve payloaden UTEN SYNCBYTE

# SYNKRONE
CMD_BASE_ID_APPL_NAME       = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Sender applikasjonsnavnet til brettet
CMD_BASE_ID_VERSION         = bytes([0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])     # Sender versjonen av firmvaren brettet bruker
CMD_BASE_ID_SERIAL_NUMBER   = bytes([0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Sender seriellnummeret til brettet

CMD_ID_VSC_INITIALIZE       = bytes([0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Starter innsammlings komponentene 
CMD_ID_VSC_SHUTDOWN         = bytes([0x65, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Stopper innsammlings komponentene 
CMD_ID_VSC_GET_VERSION_CL   = bytes([0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Henter versjonen av Chip Library
CMD_ID_VSC_GET_VERSION_AM   = bytes([0x6d, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])     # Henter versjonen av Application Manager

CMD_ID_VSC_START_MEASUREMENT= bytes([0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Starter innsammling: Regular (Funker med mod_cmd())
CMD_ID_VSC_STOP_MEASUREMENT = bytes([0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Stopper innsammling

# vvv FIX PLZ vvv
CMD_ID_VSC_AM_ENABLE_APPS   = bytes([0x71, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00])     # Starter opp applikasjoner (Payload er spesifik: se dokument)
CMD_ID_VSC_AM_APP_CONFIG    = bytes([0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Redigerer en applikasjon (TargetID og payload er spesifik: se dokument)

# ASYNKRONE
CMD_ID_VSC_AM_APP_OUTPUT    = bytes([0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Henter bio-målinger fra en innsamlingssesjon (brukes etter START_MEASUREMENT) (output payload depends: se dokument)
CMD_ID_VSC_MEAS_ERROR       = bytes([0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])     # Sier i fra om en feil under en bio-målinger


# Gir navnet til en kommando basert på kommando_iden
def get_command_from_id(command_id) -> str:
    command_map = {
        0x00: "CMD_BASE_ID_APPL_NAME",
        0x01: "CMD_BASE_ID_VERSION",
        0x13: "CMD_BASE_ID_SERIAL_NUMBER",

        0x64: "CMD_ID_VSC_INITIALIZE",
        0x65: "CMD_ID_VSC_SHUTDOWN",
        0x6d: "CMD_ID_VSC_GET_VERSION_CL / _AM",

        0x6e: "CMD_ID_VSC_START_MEASUREMENT",
        0x6f: "CMD_ID_VSC_STOP_MEASUREMENT",
        0x71: "CMD_ID_VSC_AM_ENABLE_APPS",
        0x72: "CMD_ID_VSC_AM_APP_CONFIG",

        0x73: "CMD_ID_VSC_AM_APP_OUTPUT",
        0x74: "CMD_ID_VSC_MEAS_ERROR",
    }

    command_name = command_map.get(command_id)
    if command_name is None:
        return "UKJENT KOMMANDO"
    return command_name


# Henter den riktige feilmeldingen til en errorkode
def get_error_desc(error_code) -> str:
    error_descriptions = {
        0x00: "Operation was successful.",
        0x01: "Operation is not permitted.",
        0x02: "Message is invalid. (Unsupported message type, incorrect CRC, ...)",
        0x03: "Message has the wrong size.",
        0x04: "Pointer is invalid. (NULL pointer, pointer wrong memory region, ...)",
        0x05: "Access is denied.",
        0x06: "Argument is invalid.",
        0x07: "An argument has the wrong size.",
        0x08: "Function is not supported or not implemented.",
        0x09: "Operation timed out.",
        0x0a: "Checksum comparison failed.",
        0x0b: "Data overflow occurred.",
        0x0c: "Getting or setting an event failed. (Event queue is full or empty, unexpected event received, ...)",
        0x0d: "Getting or setting an interrupt failed. (Interrupt resource is not available, ...)",
        0x0e: "Accessing the timer peripheral failed.",
        0x0f: "Accessing the LED peripheral failed.",
        0x10: "Accessing the temperature sensor failed.",
        0x11: "Communication error occurred.",
        0x12: "FIFO operation failed.",
        0x13: "Overtemperature detected.",
        0x14: "Sensor identification failed.",
        0x15: "Generic communication interface error. (Communication interface is not available, error while opening or closing a communication interface, ...)",
        0x16: "Synchronization error occurred.",
        0x17: "Generic protocol error occurred.",
        0x18: "Memory allocation error occurred.",
        0x19: "Thread handling operation failed.",
        0x1a: "Accessing the SPI peripheral failed.",
        0x1b: "Accessing the DAC peripheral failed.",
        0x1c: "Accessing the I2C peripheral failed.",
        0x1d: "No data available.",
        0x1e: "System configuration failed. (System resource is not available, system resource generates an error, ...)",
        0x1f: "Accessing the USB peripheral failed.",
        0x20: "Accessing the ADC peripheral failed.",
        0x21: "Sensor configuration failed.",
        0x22: "Saturation detected.",
        0x23: "Mutex handling operation failed.",
        0x24: "Accessing the accelerometer failed.",
        0x25: "Software component is unusable due to incomplete or incorrect configuration.",
        0x26: "BLE stack handling operation failed.",
        0x27: "File handling operation failed.",
        0x28: "Internal data inconsistency detected.",
        0x29: "Module is busy."
    }
    
    error_desc = error_descriptions.get(error_code)
    if error_desc is None:
        return "UKJENT ERROR"
    return error_desc


# Tar en kommando og returnerer den samme kommandoen med de modifiserte verdiene
# Dersom man endrer payloaden, endres payload_len iht payloadens størrelse
# Alle input tas inn som int
def mod_cmd(cmd, target_id=None, error_code=None, payload=None) -> bytes:

    # Kopier kommandoen over til en listeform
    modded_cmd = []
    for byte_index in range(0, len(cmd)):
        modded_cmd.append(cmd[byte_index])

    # Endre attributtene 
    if target_id is not None:
        if target_id >= 256:
            raise ValueError("TargetID kan bare være en byte")
        modded_cmd[1] = target_id
    
    if error_code is not None:
        if error_code >= 256:
            raise ValueError("Error-code kan bare være en byte")
        modded_cmd[2] = error_code

    if payload is not None:
        if payload >= 0x4294967296:
            raise ValueError("Payloaden kan bare være 16 777 215 bytes")

        # Håndter den nye payload lengden:
        # Finn ut hva den nye payload_len er ved å se på lengden av payloaden LOLL
        payload_len = 0
        hex_counter = payload
        while hex_counter:
            hex_counter >>= 8
            payload_len += 1

        # Skriv inn den nye payload_len en
        payload_len_in_bytes = struct.pack("<I", payload_len)
        for byte_index in range(0, PAYLOAD_OFFSET-PAYLOAD_LEN_OFFSET):
            modded_cmd[PAYLOAD_LEN_OFFSET + byte_index] = payload_len_in_bytes[byte_index]

        # Håndter payloaden:
        # Payload som liste av bytes
        payload = payload.to_bytes(payload_len, "little")

        # Finn ut om cmd har en payload fra før av
        # Hvis ikke: append bytes. Hvis: overskriv
        if len(modded_cmd) == PAYLOAD_OFFSET:
            for byte_index in range(0, payload_len):
                modded_cmd.append(payload[byte_index])
        else:
            for byte_index in range(PAYLOAD_OFFSET, PAYLOAD_OFFSET+payload_len):
                try:
                    modded_cmd[byte_index] = payload[byte_index-PAYLOAD_OFFSET];    # Overskriver gamle payloadbytes
                except IndexError: 
                    modded_cmd.append(payload[byte_index-PAYLOAD_OFFSET])           # Hvis vi har overskrevet og nå skriver utenfor payloaden som var


    return bytes(modded_cmd)