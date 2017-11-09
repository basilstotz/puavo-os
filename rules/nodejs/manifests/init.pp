class nodejs {
  include ::apt

  # This should be updated to node_6.x, node_8.x, ... later
  $node_branch = 'node_4.x'

  file {
    '/etc/apt/preferences.d/50-nodesource.pref':
      content => template('nodejs/50-nodesource.pref');

    '/etc/apt/sources.list.d/nodesource.list':
      content => template('nodejs/nodesource.list'),
      notify  => Exec['apt update'],
      require => File['/etc/apt/trusted.gpg.d/nodesource.gpg'];

    '/etc/apt/trusted.gpg.d/nodesource.gpg':
      source => 'puppet:///modules/nodejs/nodesource.gpg';
  }
}
