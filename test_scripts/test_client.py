# test client udo connection
from expyriment import control, stimuli, io, misc
from expyriment.misc import Clock
from trakstar import UDPConnection

# t : test connect
# q : quit client
# space : enter


control.set_develop_mode(True)
exp = control.initialize()

udp = UDPConnection()
print udp

if not udp.connect_peer("169.254.1.1"):  # 41.89.98.24
    print "error connecting to peer"
    exit()

stimuli.TextLine("connected to " + udp.peer_ip).present()

c = Clock()

##udp.send("maximum: 72")
##udp.send("measurement: 25")
##udp.send("filename: test")
##udp.send("report: 5")
##print "--> ", c.time, "done"
##udp.send("done")
##feedback = udp.poll()
##while feedback is None:
##    feedback = udp.poll()
##print "<-- ", c.time,  feedback
##
##print "--> ", c.time, "start"
##udp.send("start")
##feedback = udp.poll()
##while feedback is None:
##    feedback = udp.poll()
##print "<-- ", c.time,  feedback   
##c.wait(2000)
##
##print "--> ", c.time, "pause"
##udp.send("pause")
##feedback = udp.poll()
##while feedback is None:
##    feedback = udp.poll()
##print "<-- ", c.time,  feedback   
##c.wait(2000)
##
##print "--> ", c.time, "unpause"
##udp.send("unpause")
##udp.send("unpause") #for data output
##feedback = udp.poll()
##while feedback is None:
##    feedback = udp.poll()
##print "<-- ", c.time,  feedback   
##c.wait(2000)
##
##print "--> ", c.time, "quit"
##udp.send("quit")
##feedback = udp.poll()
##while feedback is None:
##    feedback = udp.poll()
##print "<-- ", c.time,  feedback   

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
            c.reset_stopwatch()
            ok, time = udp.ping()
            print c.stopwatch_time
            times.append(time)
            c.wait(100)
        stimuli.BlankScreen().present()
        print times

    feedback = udp.poll()
    if feedback is not None:
        print "<-- ", c.time,  feedback    

udp.unconnect_peer()
