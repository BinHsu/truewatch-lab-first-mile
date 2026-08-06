resource "truewatch_notify_object" "lab_email" {
  count = var.enable_notify_chain ? 1 : 0

  name = "${var.name_prefix}-mail"
  type = "mailGroup"
  # to[] must be workspace members (acnt_… UUID preferred). Arbitrary external
  # emails store in API but console shows empty and mail often never arrives.
  opt_set = jsonencode({
    to = [var.lab_alert_email]
  })
  open_permission_set = false
}

resource "truewatch_alert_policy" "lab" {
  count = var.enable_notify_chain ? 1 : 0

  name          = "${var.name_prefix}-alert-policy"
  desc          = "Lab first-mile alert policy (N3 email)."
  rule_timezone = var.rule_timezone

  # Associate monitors from the monitor resource (created after this policy).
  # Binding is also set via alert_policy_uuids on truewatch_monitor.lab.
  checker_uuids = []

  alert_opt = {
    alert_type     = "status"
    agg_interval   = 60
    agg_fields     = ["df_monitor_checker_id"]
    silent_timeout = 300
    ignore_ok      = true

    alert_target = [{
      name = "Lab email"

      targets = [{
        to     = [truewatch_notify_object.lab_email[0].uuid]
        # No nodata — idle lab must not email-bomb; alert is fault inject (>=900) only.
        status = "critical"
      }]
    }]
  }

  depends_on = [
    truewatch_notify_object.lab_email,
  ]
}
