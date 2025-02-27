import serial
import time

port_name = '/dev/ttyUSB0'

ser = serial.Serial(
    port=port_name,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
)

# Enabling the alarm (send "0" to enable it)
print("Enabling alarm...")
for i in range(1000):
    byte_to_send = bytes([0])  # send "0" to enable the alarm
    print(byte_to_send)
    ser.write(byte_to_send)        
    time.sleep(0.01)  # Adjust sleep time as necessary for your use case

# Optionally, wait for some time before disabling the alarm
time.sleep(2)  # Wait 5 seconds or however long you want the alarm to be active

# Attempt to disable the alarm (try different sequences)
print("Disabling alarm...")

# Possible sequences for disabling (adjust according to your system)
disable_sequences = [
    bytes([255]),    # A common signal for turning off
    bytes([1]),      # If this reduces volume, it might still be part of a larger sequence
    bytes([2]),      # If '2' is used for full disable, try this
    bytes([255, 0])  # A possible combination of bytes (change if needed)
]

# Try each disable sequence
for seq in disable_sequences:
    for i in range(1000):
        print(f"Sending disable sequence: {seq}")
        ser.write(seq)
        time.sleep(0.1)  # Adjust sleep time as necessary for your use case

ser.close()
