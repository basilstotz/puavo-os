class gnome_shell_extensions {
  include packages

  file {
    '/usr/share/gnome-shell/extensions/bigtouch-ux@puavo.org':
      recurse => true,
      require => Package['gnome-shell-extensions'],
      source  => 'puppet:///modules/gnome_shell_extensions/bigtouch-ux';

  '/usr/share/gnome-shell/extensions/bottompanel@tmoer93':
      recurse => true,
      require => Package['gnome-shell-extensions'],
      source  => 'puppet:///modules/gnome_shell_extensions/bottompanel@tmoer93';

  }

  Package <| title == gnome-shell-extensions |>
}
