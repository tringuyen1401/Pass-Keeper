# Pass-Keeper
A vault to store the password and can type it out when connected to a computer


The initial plan was to have a physical storage for the password which only types passwords 
by receiving texts from authorized phone number using:
1) a Raspberry Pi Zero 
2) pass: https://github.com/girst/hardpass-sendHID
3) Duckberry Pi: https://www.reddit.com/r/raspberry_pi/comments/46ikup/duckberry_pi_keyboard_emulator_and_automator_on_a/
4) A online phone number (Twilio is an example)

However, I later discovered that since Raspberry Pi Zero only have 1 OTG ports that cannot both
serve as a host port (for wifi dongle to get updates from the database) and as HID keyboard (to type
the password to the PC). Thus, I have to make some changes and make the smshandler.py dump the 
request info to root file and then process locally everytime the system is not in host mode (which means
it is now a HID keyboard). This means it will type out the latest password requested. You can change
the stored password by texting to the server, and connect the wifi dongle to the OTG port.

Another option is to set a sleep time after you have update the request and plug it right in to the
PC though this way may cause more hassle than the benefit

The program can, however, be easily configured back to the original model should I find another device
that has 2 OTG ports and is as small as the Zero.




