### Automating my Peachtree Decco with a Hifiberry and a Raspberry Pi IR Remote

![Peachtree decco amplifier and a pi zero 2 W with a IR led](peachtree-pi.jpeg)

This project automates the control of a Peachtree Decco amplifier using a Raspberry Pi with a Hifiberry DAC and a secondary Raspberry Pi configured as an IR remote. The goal is to integrate modern streaming capabilities (Spotify, AirPlay, Roon, etc.) with the Peachtree Decco from an external raspberry pi running hifiberry OS, and the automate power and input controls through a infrared remote running on a second raspberry pi.

The Peachtree Decco amplifier (2007) is known for its excellent sound, but it has a few limitations:
1. The USB input port is prone to breaking. Mine broke twice. Didn't bother to fix it the second time.
2. Volume and input selection need to be manually adjusted after powering on.

To solve the broken USB issue, I added a Raspberry Pi running Hifiberry OS with a [hifiberry DAC](https://www.hifiberry.com/shop/boards/dacplus-dsp/) HAT , allowing me to stream audio remotely. 

To further automate the process, I created this project to simulate the remote, and turn the decco amplifier on when the music starts playing on the hifiberry. This sequence takes 30 seconds, because the analog tube needs to warm up. 

This setup includes features for automatically turning the amplifier on and off based on whether audio is playing, ensuring seamless integration with your audio system.

This project is made possible through open source, including the LIRC config file for the peachtree remote from   [Part of the Thing](https://partofthething.com/thoughts/a-lirc-config-file-for-the-peachtree-audio-decco-ir-remote-control/) 

### Prerequisites
- Peachtree Decco amplifier
- Raspberry Pi with a [hifiberry DAC](https://www.hifiberry.com/shop/boards/dacplus-dsp/) HAT running hifiberry OS attached to the Decco
- Another Raspberry Pi (e.g., Pi Zero 2W) to act as the IR remote
- IR LED
- Optional Resistor and transistor (for long-distance IR signaling)

### Steps

1. **Set up the Raspberry Pi:**
   - Install Raspberry Pi OS (Raspbian) on the Pi.
   - Log in to the Raspberry Pi.

2. **Install LIRC:**
   ```bash
   sudo apt install lirc
   ```

3. **Enable GPIO pins for IR:**
   Add the following lines to `/boot/firmware/config.txt`:
   ```bash
   dtoverlay=gpio-ir,gpio_pin=18
   dtoverlay=gpio-ir-tx,gpio_pin=15
   ```

4. **Configure LIRC modules:**
   Add the following to `/etc/modules` to use pin 18 and 15 for IR input/output:
   ```bash
   lirc_dev
   lirc_rpi gpio_in_pin=18 gpio_out_pin=15
   ```

5. **Edit LIRC configuration:**
   Edit `/etc/lirc/lirc_options.conf` and set the driver to default:
   ```bash
   driver = default
   ```

6. **Install the Python script:**
   Make the script executable and copy it to the correct directories:
   ```bash
   cp decco-pi-led-hifiberry.py /usr/local/bin/
   chmod +x /usr/local/bin/decco-pi-led-hifiberry.py
   cp decco.lircd.conf /etc/lirc/lircd.conf.d/
   cp decco-pi-led-hifiberry.service /etc/systemd/system/decco-pi-led-hifiberry.service
   ```

7. **Reboot the Raspberry Pi:**
   Reboot to apply the GPIO configuration changes:
   ```bash
   sudo reboot
   ```

8. **Test LIRC:**
   Run the following command to test if LIRC is working:
   ```bash
   irsend SEND_ONCE decco AUX1
   ```
   If no errors occur, the IR configuration is probably correct. If you see an Input/Output error, double-check the LIRC and GPIO setup.

9. **Connect the IR LED:**

   - Now connect the IR LED, the long leg into the Pin 15, and the short leg into the ground.  For the prototype, no soldering is required.  For debugging, you can also put in a regular LED in the some holes to visually see if the IR signals are being sent.
   - Optionally, add a transistor and a resistor for longer-range IR signals.


![side view of the pi zero 2 W with a IR led inserted.](pi-side.jpeg)



10. **Set up SSH for Hifiberry communication:**
   To be able to log into the hifiberry, you need to enable SSH in the hifiberry. Then on the IR raspberry pi, generate and copy the SSH key for the current and root user, so that you can log into the hifiberry without a password:
   ```bash
   ssh-keygen
   ssh-copy-id root@<hifiberry-hostname>
   sudo ssh-keygen
   sudo ssh-copy-id root@<hifiberry-hostname>
   ```

11. **Test the Python script:**
   adjust the configuration parameters in the scipt
   Test the daemon by running the script manually:
   ```bash
   /usr/local/bin/decco-pi-led-hifiberry.py
   ```
   Also test it as root, as that is what the script runs at.
   ```bash
   sudo /usr/local/bin/decco-pi-led-hifiberry.py
   ```
   

12. **Set up the script as a systemd service:**
   Enable the script to start automatically with the system:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable decco-pi-led-hifiberry
   sudo systemctl start decco-pi-led-hifiberry
   sudo systemctl status decco-pi-led-hifiberry
   ```

### Optional Steps:
- Keep the Raspberry Pi up to date:
   ```bash
   sudo apt-get update && sudo apt-get -y upgrade
   ```
- Enable automatic software updates.

This project brings modern convenience to the Peachtree Decco amplifier, combining Raspberry Pi hardware with automation for a fully integrated audio experience.


![top view of the pi zero 2 W with a IR led inserted.](pi-top.jpeg)


## Future improvements ##

- Mount the pi, including the IR led,  inside the decco housing, to make it neater
- Add LIRC to the hifiberryOS, so that i can run both the DAC and the IR led from the same raspberry PI. This requires 