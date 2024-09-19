import time
import os
from datetime import datetime
import subprocess

#Peachtree decco remote automater

# usb
# coax
# opt 
# aux1
# aux2

STATUS_FILE = "/home/bosch/amplifier_status.txt"  # Path to save amplifier status
GET_RPI_ALSA_STATUS_CMD = "scp root@192.168.178.6:/proc/asound/card0/pcm0p/sub0/status /home/bosch/rpi-alsa-status"
#PCM_STATUS_FILE = "/proc/asound/card0/pcm0p/sub0/status"
PCM_STATUS_FILE = "/home/bosch/rpi-alsa-status"
AMPLIFIER_ON_CMD = "/home/bosch/decco_set.sh"   # Command to turn amplifier on
AMPLIFIER_OFF_CMD = "/home/bosch/decco_off.sh" # Command to turn amplifier off


#AMPLIFIER_ON_CMD = "echo 11"   # Command to turn amplifier on
#AMPLIFIER_OFF_CMD = "echo 13" # Command to turn amplifier off


CHECK_INTERVAL = 10         # Check every 20 seconds
NO_SOUND_THRESHOLD = 20*60  # 30 minutes (in seconds)




def read_pcm_status():
    import subprocess
    try:
        result = subprocess.run(
            ["ssh", "root@192.168.178.6", "-x", "cat /proc/asound/card0/pcm0p/sub0/status | grep RUNNING"],
            stdout=subprocess.DEVNULL,  # Discard the output
            stderr=subprocess.DEVNULL,  # Discard error messages
            timeout=10,  # 10 seconds timeout
            check=True   # Raise an exception if the command fails
        )
        return True
    except subprocess.TimeoutExpired:
        print("Command timed out after 10 seconds")
        return False
    except subprocess.CalledProcessError:
        # Command didn't find "RUNNING" (grep failed) or other error
        return False
        

def read_pcm_status2():
    if not os.system("ssh root@192.168.178.6 -x cat /proc/asound/card0/pcm0p/sub0/status | grep RUNNING > /dev/null"):
        return True
    else:
        return False    
#    os.system(GET_RPI_ALSA_STATUS_CMD)    
#    try:
#        with open(PCM_STATUS_FILE, 'r') as f:
#            status = f.read()
#            return 'RUNNING' in status
#    except Exception as e:
#        print(f"Error reading PCM status: {e}")
#        return False

def read_amplifier_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return f.read().strip() == 'ON'
    return False

def write_amplifier_status(on):
    with open(STATUS_FILE, 'w') as f:
        f.write('ON' if on else 'OFF')

def turn_amplifier_on():
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Amplifier turning ON")
    write_amplifier_status(True)
    os.system(AMPLIFIER_ON_CMD)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Amplifier turned ON")

def turn_amplifier_off():
    os.system(AMPLIFIER_OFF_CMD)
    write_amplifier_status(False)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Amplifier turned OFF")

def main():
    amplifier_on = read_amplifier_status()
    no_sound_time = 0 if amplifier_on else NO_SOUND_THRESHOLD  # Start with amp off if needed

    if amplifier_on:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - loop started Amplifier On")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - loop started Amplifier Off")
    if read_pcm_status():     
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music playing")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music not playing")
            
    while True:
        if read_pcm_status():
            # Music is playing
            #print("Music is playing")
            if no_sound_time != 0:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music started playing")
                os.system("irsend SEND_ONCE decco AUX1")
            
            if not amplifier_on:
                turn_amplifier_on()
                amplifier_on = True
            no_sound_time = 0
        else:
            # No music
            #print("Music is not playing")
            if no_sound_time == 0:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music stopped playing")
                #os.system("irsend SEND_ONCE decco USB")

            if no_sound_time > 30 and no_sound_time < 96:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music stopped playing for a while")
                os.system("irsend SEND_ONCE decco USB")

            if no_sound_time > (NO_SOUND_THRESHOLD*0.60)   and no_sound_time < (NO_SOUND_THRESHOLD*0.6 + 40) :
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - music stopped playing a long time ago")
                os.system("irsend SEND_ONCE decco MUTE")

            
            no_sound_time += CHECK_INTERVAL
            if amplifier_on and no_sound_time >= NO_SOUND_THRESHOLD:
                turn_amplifier_off()
                amplifier_on = False

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()