import as7058_macros as m


# Oppsettet til målingen av rå data
RAW_OUTPUT_MAX_LEN = 149
RAW_OUTPUT = {
    "packet_counter"                    : 0x00,     # uint8, 1 byte
    "fifo_samples_num"                  : 0x00,     # uint8, 1 byte
    "acc_samples_num"                   : 0x00,     # uint8, 1 byte
    "flags_and_agc_statuses_num"        : 0x00,     # uint8, 1 byte
    "ext_event_occurrence_num_present"  : bool,     # bool 1 bit    |
    "status_event_present"              : bool,     # bool 1 bit    |-> Ekstra: nedbrytning av "flags_and_agc_statuses_num"
    "agc_statuses_num"                  :  0x0,     # nibble 4 bit  |
    "fifo_samples"                      : 0x00,     # array med uint24, x-bytes     
    "acc_samples"                       : 0x00,     # array med uint24, x-bytes     består av tre koordinater på 2 bytes hver 2*3=6 bytes
    "agc_statuses"                      : 0x00,     # array med uint24, x-bytes
    "status_events"                     : 0x00,     # Valgfritt status event, 0 - 9 bytes
    "ext_event_occurrence_num"          : 0x00      # Valgfritt uint8, 1 byte
}

# Oppsettet til målingen av hjertefrekvens
HRM_OUTPUT = {
    "heart_rate"        : 0x00,     # Uint16, 2 bytes
    "quality"           : 0x00,     # Uint8,  1 byte
    "motion_frequency"  : 0x00,     # Uint8,  1 byte
    "pvr_ms"            : 0x00,     # Uint16, 10 bytes
    "prv_ms_num"        : 0x00,     # Uint8,  1 byte
    "reserved"          : 0x00      # Uint8,  1 byte
}


# Parser outputten til en rå-måling
def parse_raw_payload(output: bytes) -> dict:
    parsed_output = RAW_OUTPUT

    # fiks inn en loop herregud
    parsed_output["packet_counter"] = bytes(output[m.PAYLOAD_OFFSET])
    parsed_output["fifo_samples_num"] = bytes([output[m.PAYLOAD_OFFSET+1]])
    parsed_output["acc_samples_num"] = bytes([output[m.PAYLOAD_OFFSET+2]])
    parsed_output["flags_and_agc_statuses_num"] = bytes([output[m.PAYLOAD_OFFSET+3]])

    # Holder på indeksen fordi her går det unna!!!
    current_index = m.PAYLOAD_OFFSET + 4

    # Leser antall fifo_statuser og legger dem inn
    fifo_samples = []
    fifo_samples_num = int.from_bytes(parsed_output["fifo_samples_num"]);
    for _ in range(fifo_samples_num):
        single_fifo_sample = bytes([])
        for _ in range(m.FIFO_SAMPLE_SIZE):
            single_fifo_sample += bytes([output[current_index]])
            current_index += 1
        fifo_samples.append(single_fifo_sample)
    parsed_output["fifo_samples"] = fifo_samples

    # Leser antall acc_sampler og legger dem inn
    acc_samples = []
    acc_samples_num = int.from_bytes(parsed_output["acc_samples_num"]);
    for _ in range(acc_samples_num):
        single_acc_sample = bytes([])
        for _ in range(m.ACC_SAMPLE_SIZE):
            single_acc_sample += bytes([output[current_index]])
            current_index += 1
        acc_samples.append(single_acc_sample)
    parsed_output["acc_samples"] = acc_samples

    # Leser antall agc_statuser og legger dem inn
    agc_statuses = []
    agc_statuses_num = int.from_bytes(parsed_output["flags_and_agc_statuses_num"]) & 0x0F;
    parsed_output["agc_statuses_num"] = agc_statuses_num
    for _ in range(agc_statuses_num):
        single_agc_status = bytes([])
        for _ in range(m.AGC_STATUS_SIZE):
            single_agc_status += bytes([output[current_index]])
            current_index += 1
        agc_statuses.append(single_agc_status)
    parsed_output["agc_statuses"] = agc_statuses

    # Sjekker om status_event er her: Legger til boolen og evt verdiene
    status_event_present = ((int.from_bytes(parsed_output["flags_and_agc_statuses_num"]) >> 4) & 0x01) == 1
    parsed_output["status_event_present"] = status_event_present
    if status_event_present:

        status_events = bytes([])
        for _ in range(m.STATUS_EVENT_SIZE):
            status_events += bytes([output[current_index]])
            current_index += 1
        parsed_output["status_events"] = status_events

    # Sjekker om ext_event- er her: Legger til boolen og evt verdien
    ext_event_occurrence_num_present = ((int.from_bytes(parsed_output["flags_and_agc_statuses_num"]) >> 5) & 0x01) == 1
    parsed_output["ext_event_occurrence_num_present"] = ext_event_occurrence_num_present
    print(ext_event_occurrence_num_present)
    if ext_event_occurrence_num_present:
        
        parsed_output["ext_event_occurrence_num"] = bytes([output[current_index]])

    return parsed_output



# Parser outputten til en HRM-måling
def parse_hrm_payload(output: bytes) -> dict:    
    parsed_output = HRM_OUTPUT

    parsed_output["heart_rate"] = bytes([output[m.PAYLOAD_OFFSET], output[m.PAYLOAD_OFFSET+1]])
    parsed_output["quality"] = bytes([output[m.PAYLOAD_OFFSET+2]])
    parsed_output["motion_frequency"] = bytes([output[m.PAYLOAD_OFFSET+3]])
    
    pvr_data = bytes([])
    for byte_index in range(m.PAYLOAD_OFFSET+4, m.PAYLOAD_OFFSET+14):
        pvr_data += bytes([output[byte_index]])
    parsed_output["pvr_ms"] = pvr_data

    parsed_output["pvr_ms_num"] = output[m.PAYLOAD_OFFSET+14]
    parsed_output["reserved"] = output[m.PAYLOAD_OFFSET+15]

    return parsed_output


# Returnerer payload_len som en int
def get_payload_length(output: bytes) -> int:

    # Last inn payload_len inn i en tabell
    payload_len = []
    for byte_index in range(m.PAYLOAD_LEN_OFFSET, m.PAYLOAD_OFFSET):
        payload_len.append(output[byte_index])

    # Bruker big-endian fordi listen ovenfor er invertert
    return int.from_bytes(bytes(payload_len), "big")