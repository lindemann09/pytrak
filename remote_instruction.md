#programming instruction for remote control with pytrak

System settings default values:
Remote instructions
===================

* measurement rate: 80 Hz
* maximum range: 36 inches
* report rate of the data: 1 (every data byte is reported)
* power line frequency: 60 Hz
* metric data reporting: 1 (coordinates in mm)

pytrak expects at the beginning of your experiment (if you use remote control) 
a specification of your desired TrakSTAR system settings.

If you wish to use the default values (or once you've changed what you wanted to), 
simply send the string "done".

You can set a parameter by sending its name, followed by a colon, 
followed by the value to be set.

These are your options:
"filename: <str>"
"measurement: <int>" (legal values between 20 and 255)
"maximum: <int>" (legal values are 36, 72, 144)
"report: <int>" (legal values between 1 and 127)
"power: <int>" (legal values are 50 and 60)
"metric: <int>" (legal values are 0 or 1)

e.g.
```
UDPConnection().send("filename: test")
UDPConnection().send("maximum range: 72")
UDPConnection().send("done")
```

note that it is not important if you call the parameter for better code readability "maximum range",
as long as it begins with the string "maximum" and has a colon before the value.

pytrak sends you the string "confirm" once it has received the "done" input
retrieve it via UDPConnection().poll()

To start recording, you have to send to pytrak the string "start" 
UDPConnection().send("start")
pytrak will send "confirm" again once it has started.

To quit recording, you have to send to pytrak the string "quit"
UDPConnection().send("quit")

to toggle pause 
UDPConnection().send("toggle_pause")
