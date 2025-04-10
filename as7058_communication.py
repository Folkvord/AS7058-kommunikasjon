import serial
import struct
import crcmod

import as7058_commands as c
import as7058_macros as m
import as7058_datatypes as d

# CRC-16-CCITT relaterte konstanter
SYNC_BYTE = bytes([0x55])                                       # Sync-byten hver kommando trenger
crc16 = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False)     # Hva programmet bruker til å kalkulere checksummen

class Communicator:

    ser = None              # Serial-objektet
    last_exit_code = 0      # Den siste exitkoden gitt av en kommando
    timeout = 0             # Pausen mellom lesninger


    # Tar inn com-porten brettet er koblet til og baudraten
    def __init__(self, com_port: str, baud_rate: int, timeout: float = 0.01):
        self.timeout = timeout
        self.ser = self.__connect(com_port, baud_rate, timeout)
        
    
    # Skriver en kommando til brettet og leser responsen
    # Bytes      --> Antall bytes som skal leses (Grunninstillt til 100 bytes)
    # Return_str --> Om metoden skal returnere responsen som en string eller bytes (Grunninstillt til å returnere string)
    def write(self, command: bytes, bytes: int = 100, return_str: bool = False) -> str:
        
        # Formater kommandoen til en RPC-pakke
        crc_value = crc16(SYNC_BYTE + command)
        checksum = d.uint16(crc_value)
        formated_command = SYNC_BYTE + command + checksum

        # Skriv og les
        self.ser.write(formated_command)
        response = self.ser.read(bytes)

        # Sjekk for feil
        if self.__check_error_code(response):
            return None

        # Returner string eller bytes
        if return_str: 
            return payload_as_string(response)
        else: 
            return response
        
        
    def read(self, bytes : int = 100, expected_type : bytes = None):
        
        read_data = self.ser.read(bytes)
        if not expected_type:
            return read_data
        
        if read_data == b'':
            print("Ingen respons")
            return read_data

        if read_data[m.COMMAND_ID_OFFSET_W_SYNC] != expected_type[m.COMMAND_ID_OFFSET]:
            print("Uforventet type")
        
        return read_data


    
    #####               Private metoder                  #####

    # Kobler til en com-port
    # Hvis koblingen nektes, exiterer programmet
    def __connect(self, com_port: str, baud_rate: int, timeout: float) -> serial:
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
    def __check_error_code(self, response: bytes) -> bool:

        # Sjekker om det kom en tom respons
        if response == b'':
            #self.last_exit_code = 0
            #print("-"*60)
            #print("Kommandoen ga ingen respons")
            #print("-"*60)
            return None

        # Kode == 0 --> ingen feil
        error_code = response[m.ERROR_CODE_OFFSET_W_SYNC]
        self.last_exit_code = error_code
        if(error_code == 0):
            return False

        # Hvis ikke --> En feil
        faulty_command = c.get_command_from_id(response[m.COMMAND_ID_OFFSET_W_SYNC])
        error_msg = c.get_error_desc(error_code)
        print("-"*60)
        print(f"Error kastet av:\t{faulty_command} ({error_code})")
        print(f"[Dokumentasjon]:\t{error_msg}")
        print("-"*60)
        return True
    
    
# Henter payloaden i form av en string
# Brukes som regel av kommandoene som returnerer en stringlike payload
# F.eks: CMD_BASE_ID_VERSION som gir versjonen av firmwaret
def payload_as_string(response: bytes) -> str:
    
    # Hent lengden av payloaden
    payload_length = 0
    for byte_index in range(m.PAYLOAD_LEN_OFFSET_W_SYNC, m.PAYLOAD_OFFSET_W_SYNC):
        payload_length += response[byte_index]

    # Ekstrakt payloaden
    payload = []
    for byte_index in range(m.PAYLOAD_OFFSET_W_SYNC, m.PAYLOAD_OFFSET_W_SYNC + payload_length):
        payload.append(chr(response[byte_index]))

    return ''.join(payload)
    
