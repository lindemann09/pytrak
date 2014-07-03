# # Server
import time

from trakstar import UDPConnection


udp = UDPConnection()
print udp

while True:
    data = udp.poll()
    if data in [udp.CONNECT, udp.UNCONNECT]:
        print time.time(), data
        print udp
    elif data == udp.PING:
        print time.time(), data
    elif data is not None:
        udp.send(data)
