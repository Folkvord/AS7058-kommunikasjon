
# Viktige filer

Dette prosjektet består av flere filer, **men tre av dem er viktigst**:

## as7058_communication.py
Inneholder en `Communicator`-klasse som lar deg kommunisere direkte med AS7058-brettet via en COM-port (UART/USB-til-seriell). Klassen håndterer både sending og mottak av data, og gir deg kontroll over lavnivå kommunikasjon med sensoren.

- `write(cmd, bytes_to_read, return_str)`
  - Sender en ferdigbygd kommando til brettet
  - Leser og returnerer responsen (enten som rå bytes eller string)

- `read(bytes_to_read)`
  - Leser en gitt mengde bytes direkte fra brettet uten å sende ny kommando

**Andre egenskaper:**
- Setter opp COM-port, baudrate og timeout
- Håndterer både binær og tekstbasert respons

---

## as7058_datatypes.py
Gir deg funksjoner som oversetter verdier til bytes – akkurat slik AS7058-firmwaren krever det.

Inneholder:
- `uint8(value)`
- `uint16(value)`
- `uint24(value)`
- `uint32(value)`
- `custom_type(value, size)`

Disse gjør det enkelt å bygge payloads til kommandoer som trenger f.eks. 3-byters verdier.

---

## as7058_commands.py

Inneholder alle ferdigdefinerte kommandoer og hjelpefunksjoner for å modifisere dem før de sendes til AS7058-brettet. Hver kommando er representert som en `bytes`-konstant og inkluderer felt som `cmdID`, `targetID`, `errcode` og `payload_len`.

>  Merk: Kommandoene inkluderer **ikke** sync-byte (`0x55`), payload-data eller CRC-checksum. Disse legges til rett før sending.

### Viktig funksjon:

- `mod_cmd(cmd, targetID=None, payload=None)`
  - Brukes for å tilpasse en eksisterende kommando med ny `targetID` og/eller `payload`.
  - `cmd` er obligatorisk og må være en kommando definert i denne filen.
  - `targetID` og `payload` er valgfrie og forventes å være av typen `bytes`.
  - Payload-lengden (`payload_len`) oppdateres automatisk.

**Tips**: Det anbefales å bruke `custom_type()` fra `as7058_datatypes.py` for å lage korrekt formatterte payloads med ønsket lengde (inkludert ledende nuller).

---

Vil du sende en kommando til brettet?
1. Velg en kommando fra `as7058_commands.py`
2. Bruk `mod_cmd()` til å sette inn riktig `targetID` og `payload`
3. Send den via `Communicator.write()` fra `as7058_communication.py`

---

# Hvordan bruke rammeverket

1. **Start med `as7058_commands.py`**  
   Velg en kommando, og bruk `mod_cmd()` til å sette target-ID og payload.

2. **Bruk `as7058_communication.py`**  
   Instansier `Communicator`, og kall `write()` for å sende kommandoen til brettet.

3. **Bruk `as7058_datatypes.py`**  
   For å formatere tall til riktig lengde (f.eks. 24-bit ints), bruk `uint24()` eller `custom_type()`.

---

# Eksempel

```python
from as7058_commands import CMD_ID_VSC_CL_READ_REGISTER, mod_cmd
from as7058_communication import Communicator

com = Communicator("COM3", 115200, timeout=1)
cmd = mod_cmd(CMD_ID_VSC_CL_READ_REGISTER, payload=0x0F)
response = com.write(cmd, bytes_to_read=100, return_str=True)
print(response)
```

---

# TL;DR

- Dette rammeverket gir deg lavnivå-kontroll over hele AS7058-brettet
- Du bygger kommandoene manuelt, som gjør det perfekt for testing og utforsking
- Bruk `mod_cmd()` + `custom_type()` for å modifisere kommandoer
- Bruk `Communicator.write()` for å sende det og for å få responsen

---
