"""Render a pyte screen to a Pillow image, the way a dark VS Code terminal would."""

from PIL import Image, ImageDraw, ImageFont

FONTS = r"C:\Windows\Fonts"
DEFAULT_FG = (204, 204, 204)
DEFAULT_BG = (30, 30, 30)
PALETTE = {  # VS Code Dark+ terminal colours
    "black": (0, 0, 0), "red": (205, 49, 49), "green": (13, 188, 121),
    "brown": (229, 229, 16), "yellow": (229, 229, 16), "blue": (36, 114, 200),
    "magenta": (188, 63, 188), "cyan": (17, 168, 205), "white": (229, 229, 229),
    "brightblack": (102, 102, 102), "brightred": (241, 76, 76), "brightgreen": (35, 209, 139),
    "brightbrown": (245, 245, 67), "brightyellow": (245, 245, 67), "brightblue": (59, 142, 234),
    "brightmagenta": (214, 112, 214), "brightcyan": (41, 184, 219), "brightwhite": (255, 255, 255),
}
# Block elements drawn as exact quadrants: (upper-left, upper-right, lower-left, lower-right)
QUADS = {
    "█": (1, 1, 1, 1), "▀": (1, 1, 0, 0), "▄": (0, 0, 1, 1), "▌": (1, 0, 1, 0), "▐": (0, 1, 0, 1),
    "▘": (1, 0, 0, 0), "▝": (0, 1, 0, 0), "▖": (0, 0, 1, 0), "▗": (0, 0, 0, 1),
    "▛": (1, 1, 1, 0), "▜": (1, 1, 0, 1), "▙": (1, 0, 1, 1), "▟": (0, 1, 1, 1),
    "▚": (1, 0, 0, 1), "▞": (0, 1, 1, 0),
}
# Box drawing as segments from the cell centre: (left, right, up, down)
BOX = {
    "─": (1, 1, 0, 0), "━": (1, 1, 0, 0), "│": (0, 0, 1, 1), "┃": (0, 0, 1, 1),
    "┌": (0, 1, 0, 1), "╭": (0, 1, 0, 1), "┐": (1, 0, 0, 1), "╮": (1, 0, 0, 1),
    "└": (0, 1, 1, 0), "╰": (0, 1, 1, 0), "┘": (1, 0, 1, 0), "╯": (1, 0, 1, 0),
    "├": (0, 1, 1, 1), "┤": (1, 0, 1, 1), "┬": (1, 1, 0, 1), "┴": (1, 1, 1, 0), "┼": (1, 1, 1, 1),
}


def colour(value, default):
    if value == "default":
        return default
    if isinstance(value, str) and len(value) == 6:
        try:
            return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            pass
    return PALETTE.get(value, default)


class TermRenderer:
    def __init__(self, cols, rows, size):
        self.cols, self.rows = cols, rows
        self.reg = ImageFont.truetype(rf"{FONTS}\consola.ttf", size)
        self.bold = ImageFont.truetype(rf"{FONTS}\consolab.ttf", size)
        self.ital = ImageFont.truetype(rf"{FONTS}\consolai.ttf", size)
        self.sym = ImageFont.truetype(rf"{FONTS}\seguisym.ttf", int(size * 0.92))
        self.emoji = ImageFont.truetype(rf"{FONTS}\seguiemj.ttf", int(size * 0.85))
        self.cw = round(self.reg.getlength("M"))
        asc, desc = self.reg.getmetrics()
        self.ch = asc + desc + 2
        self.base = 1
        self.width, self.height = cols * self.cw, rows * self.ch
        self._missing = self._mask(self.reg, "\ue000")
        self._has = {}

    @staticmethod
    def _mask(font, ch):
        m = font.getmask(ch)
        return (m.size, bytes(m))

    def _font_for(self, ch, cell):
        if ord(ch) < 128:
            return self.bold if cell.bold else (self.ital if cell.italics else self.reg)
        if ch not in self._has:
            self._has[ch] = self._mask(self.reg, ch) != self._missing
        if self._has[ch]:
            return self.bold if cell.bold else self.reg
        return self.emoji if ord(ch) >= 0x1F000 else self.sym

    def render(self, screen):
        img = Image.new("RGB", (self.width, self.height), DEFAULT_BG)
        d = ImageDraw.Draw(img)
        cw, ch = self.cw, self.ch
        for y in range(self.rows):
            line = screen.buffer[y]
            x = 0
            while x < self.cols:
                cell = line[x]
                fg = colour(cell.fg, DEFAULT_FG)
                bg = colour(cell.bg, DEFAULT_BG)
                if cell.reverse:
                    fg, bg = bg, fg
                if cell.blink:  # faint text (see feed.DimScreen)
                    fg = tuple((f + b) // 2 for f, b in zip(fg, bg))
                px, py = x * cw, y * ch
                wide = x + 1 < self.cols and line[x + 1].data == "" and cell.data not in ("", " ")
                span = 2 if wide else 1
                if bg != DEFAULT_BG:
                    d.rectangle([px, py, px + cw * span - 1, py + ch - 1], fill=bg)
                c = cell.data
                if c and c != " " and c != "\xa0":
                    if c in QUADS:
                        ul, ur, ll, lr = QUADS[c]
                        hx, hy = cw // 2, ch // 2
                        for on, box in ((ul, (0, 0, hx, hy)), (ur, (hx, 0, cw, hy)),
                                        (ll, (0, hy, hx, ch)), (lr, (hx, hy, cw, ch))):
                            if on:
                                d.rectangle([px + box[0], py + box[1], px + box[2] - 1, py + box[3] - 1], fill=fg)
                    elif c in BOX:
                        left, right, up, down = BOX[c]
                        cx, cy, t = px + cw // 2, py + ch // 2, 2 if c in "━┃" else 1
                        if left:
                            d.rectangle([px, cy, cx, cy + t - 1], fill=fg)
                        if right:
                            d.rectangle([cx, cy, px + cw - 1, cy + t - 1], fill=fg)
                        if up:
                            d.rectangle([cx, py, cx + t - 1, cy], fill=fg)
                        if down:
                            d.rectangle([cx, cy, cx + t - 1, py + ch - 1], fill=fg)
                    else:
                        font = self._font_for(c, cell)
                        if font is self.reg or font is self.bold or font is self.ital:
                            d.text((px, py + self.base), c, font=font, fill=fg)
                        else:  # centre symbol-font glyphs in their cell(s)
                            w = font.getlength(c)
                            d.text((px + (cw * span - w) / 2, py + self.base + 1), c, font=font, fill=fg,
                                   embedded_color=font is self.emoji)
                    if cell.underscore:
                        d.line([px, py + ch - 3, px + cw * span - 1, py + ch - 3], fill=fg)
                x += span
        return img
