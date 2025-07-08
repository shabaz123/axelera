# Using a RTL8822CE M.2 2.4/5 GHz WiFi Card
The RTL8822CE WLAN card supports both 2.4 GHz and 5 GHz wireless networks.

# Installing the Card
Take electrostatic discharge precautions, by touching an earthed conductor.

Ensure the antenna cables are attached to the WLAN card. If they are not, watch a YouTube video to try to see how to do it, or consider taking the WLAN card to a laptop repair store to ask them to perform the task.

With the Axelera Eval System powered off and unplugged, remove the screw which holds the M.2 card in position usually.

Insert the card on the underside. It should insert at an angle of about 30 degrees, and then when fully inserted, gently flatten it down to zero degrees with almost no pressure needed.

Now replace the screw, or, screw in the hex standoff that was supplied with the Axelera kit in a small plastic bag. If you use the standoff, you can later insert an M.2 solid-state drive (SSD) too if desired. Don't lose the screw because it will be required for that!
Now you can power on the Axelera Eval System.

# Enable the RTL8822CE Driver and Firmware
Next, perform the following steps in a temporary folder on the machine:

``sudo depmod -a``

``sudo mkdir -p /lib/firmware/rtw88``

``wget https://github.com/shabaz123/axelera/raw/refs/heads/main/rtw88/rtw8822c_fw.bin``

``wget https://github.com/shabaz123/axelera/raw/refs/heads/main/rtw88/rtw8822c_wow_fw.bin``

``sudo mv rtw88*.bin /lib/firmware/rtw88``

``sudo modprobe rtw88_8822ce``

``ifconfig -a``

That last **ifconfig -a** command should reveal a WLAN interface. Mine was listed as follows:

``wlP2p33s0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500``

Now make that interface permanent:

``echo rtw88_8822ce | sudo tee -a /etc/modules``

Reboot (by typing sudo reboot) and then retry the ifconfig -a command to confirm the interface is still there!

# Using the Driver

Type **nmcli radio wifi** and the output should indicate 'enabled'. Next, type **sudo nmcli radio wifi on** and then after a few seconds, type **nmcli dev wifi list** to see a list of SSIDs. 

To connect to an SSID, type the following:

`sudo nmcli dev wifi connect MY_SSID password "MY_PASSWORD"`

where MY_SSID is the SSID name, and MY_PASSWORD is the password (enclose it in speech-marks) as shown above.

# Check you are connected to a Wireless Network

Type **ifconfig -a** and at the wlxxxxxxxxxxxxx entry, in the second line, you should see an IP address, such as:

`inet 192.168.1.85 netmask 255.255.255.0 broadcast 192.168.1.255`

Alternatively, you may see a line such as:

`inet6 fe80::xxxx:xxxx:xxxx:xxxx prefixlen 65 scopeid 0x20<link>`

If you don't see either of those lines, then there's either an issue with the wireless connection, or the router has not assigned an IP address to your network interface for some reason.

If the above was successful, then you can disconnect your Ethernet connection, and then try **ping www.bbc.co.uk** and see if you get ping successes!



# Firmware note
Just for informational purposes, the two files that were used can alternatively be obtained by typing: 

``git clone https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git``

``cd linux-firmware/rtw88 ``
 
And you'll find the files present there. However, you'll need lots of disk space for the clone operation, so don't do it on the target system if you've just got a small amount of Flash memory.


