import as7058_communication as a
import as7058_commands as c
import as7058_output_parser as p

COM_PORT = "COM3"
BAUD_RATE = 115200

def main():
    
    com = a.Communicator(COM_PORT, BAUD_RATE)
    write_idenity(com)  

    com.write(c.CMD_ID_VSC_INITIALIZE)
    com.write(c.CMD_ID_VSC_START_MEASUREMENT)
    com.write(c.CMD_ID_VSC_SHUTDOWN)


# Henter identiteten til brettet
def write_idenity(com):
    
    responses = []
    identity_commands = [c.CMD_BASE_ID_APPL_NAME, c.CMD_BASE_ID_VERSION, c.CMD_BASE_ID_SERIAL_NUMBER]
    for command in identity_commands:
        responses.append(com.write(command))

    print(f"{responses[0]} - {responses[1]}\n{responses[2]}\n")


if __name__ == "__main__":
    main()
