const Main = imports.ui.main;
const St   = imports.gi.St;
const Util = imports.misc.util;

let logout_button, menu_button;

function make_button(icon_name, spawn_command) {
    let button = new St.Bin({ can_focus:   true,
			      reactive:    true,
			      style_class: 'panel-button',
			      track_hover: true,
			      x_fill:      true,
			      y_fill:      false });
    let icon = new St.Icon({ icon_name:   icon_name,
                             style_class: 'launcher-box-item' });

    button.set_child(icon);
    button.connect('button-press-event',
		  function() { Util.spawn(spawn_command); });

    return button;
}

function init() {
    logout_button = make_button('webmenu',
	    			[ 'webmenu-spawn', '--logout' ]);
    menu_button   = make_button('webmenu-logout',
				[ 'webmenu-spawn' ]);
}

function disable() {
    Main.panel._leftBox.remove_child(menu_button);
    Main.panel._rightBox.remove_child(logout_button);
}

function enable() {
    Main.panel._leftBox.insert_child_at_index(menu_button,    0);
    Main.panel._rightBox.insert_child_at_index(logout_button, -1);
}
