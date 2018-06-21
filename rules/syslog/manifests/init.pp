class syslog {
  include ::packages

  Package <| title == syslog-ng |>
}
