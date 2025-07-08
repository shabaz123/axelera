# Firmware for RTL8822CE WLAN cards
To  use, create a folder called **rtw88** in your **/ib/firmware** directory on your target machine, and then copy the two .bin files into **/lib/firmware/rtw88**

Note: the two files can also be obtained by typing: 

``git clone https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git``

``cd linux-firmware/rtw88 ``
 
And you'll find the files present there. However, you'll need lots of disk space for the clone operation, so don't do it on the target system if you've just got a small amount of Flash memory.


