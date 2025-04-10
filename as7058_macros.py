# Konstanter relatert til oppsettet av responser (MED SYNC-BYTE)
COMMAND_ID_OFFSET_W_SYNC   = 1       # Offsettet til kommando-IDen
TARGET_ID_OFFSET_W_SYNC    = 2       # Offsettet til target-IDen
ERROR_CODE_OFFSET_W_SYNC   = 3       # Offsettet til errorkoden
PAYLOAD_LEN_OFFSET_W_SYNC  = 4       # Offsettet fra begynnelsen til lengden av payloaden
PAYLOAD_OFFSET_W_SYNC      = 8       # Offsettet fra begynnelsen av responsen til selve payloaden

# Konstanter relatert til oppsettet av responser (UTEN SYNC-BYTE)
COMMAND_ID_OFFSET   = 0
TARGET_ID_OFFSET    = 1
ERROR_CODE_OFFSET   = 2
PAYLOAD_LEN_OFFSET  = 3
PAYLOAD_OFFSET      = 7

# Antall bytes i payload_length segmentet
PAYLOAD_LEN_BYTES = PAYLOAD_OFFSET - PAYLOAD_LEN_OFFSET

# Datatyper (i bytes)
UINT8 = 1
UINT16 = 2
UINT24 = 3
UINT32 = 4
FIFO_SAMPLE_SIZE = UINT24
ACC_SAMPLE_SIZE = 6
AGC_STATUS_SIZE = 4
STATUS_EVENT_SIZE = 9
