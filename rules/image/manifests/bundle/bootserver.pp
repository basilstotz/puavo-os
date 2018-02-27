class image::bundle::bootserver {
  include ::bootserver_autopoweron
  # include ::bootserver_backup         # XXX needs work
  include ::bootserver_cron
  include ::bootserver_cups
  include ::packages

  Package <| tag == tag_puavo_bootserver |>
}
