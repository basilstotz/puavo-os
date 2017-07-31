# PuavoMenu avatar button, for easy access to the user's profile

import os.path
import gtk
import cairo
import gobject
import pango

import utils


# gtk.Label can't easily receive click events, so we have to derive this
# from gtk.Button
class AvatarButton(gtk.Button):
    """User avatar and username button"""
    def __init__(self, width, avatar_size, avatar_path="", user_name=""):
        gtk.Button.__init__(self)
        self.set_size_request(width, avatar_size)
        self.__avatar = None
        self.__avatar_size = avatar_size
        self.__avatar_path = avatar_path
        self.__username = user_name if len(user_name) > 0 else "J. Random Hacker"
        self.__hover = False
        self.__layout = None
        self.connect("enter-notify-event", self.enter)
        self.connect("leave-notify-event", self.leave)
        self.__create_layout()
        self.__load_avatar(avatar_path)

    # Creates the Pango text layout handler when the username changes
    def __create_layout(self):
        if self.__layout:
            self.__layout = None

        self.__layout = self.create_pango_layout(self.__username)
        self.__layout.set_alignment(pango.ALIGN_LEFT)
        self.__layout.set_font_description(pango.FontDescription("Ubuntu 12"))

    # Loads and resizes the avatar icon
    def __load_avatar(self, path):
        self.__avatar = None

        try:
            if not os.path.isfile(path):
                raise RuntimeError("file not found")

            buf = gtk.gdk.pixbuf_new_from_file(path)
            print('Loaded avatar image "{0}", {1}x{2} pixels'.format(
                path, buf.get_width(), buf.get_height()))

            if buf.get_width() != self.__avatar_size or buf.get_height() != self.__avatar_size:
                buf = buf.scale_simple(self.__avatar_size, self.__avatar_size,
                    gtk.gdk.INTERP_BILINEAR)

            self.__avatar = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                self.__avatar_size, self.__avatar_size)
            ctx = cairo.Context(self.__avatar)
            gdkcr = gtk.gdk.CairoContext(ctx)
            gdkcr.set_source_pixbuf(buf, 0, 0)
            gdkcr.paint()
        except Exception as e:
            print('ERROR: Could not load avatar image "{0}": {1}'.format(path, str(e)))
            self.__avatar = None

    # Get the username
    @property
    def name(self):
        return self.__username

    # Change the displayed username
    @name.setter
    def name(self, name):
        if self.__username != name:
            self.__username = name
            self.__create_layout()
            self.queue_draw()

    # Get the avatar path
    @property
    def avatar(self):
        return self.__avatar_path

    # Change the displayed avatar
    @avatar.setter
    def avatar(self, avatar_path):
        if self.__avatar_path != avatar_path:
            self.__avatar_path = avatar_path
            self.__load_avatar(avatar_path)
            self.queue_draw()

    def enter(self, widget, event):
        self.__hover = True

    def leave(self, widget, event):
        self.__hover = False

    def do_expose_event(self, event):
        try:
            x = self.allocation.x
            y = self.allocation.y

            cr = self.window.cairo_create()

            # get foreground and background colors from the theme
            style = self.get_style()
            #state = gtk.STATE_NORMAL
            state = gtk.STATE_SELECTED if self.__hover else gtk.STATE_NORMAL

            if self.__hover:
                cr.set_source_rgba(style.bg[state].red_float, style.bg[state].green_float,
                    style.bg[state].blue_float, 1.0)
                cr.rectangle(x, y, self.allocation.width, self.allocation.height)
                cr.fill()

            # avatar
            if self.__avatar:
                cr.set_source_surface(self.__avatar, x, y)
                cr.rectangle(x, y, self.__avatar_size, self.__avatar_size)
                cr.fill()
            else:
                # TODO: this looks ugly, display some "default" image instead
                utils.draw_red_X(cr, x, y, self.__avatar_size, self.__avatar_size)

            # username
            self.__layout.set_width(pango.SCALE * self.allocation.width)

            attr = pango.AttrList()
            attr.insert(pango.AttrForeground(style.fg[state].red,
                style.fg[state].green, style.fg[state].blue, 0, -1))
            self.__layout.set_attributes(attr)

            (tw, th) = self.__layout.get_pixel_size()

            # center the name vertically
            self.window.draw_layout(style.fg_gc[state],
                x + self.__avatar_size + 10,
                y + self.__avatar_size / 2 - (th / 2),
                self.__layout)
        except Exception as e:
            print('ERROR: Could not draw the avatar button: {0}'.format(str(e)))

        return False


gobject.type_register(AvatarButton)
