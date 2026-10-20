"""Feed raw terminal output into pyte, minus the codes pyte would misread.

Claude Code sends private CSI codes (keyboard-protocol switches like ESC[>4m, queries
like ESC[>0q and ESC[?u). pyte ignores the private prefix and would read ESC[>4m as
"underline on", so they are dropped. A sequence split across two reads is held back
until the rest arrives.
"""

import re

import pyte

PRIVATE = re.compile(r"\x1b\[[<>=][0-9;:]*[ -/]*[@-~]|\x1b\[\?[0-9;:]*u")
INCOMPLETE = re.compile(r"\x1b(\[[0-9;:<>=?]*[ -/]*)?$")


class DimScreen(pyte.Screen):
    """pyte ignores SGR 2 (faint). Track it in the otherwise unused 'blink' attribute."""

    def select_graphic_rendition(self, *attrs):
        faint = self.cursor.attrs.blink
        a, i = list(attrs) or [0], 0
        while i < len(a):
            x = a[i]
            if x in (38, 48, 58) and i + 1 < len(a):      # skip colour sub-parameters
                i += 3 if a[i + 1] == 5 else 5 if a[i + 1] == 2 else 1
                continue
            if x in (0, 22):
                faint = False
            elif x == 2:
                faint = True
            i += 1
        super().select_graphic_rendition(*attrs)
        self.cursor.attrs = self.cursor.attrs._replace(blink=faint)


class Feeder:
    def __init__(self, cols, rows):
        self.screen = DimScreen(cols, rows)
        self.stream = pyte.Stream(self.screen)
        self.carry = ""

    def feed(self, data):
        data = self.carry + data
        m = INCOMPLETE.search(data)
        if m:
            self.carry, data = data[m.start():], data[:m.start()]
        else:
            self.carry = ""
        self.stream.feed(PRIVATE.sub("", data))
