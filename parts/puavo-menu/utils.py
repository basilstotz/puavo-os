# PuavoMenu miscellaneous utility functions

import gtk
from math import radians


# Draws an arbitrarily-sized red "X" placeholder icon
def draw_red_X(ctx, x, y, w, h):
    # https://www.cairographics.org/FAQ/#sharp_lines
    ctx.save()
    ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
    ctx.rectangle(x + 0.5, y + 0.5, w - 1, h - 1)
    ctx.fill_preserve()
    ctx.set_source_rgba(1.0, 0.0, 0.0, 1.0)
    ctx.move_to(x + 0.5, y + 0.5)
    ctx.line_to(x + w - 0.5, y + h - 0.5)
    ctx.move_to(x + 0.5, y + h - 0.5)
    ctx.line_to(x + w - 0.5, y + 0.5)
    ctx.set_line_width(1)
    ctx.stroke()
    ctx.restore()


# Creates a path with rounded corners. You must stroke/fill the path yourself.
def rounded_rectangle(ctx, x, y, w, h, r=20):
    # see https://www.cairographics.org/samples/rounded_rectangle/
    if r < 1:
        ctx.rectangle(x, y, w, h)
    else:
        ctx.arc(x + w - r, y + r, r, radians(-90.0), radians(0.0))
        ctx.arc(x + w - r, y + h - r, r, radians(0.0), radians(90.0))
        ctx.arc(x + r, y + h - r, r, radians(90.0), radians(180.0))
        ctx.arc(x + r, y + r, r, radians(180.0), radians(270.0))


# Simple class for drawing horizontal or vertical separator lines, with custom colors
class SeparatorLine(gtk.DrawingArea):
    def __init__(self, orientation=gtk.ORIENTATION_HORIZONTAL):
        super(SeparatorLine, self).__init__()
        self.__orientation = orientation
        self.set_size_request(50, 50)
        self.connect("expose-event", self.expose)

    def expose(self, widget, event):
        cr = widget.window.cairo_create()

        style = self.get_style()
        state = gtk.STATE_NORMAL

        cr.set_source_rgba(style.dark[state].red_float, style.dark[state].green_float,
            style.dark[state].blue_float, 1.0)

        cr.set_line_width(1)

        if self.__orientation == gtk.ORIENTATION_HORIZONTAL:
            cr.move_to(0, 0.5)
            cr.line_to(self.allocation.width, 0.5)
        else:
            cr.move_to(0.5, 0)
            cr.line_to(0.5, self.allocation.height)

        cr.stroke()
