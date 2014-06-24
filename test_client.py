# test client udo connection
from expyriment import control, stimuli, io, misc
from expyriment.misc import Clock
from udp_connection import UDPConnection

# t : test connect
# q : quit client
# space : enter


control.set_develop_mode(True)
exp = control.initialize()

udp = UDPConnection()
print udp

if not udp.connect_peer("192.168.1.107"):  # 41.89.98.24
    print "error connecting to peer"
    exit()

stimuli.TextLine("connected to " + udp.peer_ip).present()

c = Clock()

while True:
    key = exp.keyboard.check()
    if key == ord("q"):
        break
    elif key == misc.constants.K_SPACE:
        text = io.TextInput().get()
        stimuli.BlankScreen().present()
        print "--> ", c.time, text
        udp.send(text)
    elif key == ord("t"):
        times = []
        for cnt in range(20):
            stimuli.TextLine("ping test " + str(cnt)).present()
            ok, time = udp.ping()
            times.append(time)
            c.wait(100)
        stimuli.BlankScreen().present()
        print times

    feedback = udp.poll()
    if feedback is not None:
        print "<-- ", c.time,  feedback

udp.unconnect_peer()
