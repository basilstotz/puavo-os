# PuavoMenu buttons
# -*- coding: utf-8 -*-

import gtk
import cairo
import pango
import gobject

import iconcache
import utils

# Size of a program button. Changing this shouldn't break anything... in theory.
PROGRAM_BUTTON_WIDTH = 150
PROGRAM_BUTTON_HEIGHT = 110
PROGRAM_BUTTON_CORNER_ROUNDING = 5

PROGRAM_BUTTON_TITLE_FONT = "Ubuntu 9"
PROGRAM_FONT_DESCRIPTOR = pango.FontDescription(PROGRAM_BUTTON_TITLE_FONT)

SYSTEM_BUTTON_TITLE_FONT = "Ubuntu 10"
SYSTEM_FONT_DESCRIPTOR = pango.FontDescription(SYSTEM_BUTTON_TITLE_FONT)

# The width and height of all icons. Again, changing this without resizing the windows
# is a bad idea.
PROGRAM_ICON_SIZE = 48

# Icon's position inside the button
PROGRAM_ICON_X = (PROGRAM_BUTTON_WIDTH / 2) - (PROGRAM_ICON_SIZE / 2)
PROGRAM_ICON_Y = 20

# "System" buttons on the sidebar
SYSTEM_BUTTON_ICON_SIZE = 32
SYSTEM_BUTTON_HEIGHT = 40
SYSTEM_BUTTON_CORNER_ROUNDING = 3
SYSTEM_BUTTON_ICON_X = 10
SYSTEM_BUTTON_ICON_Y = (SYSTEM_BUTTON_HEIGHT / 2) - (SYSTEM_BUTTON_ICON_SIZE / 2)
SYSTEM_BUTTON_LABEL_X = SYSTEM_BUTTON_ICON_X + SYSTEM_BUTTON_ICON_SIZE + 10


class MenuButton(gtk.Button):
    def __init__(self, parent, label, icon, tooltip=None, background=None):
        gtk.Button.__init__(self)
        self.set_size_request(PROGRAM_BUTTON_WIDTH, PROGRAM_BUTTON_HEIGHT)
        self.set_label(label)
        self.__icon = icon

        if tooltip:
            self.set_property("tooltip-text", tooltip)

        self.__background = background
        self.__hover = False

        self.connect("enter-notify-event", self.enter)
        self.connect("leave-notify-event", self.leave)

        self.__layout = self.create_pango_layout(label)
        self.__layout.set_alignment(pango.ALIGN_CENTER)
        self.__layout.set_font_description(PROGRAM_FONT_DESCRIPTOR)

    def enter(self, widget, event):
        self.__hover = True
        return False

    def leave(self, widget, event):
        self.__hover = False
        return False

    def do_expose_event(self, event):
        try:
            x = self.allocation.x
            y = self.allocation.y
            w = self.allocation.width
            h = self.allocation.height

            cr = self.window.cairo_create()

            # get foreground and background colors from the theme
            style = self.get_style()
            state = gtk.STATE_SELECTED if self.__hover else gtk.STATE_NORMAL
            gc = self.get_style()

            # hover rectagle
            if self.__hover:
                cr.set_source_rgba(style.bg[state].red_float, style.bg[state].green_float,
                    style.bg[state].blue_float, 1.0)
                utils.rounded_rectangle(cr, x, y, w, h, PROGRAM_BUTTON_CORNER_ROUNDING)
                cr.fill()

            # background image (DANGER: HARDCODED SIZE!)
            if self.__background:
                cr.set_source_surface(self.__background, x, y)
                cr.rectangle(x, y, 150, 110)
                cr.fill()

            iconcache.icons48.draw_icon(cr, self.__icon, x + PROGRAM_ICON_X, y + PROGRAM_ICON_Y + 5)

            self.__layout.set_width(pango.SCALE * w)

            attr = pango.AttrList()
            attr.insert(pango.AttrForeground(style.fg[gtk.STATE_NORMAL].red,
                style.fg[gtk.STATE_NORMAL].green, style.fg[gtk.STATE_NORMAL].blue, 0, -1))
            self.__layout.set_attributes(attr)

            self.window.draw_layout(style.fg_gc[state], x,
                y + PROGRAM_ICON_Y + PROGRAM_ICON_SIZE + 10, self.__layout)
        except Exception as e:
            print('ERROR: Could not draw a ProgramButton: {0}'.format(str(e)))

        return False


class ProgramButton(gtk.Button):
    def __init__(self, parent, id, label, icon, tooltip=None, is_fave=False):
        gtk.Button.__init__(self)
        self.set_size_request(PROGRAM_BUTTON_WIDTH, PROGRAM_BUTTON_HEIGHT)
        self.set_label(label)
        self.__parent = parent
        self.__id = id      # the popup menu item callback functions need the program ID
        self.__icon = icon

        if tooltip:
            self.set_property("tooltip-text", tooltip)

        self.__is_fave = is_fave

        self.__hover = False
        self.__menu_open = False

        self.connect("enter-notify-event", self.enter)
        self.connect("leave-notify-event", self.leave)
        self.connect("button-press-event", self.open_menu)

        self.__layout = self.create_pango_layout(label)
        self.__layout.set_alignment(pango.ALIGN_CENTER)
        self.__layout.set_font_description(PROGRAM_FONT_DESCRIPTOR)

        self.__menu = None

    def enter(self, widget, event):
        self.__hover = True
        self.__menu_open = False
        return False

    def leave(self, widget, event):
        self.__hover = False
        return False

    # Open the right-click menu
    def open_menu(self, widget, event):
        if event.button == 3:
            self.__menu = gtk.Menu()
            self.__menu.connect("deactivate", self.__cancel_menu)
            desktop_item = gtk.MenuItem("Add to desktop")
            desktop_item.connect("activate", self.__add_me_to_the_desktop)
            desktop_item.show()
            self.__menu.append(desktop_item)
            panel_item = gtk.MenuItem("Add to panel")
            panel_item.connect("activate", self.add_me_to_the_panel)
            panel_item.show()
            self.__menu.append(panel_item)

            if self.__is_fave:
                remove_fave = gtk.MenuItem("Remove from favorites")
                remove_fave.connect("activate", self.remove_me_from_faves)
                remove_fave.show()
                self.__menu.append(remove_fave)

            self.__menu_open = True
            self.__menu.popup(None, None, None, event.button, event.time)

    # Nothing in the popup menu was clicked
    def __cancel_menu(self, menushell):
        self.__menu_open = False
        self.__menu = None

    # "Add to desktop" popup menu item
    def __add_me_to_the_desktop(self, item):
        self.__parent.add_program_to_desktop(self.__id)
        self.__menu_open = False
        self.__menu = None

    # "Add to panel" popup menu item
    def add_me_to_the_panel(self, item):
        self.__parent.add_program_to_panel(self.__id)
        self.__menu_open = False
        self.__menu = None

    # "Remove from favorites" popup menu item
    def remove_me_from_faves(self, item):
        self.__parent.remove_from_faves(self.__id)
        self.__menu_open = False
        self.__menu = None

    def do_expose_event(self, event):
        try:
            x = self.allocation.x
            y = self.allocation.y
            w = self.allocation.width
            h = self.allocation.height

            cr = self.window.cairo_create()

            is_hovered = self.__hover or self.__menu_open

            # get foreground and background colors from the theme
            style = self.get_style()
            state = gtk.STATE_SELECTED if is_hovered else gtk.STATE_NORMAL
            gc = self.get_style()

            # hover rectagle
            if is_hovered:
                cr.set_source_rgba(style.bg[state].red_float, style.bg[state].green_float,
                    style.bg[state].blue_float, 1.0)
                utils.rounded_rectangle(cr, x, y, w, h, PROGRAM_BUTTON_CORNER_ROUNDING)
                cr.fill()

            iconcache.icons48.draw_icon(cr, self.__icon, x + PROGRAM_ICON_X, y + PROGRAM_ICON_Y)

            self.__layout.set_width(pango.SCALE * w)

            attr = pango.AttrList()
            attr.insert(pango.AttrForeground(style.fg[state].red,
                style.fg[state].green, style.fg[state].blue, 0, -1))
            self.__layout.set_attributes(attr)

            self.window.draw_layout(style.fg_gc[state], x,
                y + PROGRAM_ICON_Y + PROGRAM_ICON_SIZE + 5, self.__layout)
        except Exception as e:
            print('ERROR: Could not draw a ProgramButton: {0}'.format(str(e)))

        return False


class SystemButton(gtk.Button):
    def __init__(self, parent, width, label, icon, tooltip=None):
        gtk.Button.__init__(self)
        self.set_size_request(width, SYSTEM_BUTTON_HEIGHT)
        self.set_label(label)
        self.__icon = icon
        self.__hover = False
        self.connect("enter-notify-event", self.enter)
        self.connect("leave-notify-event", self.leave)

        if tooltip:
            self.set_property("tooltip-text", tooltip)

        self.__layout = self.create_pango_layout(label)
        self.__layout.set_alignment(pango.ALIGN_LEFT)
        self.__layout.set_font_description(SYSTEM_FONT_DESCRIPTOR)

    def enter(self, widget, event):
        self.__hover = True
        return False

    def leave(self, widget, event):
        self.__hover = False
        return False

    def do_expose_event(self, event):
        try:
            x = self.allocation.x
            y = self.allocation.y
            w = self.allocation.width
            h = self.allocation.height

            cr = self.window.cairo_create()

            # get foreground and background colors from the theme
            style = self.get_style()
            state = gtk.STATE_SELECTED if self.__hover else gtk.STATE_NORMAL
            gc = self.get_style()

            if self.__hover:
                cr.set_source_rgba(style.bg[state].red_float, style.bg[state].green_float,
                    style.bg[state].blue_float, 1.0)
                utils.rounded_rectangle(cr, x, y, w, h, SYSTEM_BUTTON_CORNER_ROUNDING)
                cr.fill()

            iconcache.icons32.draw_icon(cr, self.__icon,
                x + SYSTEM_BUTTON_ICON_X,
                y + SYSTEM_BUTTON_ICON_Y)

            self.__layout.set_alignment(pango.ALIGN_LEFT)
            self.__layout.set_width(pango.SCALE * w)

            attr = pango.AttrList()
            attr.insert(pango.AttrForeground(style.fg[state].red,
                style.fg[state].green, style.fg[state].blue, 0, -1))
            self.__layout.set_attributes(attr)

            (tw, th) = self.__layout.get_pixel_size()

            # center the label vertically
            self.window.draw_layout(style.fg_gc[state],
                x + SYSTEM_BUTTON_LABEL_X,
                y + (SYSTEM_BUTTON_HEIGHT / 2) - (th / 2),
                self.__layout)
        except Exception as e:
            print('ERROR: Could not draw a SystemButton: {0}'.format(str(e)))

        return False


gobject.type_register(MenuButton)
gobject.type_register(ProgramButton)
gobject.type_register(SystemButton)
