# Serial Comms Interface

## Installation
Copy the SerialComms.py file to your machine

## Standalone Operation
Type the following to send any arbitrary command:

```
python SerialComms.py "MY COMMAND TEXT"
```

## Embedded in Software
You can use the code from within other Python code, by adding this to your code:

```
from SerialComms import SerialComms
comms = SerialComms()
comms.send("MY COMMAND TEXT")
```
