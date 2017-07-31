# PuavoMenu icon caching

import os.path
import gtk
import cairo

import utils


# TODO: actually support multiple surfaces
class IconCache(object):
    """Class for caching idencitally-sized icons efficiently. It's better to have a few large
    bitmaps in memory than dozens or even hundreds of smaller ones. Currently supported icon
    sizes are 32x32 and 48x48. The dimensions of the memory bitmap can be specified."""
    def __init__(self, icon_size, bitmap_size=512):
        if icon_size not in (32, 48):
            raise RuntimeError("Icon cache icon size must be either 32 or 48, {0} is not valid".
                format(icon_size))

        if bitmap_size < 128 or bitmap_size > 1024:
            raise RuntimeError("Icon cache surface dimensions must be between 128-1024, {0} is not valid".
                format(bitmap_size))

        self.__icon_size = icon_size
        self.__bitmap_size = bitmap_size
        self.__lookup = {}
        self.__surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.__bitmap_size, self.__bitmap_size)
        self.__ctx = cairo.Context(self.__surface)
        self.__atlas_num = 0
        self.__x = 0
        self.__y = 0

        # Fill the surface with nothingness, even the alpha channel, so we can blit from it
        # without messing up whatever's already behind the icon
        self.__ctx.save()
        self.__ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.__ctx.rectangle(0, 0, self.__bitmap_size, self.__bitmap_size)
        self.__ctx.paint()
        self.__ctx.restore()

    # purely for debugging!
    def save(self, name):
        return self.__surface.write_to_png(name)

    # Loads a new icon if it hasn't been loaded yet. Always returns
    # a valid icon handle.
    def load_icon(self, path):
        if path in self.__lookup:
            return self.__lookup[path]

        status, atlas_num, x, y = True, self.__atlas_num, self.__x, self.__y

        try:
            if not os.path.isfile(path):
                raise RuntimeError("file not found")

            if os.path.splitext(path)[1] not in (".png"):
                raise RuntimeError("only PNG images can be loaded")

            icon = cairo.ImageSurface.create_from_png(path)
            icon_w = icon.get_width()
            icon_h = icon.get_height()

            if icon_w != self.__icon_size or icon_h != self.__icon_size:
                # TODO: There has to be a better and faster way to do this
                # print('WARNING: Resizing image "{0}" from {1}x{2} to {3}x{3}'.format(
                #    path, icon_w, icon_h, self.__icon_size, self.__icon_size))

                scaler = cairo.Matrix()
                scaler.scale(float(icon_w) / float(self.__icon_size),
                    float(icon_h) / float(self.__icon_size))

                pattern = cairo.SurfacePattern(icon)
                pattern.set_matrix(scaler)
                pattern.set_filter(cairo.FILTER_BILINEAR)

                canvas = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.__icon_size, self.__icon_size)
                ctx = cairo.Context(canvas)
                ctx.set_source(pattern)
                ctx.paint()

                icon = canvas

            if (self.__y + self.__icon_size) > self.__bitmap_size:
                ### TODO: Create another atlas surface
                raise RuntimeError("the icon cache (icon_size={0}, bitmap_size={1}) is full!".
                    format(self.__icon_size, self.__bitmap_size))

            self.__ctx.set_source_surface(icon, x, y)
            self.__ctx.paint()

            # compute the position for the next icon
            self.__x += self.__icon_size

            if (self.__x + self.__icon_size) > self.__bitmap_size:
                self.__x = 0
                self.__y += self.__icon_size

            self.__lookup[path] = (True, atlas_num, x, y)

            #print('Loaded icon "{0}": atlas={1}, x={2}, y={3}, icon_size={4}'.format(
            #    path, atlas_num, x, y, self.__icon_size))
        except Exception as e:
            msg = str(e)

            if msg == "":
                msg = "<The exception has no message>"

            print('ERROR: Could not load icon "{0}": {1}'.format(path, msg))
            status = False

        return status, atlas_num, x, y

    # overload [] for easier access
    def __getitem__(self, path):
        return self.load_icon(path)

    # Draws the specified icon onto the context at the specified coordinates
    def draw_icon(self, ctx, icon, x, y):
        if (icon is None) or (not icon[0]):
            # draw a red "X" to indicate a broken/missing icon
            utils.draw_red_X(ctx, x, y, self.__icon_size, self.__icon_size)
        else:
            # https://www.cairographics.org/FAQ/#paint_from_a_surface
            ctx.set_source_surface(self.__surface, x - icon[2], y - icon[3])
            ctx.rectangle(x, y, self.__icon_size, self.__icon_size)
            ctx.fill()


icons32 = IconCache(icon_size=32, bitmap_size=128)
icons48 = IconCache(icon_size=48, bitmap_size=48 * 12)
