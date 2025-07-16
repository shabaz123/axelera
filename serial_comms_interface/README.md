# Serial Comms Interface

## Installation
Copy the SerialComms.py file to your machine

## Standalone Operation
Type the following to send any arbitrary command:

```
python SerialComms.py "MY COMMAND TEXT"
```

## Embedded in Software
You can pull in the serial comms code into your own Python code, by simply ensuring the SerialComms.py file is in the same folder as your own code, and adding this to your code:

```
from SerialComms import SerialComms
comms = SerialComms()
comms.send("MY COMMAND TEXT")
```
