class gnome_shell_session {
  include gnome_shell_extensions,
	  packages

  file {
    '/usr/bin/puavo-gnome-session':
      mode   => '0755',
      source => 'puppet:///modules/gnome_shell_session/bin/puavo-gnome-session';

    '/usr/share/gnome-session/sessions/puavo-gnome.session':
      require => Package['gnome-session'],
      source  => 'puppet:///modules/gnome_shell_session/sessions/puavo-gnome.session';

    '/usr/share/gnome-shell/modes/puavo.json':
      require => [ File['/usr/share/gnome-shell/extensions/bottompanel@tmoer93']
		 , Package['gnome-shell-common'] ],
      source  => 'puppet:///modules/gnome_shell_session/modes/puavo.json';

    '/usr/share/xsessions/puavo-gnome.desktop':
      source => 'puppet:///modules/gnome_shell_session/xsessions/puavo-gnome.desktop';
  }

  Package <| title == gnome-shell-common or title == gnome-session |>
}
