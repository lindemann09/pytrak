from time import strftime
from expyriment import stimuli
from .__init__ import __version__

class RecordingScreen(object):
    def __init__(self, window_size, filename):
        """Expyriment has to be intialized"""
        margin = 50
        self.left = -1*window_size[0]/2 + margin
        self.right = window_size[0]/2 - margin
        self.top = window_size[1]/2 - margin
        self.bottom = -1*window_size[1]/2 + margin

        self.elements = []
        self.add_text_line_left("PyTrak v" + str(__version__),
                                [self.left, self.top])
        self.add_text_line_left("p: pause/unpause", [self.left, self.bottom])
        self.add_text_line_left("space: set marker", [self.left + 150, self.bottom])
        self.add_text_line_left("up/down: de/increase plot scaling",
                                [self.left + 300, self.bottom])
        self.add_text_line_left("n: normalize plotting",
                                [self.left + 550, self.bottom])
        self.add_text_line_right("q: quit recording", [self.right, self.bottom])
        self.add_text_line_centered("filename: " + filename,
                                    [0, self.top])
        self.add_text_line_right("date: {0}".format(strftime("%d/%m/%Y")),
                                [self.right, self.top])

    @staticmethod
    def _text_line(text, position, text_size=15, text_colour=(255, 150, 50)):
        """helper function"""
        return stimuli.TextLine(text, position=position,
                                text_size=text_size,
                                text_colour=text_colour)

    def add_text_line_centered(self, text, position, text_size=15,
                               text_colour=(255, 150, 50)):
        self.elements.append(RecordingScreen._text_line(text, position,
                                                       text_size,
                                                       text_colour))

    def add_text_line_right(self, text, position, text_size=15,
                            text_colour=(255, 150, 50)):
        """text_line right aligned"""
        txt = RecordingScreen._text_line(text, position, text_size,
                                        text_colour)
        txt.move((-1 * (txt.surface_size[0] / 2), 0))
        self.elements.append(txt)

    def add_text_line_left(self, text, position, text_size=15,
                           text_colour=(255, 150, 50)):
        """text line left aligned"""
        txt = RecordingScreen._text_line(text, position, text_size,
                                        text_colour)
        txt.move((txt.surface_size[0] / 2, 0))
        self.elements.append(txt)

    def stimulus(self, infotext=""):
        """Return the stimulus including infotext (obligatory)"""
        canvas = stimuli.BlankScreen()
        for elem in self.elements:
            elem.plot(canvas)
        if len(infotext) > 0:
            RecordingScreen._text_line(text=infotext, position=[0, 0],
                                      text_size=36).plot(canvas)
        return canvas
