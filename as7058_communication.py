import serial
import struct
import crcmod

import as7058_commands as c

# CRC-16-CCITT relaterte konstanter
SYNC_BYTE = bytes([0x55])                                       # Sync-byten hver kommando trenger
crc16 = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False)     # Hva programmet bruker til å kalkulere checksummen

# Konstanter relatert til oppsettet av responser (MED SYNC-BYTE)
COMMAND_ID_OFFSET   = 1       # Offsettet til kommando-IDen
TARGET_ID_OFFSET    = 2       # Offsettet til target-IDen
ERROR_CODE_OFFSET   = 3       # Offsettet til errorkoden
PAYLOAD_LEN_OFFSET  = 4       # Offsettet fra begynnelsen til lengden av payloaden
PAYLOAD_OFFSET      = 8       # Offsettet fra begynnelsen av responsen til selve payloaden


class Communicator:

    ser = None              # Serial-objektet
    last_exit_code = 0      # Den siste exitkoden gitt av en kommando
    timeout = 0             # Pausen mellom lesninger


    # Tar inn com-porten brettet er koblet til og baudraten
    def __init__(self, com_port, baud_rate, timeout=0.01):
        self.timeout = timeout
        self.ser = self.__connect(com_port, baud_rate, timeout)
        
    
    # Skriver en kommando til brettet og leser responsen
    # Bytes      --> Antall bytes som skal leses (Grunninstillt til 100 bytes)
    # Return_str --> Om metoden skal returnere responsen som en string eller bytes (Grunninstillt til å returnere string)
    def write(self, command, bytes=100, return_str=True) -> str:
        
        # Formater kommandoen til en RPC-pakke
        crc_value = crc16(SYNC_BYTE + command)
        checksum = struct.pack("<H", crc_value)
        formated_command = SYNC_BYTE + command + checksum

        # Skriv og les
        self.ser.write(formated_command)
        response = self.ser.read(bytes)

        # Sjekker om ingen respons ble gitt
        if response == b'':
            print("OBS: INGEN RESPONS GITT")
            return None

        # Sjekk for feil
        if self.__check_error_code(response):
            return None

        # Returner string eller bytes
        if return_str: 
            return self.__payload_as_string(response)
        else: 
            return response


    def measure_bio_data(self, log_file=None, measure_cycles=1000):

        if log_file is not None:
            file = open(log_file, "r")
        
        for cycle in range(0, measure_cycles):

            data = self.ser.read()




    
    #####               Private metoder                  #####

    # Kobler til en com-port
    # Hvis koblingen nektes, exiterer programmet
    def __connect(self, com_port, baud_rate, timeout) -> serial:
        try:
            ser = serial.Serial(port=com_port, baudrate=baud_rate, timeout=timeout)
            print(f"Koblet til: {com_port}")

        except serial.SerialException:
            print(f"Kunne ikke koble til: {com_port}")
            exit()

        return ser
    

    # Sjekker etter feil gitt av en respons. Brukes BARE for å melde om en feilkode:
    # Om en feil returneres printes en melding til terminalen, men ingenting stoppes / kastes.
    # Errorkoden lagres i attributten: self.last_exit_code
    def __check_error_code(self, response) -> bool:

        # Kode == 0 --> ingen feil
        error_code = response[ERROR_CODE_OFFSET]
        self.last_exit_code = error_code
        if(error_code == 0):
            return False

        # Hvis ikke --> En feil
        faulty_command = c.get_command_from_id(response[COMMAND_ID_OFFSET])
        error_msg = c.get_error_desc(error_code)
        print("-"*60)
        print(f"Error kastet av:\t{faulty_command} ({error_code})")
        print(f"[Dokumentasjon]:\t{error_msg}")
        print("-"*60)
        return True
    
    
    # Henter payloaden i form av en string
    def __payload_as_string(self, response) -> str:
    
        # Hent lengden av payloaden
        payload_length = 0
        for byte_index in range(PAYLOAD_LEN_OFFSET, PAYLOAD_OFFSET):
            payload_length += response[byte_index]

        # Ekstrakt payloaden
        payload = []
        for byte in range(0, payload_length):
            payload.append(chr(response[PAYLOAD_OFFSET + byte]))

        return ''.join(payload)
    
