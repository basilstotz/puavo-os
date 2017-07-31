# PuavoMenu YAML file parser and menu structure validator/generator

import os, os.path, time, re
from fnmatch import fnmatch
import yaml


# PyYAML seriously does not do Unicode without hacks like this
def use_utf8_please(loader, node):
    return loader.construct_scalar(node).encode('utf-8')

yaml.add_constructor(u'tag:yaml.org,2002:str', use_utf8_please)


def have_valid_string(what, where):
    return (what in where) and (type(where[what]) is str) and (len(where[what].strip()) > 0)


def have_valid_list(what, where):
    return (what in where) and (type(where[what]) is list) and (len(where[what]) > 0)


# Loads a YAML and returns programs, menus and categories listed in it. Can be used multiple
# times; if you merge the resulting dictionaries, you can overwrite earlier definitions.
# Will aggressively remove incomplete and duplicate programs, menus and categories.
def load_yaml(name):
    print('load_yaml(): loading "{0}"...'.format(name))

    programs = {}
    menus = {}
    categories = {}

    try:
        loader = yaml.Loader(open(name).read())
        data = loader.get_single_data()

        # ------------------------------------------------------------------------------------------
        # Parse programs

        for p in data.get("programs", []):
            # Expand single-line definitions into full definitions, dangerously assuming
            # everything along the way...
            if type(p) is str:
                # "type" *MUST* be "desktop" here
                p = { "id": p, "source": p, "type": "desktop" }

            if not have_valid_string("id", p):
                print("ERROR: Skipping a program with a missing or invalid ID")
                continue

            if "type" in p:
                if p["type"] not in ("desktop", "web", "custom"):
                    print('ERROR: Program "{0}" has an unknown type of "{1}", skipping'.
                        format(p["id"], p["type"]))
                    continue
            else:
                # Assume type if not specified
                p["type"] = "desktop"

            if (p["type"] == "desktop") and ("source" not in p):
                # a desktop program without source, assume the source .deskto file has the
                # same name as the ID
                p["source"] = p["id"]

            id = p["id"]

            # Verify program description, if any
            if "description" in p:
                if type(p["description"]) is str:
                    if not have_valid_string("description", p):
                        print('WARNING: Program "{0}" description is not valid, description removed'.
                            format(id))
                        del p["description"]
                elif type(p["description"]) is dict:
                    if len(p["description"]) == 0:
                        print('WARNING: Program "{0}" description is not valid, description removed'.
                            format(id))
                        del p["description"]
                else:
                    print('WARNING: Program "{0}" description is defined completely wrong'.format(id))
                    del p["description"]

            # Check custom commands
            if p["type"] == "custom":
                if not have_valid_string("command", p):
                    print('ERROR: Custom command "{0}" has no command, skipping'.format(id))
                    continue

                if "name" not in p:
                    print('WARNING: Custom command "{0}" has no name, using its ID as the name'.
                        format(id))
                    p["name"] = id

                if type(p["name"]) is str:
                    if not have_valid_string("name", p):
                        print('WARNING: Custom command "{0}" name is not valid, using its ID as the name'.
                            format(id))
                        p["name"] = id
                elif type(p["name"]) is dict:
                    if len(p["name"]) == 0:
                        print('WARNING: Custom command "{0}" name is not valid, using its ID as the name'.
                            format(id))
                        p["name"] = id
                else:
                    print('WARNING: Custom command "{0}" name is defined completely wrong'.format(id))
                    p["name"] = id

            # Check web links
            if p["type"] == "web":
                if not have_valid_string("url", p):
                    print('ERROR: Web link "{0}" has no URL, skipping'.format(id))
                    continue

                if "name" not in p:
                    print('WARNING: Web link "{0}" has no name, using its ID as the name'.format(id))
                    p["name"] = id

                if type(p["name"]) is str:
                    if not have_valid_string("name", p):
                        print('WARNING: Web link "{0}" name is not valid, using its ID as the name'.
                            format(id))
                        p["name"] = id
                elif type(p["name"]) is dict:
                    if len(p["name"]) == 0:
                        print('WARNING: Web link "{0}" name is not valid, using its ID as the name'.
                            format(id))
                        p["name"] = id
                else:
                    print('WARNING: Web link "{0}" name is defined completely wrong'.format(id))
                    p["name"] = id

            if "icon" in p:
                # Make sure it's a non-emoty string
                if not have_valid_string("icon", p):
                    print('WARNING: Icon specified for program "{0}", but the icon name is not valid, icon ignored'.
                        format(id))
                    del p["icon"]

            if id in programs:
                print('ERROR: Program "{0}" defined multiple times, ignoring dupes'.format(id))
                continue

            programs[id] = p

        # ------------------------------------------------------------------------------------------
        # Parse menus

        for m in data.get("menus", []):
            if not have_valid_string("id", m):
                print('ERROR: Skipping a menu with a missing or invalid ID')
                continue

            id = m["id"]

            if id in menus:
                print('ERROR: Menu "{0}" defined multiple times, ignoring dupes'.format(id))
                continue

            if "name" not in m:
                print('WARNING: Menu "{0}" has no name, using its ID as the name'.format(id))
                m["name"] = id

            # Silently create an empty programs list if nothing has been defined
            if "programs" not in m:
                m["programs"] = []

            if "icon" in m:
                # Make sure it's a non-emoty string
                if not have_valid_string("icon", m):
                    print('WARNING: Icon specified for menu "{0}", but the icon name is not valid, icon ignored'.
                        format(id))
                    del m["icon"]

            menus[id] = m

        # ------------------------------------------------------------------------------------------
        # Parse categories

        for i in data.get("categories", []):
            if not have_valid_string("id", i):
                print('ERROR: Skipping a category without an ID')
                continue

            id = i["id"]

            if id in categories:
                print('ERROR: Category "{0}" defined multiple times, ignoring dupes'.format(id))
                continue

            if "name" not in i:
                print('WARNING: Category "{0}" has no name, using its ID as the name'.format(id))
                i["name"] = id

            # Silently add empty menu and program lists
            if "menus" not in i:
                i["menus"] = []

            if "programs" not in i:
                i["programs"] = []

            categories[id] = i

    except Exception as e:
        print('ERROR: Could not load file "{0}": {1}'.format(name, str(e)))

    return programs, menus, categories


# Very poor .desktop file loader. Returns dicts in dicts. Not very well tested.
def load_dotdesktop_file(name):
    data = {}

    for l in open(name).readlines():
        l = l.strip()

        if (len(l) == 0) or (l[0] == '#'):      # comment or empty line
            continue

        if (l[0] == '[') and (l[-1] == ']'):    # [section]
            sect_name = l[1:-1]
            data[sect_name] = {}
            section = data[sect_name]
        else:                                   # key=value
            equals = l.find('=')

            if equals != -1:
                section[l[0:equals]] = l[equals+1:]

    return data


# Parses the specified YAML files in the order they are, loads .desktop files and
# builds the menu structure out of them.
def parse_menu_files(desktop_search_paths, icon_paths, menu_files):
    # ----------------------------------------------------------------------------------------------
    # Load the YAML files

    print("--- 1: Loading the menu YAML files ---")

    programs = {}
    menus = {}
    categories = {}

    for m in menu_files:
        p, m, c = load_yaml(m)
        programs.update(p)
        menus.update(m)
        categories.update(c)

    print("Have {0} programs, {1} menus and {2} categories".format(len(programs), len(menus),
        len(categories)))

    # ----------------------------------------------------------------------------------------------
    # Load .desktop files for desktop programs

    print("--- 2: Loading .desktop files for desktop programs ---")

    # Accepted extensions in icon files. Some .desktop file "Icon" entries specify full paths,
    # so we check if the name has an extension for distinguish these names from automatic names.
    # Remember to include the dot!
    ICON_EXTENSIONS = [".png", ".xpm", ".svg"]

    new_programs = {}
    total_time = 0.0
    num_failed = 0

    for i, p in programs.items():
        if p["type"] != "desktop":
            new_programs[i] = p
            continue

        start_time = time.clock()

        # Locate the .desktop file
        desktop_path = None

        for s in desktop_search_paths:
            path = os.path.join(s, p["source"] + ".desktop")
        
            if os.path.isfile(path):
                desktop_path = path
                break
        
        if desktop_path is None:
            print('ERROR: .desktop file for "{0}" not found'.format(i))
            num_failed += 1
            continue

        end_time = time.clock()
        total_time += end_time - start_time

        # Load it
        try:
            desktop_data = load_dotdesktop_file(desktop_path)
        except Exception as e:
            print('ERROR: Can\'t load "{0}" for "{1}": {2}'.format(desktop_path, i, str(e)))
            num_failed += 1
            continue

        # Extract the relevant data out of it
        if "Desktop Entry" not in desktop_data:
            print('ERROR: Can\'t load "{0}" for "{1}": No [Desktop Entry] section in the file'.
                format(desktop_path, i))
            num_failed += 1
            continue

        entry = desktop_data["Desktop Entry"]

        if ("Name" not in entry) or ("Exec" not in entry) or ("Icon" not in entry):
            print('ERROR: Can\'t load "{0}" for "{1}": Missing Name/Exec/Icon directives in the [Desktop Entry] section'.
                format(desktop_path, i))
            num_failed += 1
            continue

        if len(entry["Exec"].strip()) == 0:
            print('ERROR: Can\'t load "{0}" for "{1}": Empty "Exec" string'.
                format(desktop_path, i))
            num_failed += 1
            continue

        # Use "command" instead of "exec" so it's the same key for both desktop and custom programs.
        # Remove %XX parameters from the Exec key in the same way WebMenu does it. It has worked
        # fine for WebMenu, maybe it works fine for us too...?
        # (Reference: file parts/webmenu/src/parseExec.coffee, line 24)
        # TODO: This needs to be verified and done in a better way
        p["command"] = re.sub(r"%[fFuUdDnNickvm]{1}", "", entry["Exec"])

        if "name" not in p:
            # No name was specified for this program. Load it from the desktop file.
            names = {}
            names["en"] = entry["Name"]

            # Check for localized strings
            if "Name[fi]" in entry:
                names["fi"] = entry["Name[fi]"]
            elif "GenericName[fi]" in entry:
                names["fi"] = entry["GenericName[fi]"]

            if "Name[sv]" in entry:
                names["sv"] = entry["Name[sv]"]
            elif "GenericName[sv]" in entry:
                names["sv"] = entry["GenericName[sv]"]

            if "Name[de]" in entry:
                names["de"] = entry["Name[de]"]
            elif "GenericName[de]" in entry:
                names["de"] = entry["GenericName[de]"]

            p["name"] = names

        # If no icon was specified in the YAML, get it from the .desktop and store it in
        # a special field, so we can distinguish between manually specified icons and
        # icons specified in .desktop files.
        if "icon" not in p:
            # Sometimes the icon name is just a generic name and you have to load an appropriate
            # icon that matches the current theme. Sometimes it's a hardcoded path. We have to
            # detect which one this is.
            name = entry["Icon"]
            _, ext = os.path.splitext(name)

            if (len(ext) > 0) and (ext in ICON_EXTENSIONS):
                p["icon"] = name
            else:
                p["desktop_icon"] = name

        new_programs[i] = p

    programs = new_programs
    print("{0} failed program definitions".format(num_failed))
    print("Time to locate and load the .desktop files: {0} seconds".format(total_time))

    # ----------------------------------------------------------------------------------------------
    # Remove nonexisting programs and menus

    print("--- 3. Check that all referenced programs and menus actually exist ---")

    num_missing_progs = 0
    num_missing_menus = 0

    for i, m in menus.items():
        m_progs = []

        for id in m["programs"]:
            # This actually can happen with fat-fingered YAML files
            if type(id) is not str:
                print('ERROR: program ID "{0}" is not a string'.format(id))
                continue

            if id not in programs:
                print('WARNING: Program "{0}" referenced in menu "{1}" does not exist'.
                    format(id, i))
                num_missing_progs += 1
                continue

            m_progs.append(id)

        if len(m_progs) == 0:
            print('WARNING: Menu "{0}" is completely empty'.format(i))

        m["programs"] = m_progs

    for i, c in categories.items():
        c_menus = []
        c_progs = []

        for id in c["menus"]:
            if id not in menus:
                print('WARNING: Menu "{0}" referenced in category "{1}" does not exist'.
                    format(id, i))
                num_missing_menus += 1
                continue

            c_menus.append(id)

        for id in c["programs"]:
            if id not in programs:
                print('WARNING: Program "{0}" referenced in category "{1}" does not exist'.
                    format(id, i))
                num_missing_progs += 1
                continue

            c_progs.append(id)

        if (len(c_menus) == 0) and (len(c_progs) == 0):
            print('WARNING: Category "{0}" is completely empty'.format(i))

        c["menus"] = c_menus
        c["programs"] = c_progs

    print("{0} missing program references, {1} missing menu references".
        format(num_missing_progs, num_missing_menus))

    # ----------------------------------------------------------------------------------------------
    # Warn about unused programs and menus Categories cannot be "unused". If defined,
    # they appear in the menu, empty or not.

    print("--- 4. Check for unused programs and menus ---")
    found_unused = False
    num_programs = 0
    num_menus = 0

    for _, p in programs.items():
        p["used"] = False

    for _, m in menus.items():
        m["used"] = False

    for _, c in categories.items():
        for m in c["menus"]:
            menus[m]["used"] = True

        for p in c["programs"]:
            programs[p]["used"] = True

    for _, m in menus.items():
        if m["used"]:
            for p in m["programs"]:
                programs[p]["used"] = True

    for i, p in programs.items():
        if p["used"] == False:
            print('WARNING: Program "{0}" defined but not used'.format(i))
            found_unused = True
        else:
            num_programs += 1

    for i, m in menus.items():
        if not m["used"]:
            print('WARNING: Menu "{0}" defined but not used'.format(i))
            found_unused = True
        else:
            num_menus += 1

    print("{0}/{1} programs in use, {2}/{3} menus in use".
        format(num_programs, len(programs), num_menus, len(menus)))

    if not found_unused:
        print("No unused programs or menus found")

    # --------------------------------------------------------------------------------------------------
    # Locate icon files

    print("--- 5. Locating and verifying icon files ---")

    total_time = 0.0
    num_missing_icons = 0

    # Locate program icons
    for i, p in programs.items():
        if not p["used"]:
            continue

        start_time = time.clock()

        icon = p.get("icon", None)
        desktop_icon = p.get("desktop_icon", None)

        #print("'{0}': icon='{1}' desktop_icon='{2}'".format(i, icon, desktop_icon))

        if not icon and not desktop_icon:
            # Impossible: no icon at all
            print('WARNING: "{0}" has no icon defined at all and it\'s a desktop program!'.format(id))
            p["icon"] = None
            num_missing_icons += 1
        elif icon and desktop_icon:
            # Impossible: both icons were specified, remove both
            print('WARNING: "{0}" has both manually and automatically defined icons!?'.
                format(id))
            p["icon"] = None
            del p["desktop_icon"]
            num_missing_icons += 1
        elif icon and not desktop_icon:
            # Check the manually specified icon path
            #print("CHECKING FOR |{0}|".format(icon))
            if not os.path.isfile(icon):
                print('WARNING: Icon "{0}" for program "{1}" does not exist'.format(icon, i))
                p["icon"] = None
                num_missing_icons += 1
        else:
            # Locate the icon specified in the .desktop file
            icon_path = None

            for s in icon_paths:
                path = os.path.join(s, p["desktop_icon"] + ".png")
            
                if os.path.isfile(path):
                    icon_path = path
                    break

            p["icon"] = icon_path

            if icon_path is None:
                print('WARNING: Icon "{0}" for program "{1}" not found'.format(p["desktop_icon"], i))
                num_missing_icons += 1

            del p["desktop_icon"]

        end_time = time.clock()
        total_time += end_time - start_time

    # Locate menu icons too. This is easier, because menu icons are all manually specified.
    for i, m in menus.items():
        if "icon" not in m:
            print('WARNING: Menu "{0}" has no icon defined'.format(i))
            m["icon"] = None
            num_missing_icons += 1
        else:
            if not os.path.isfile(m["icon"]):
                print('WARNING: Icon "{0}" for menu "{1}" does not exist'.format(m["icon"], i))
                m["icon"] = None
                num_missing_icons += 1

    print("{0} missing icons".format(num_missing_icons))
    print("Time to locate the icon files: {0} seconds".format(total_time))

    # ----------------------------------------------------------------------------------------------
    # Validate category orders and put them in the correct order

    # TODO: implement this

    # ----------------------------------------------------------------------------------------------

    return programs, menus, categories
