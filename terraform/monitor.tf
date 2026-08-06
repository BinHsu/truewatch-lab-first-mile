# Four path tip-of-spear monitors (simpleCheck allows alias "Result" reliably;
# multi-alias in one checker returned ft.CheckObjectTargetAliasError on this site).

locals {
  lab_fault_monitors = {
    dataway = {
      title = "[lab-first-mile] Fault ping (>=900) dataway"
      dql   = "M::`truewatch_lab_first_mile`:(last(`ping`)) { path = 'dataway' }"
      hint  = "EMIT_MODE=dataway … --ping 900"
    }
    datakit = {
      title = "[lab-first-mile] Fault ping (>=900) datakit"
      dql   = "M::`truewatch_lab_first_mile`:(last(`ping`)) { path = 'datakit' }"
      hint  = "EMIT_MODE=datakit … --ping 900"
    }
    ddtrace = {
      title = "[lab-first-mile] Fault ping (>=900) ddtrace"
      dql   = "M::`truewatch`:(last(`lab_first_mile_ping`)) { path = 'ddtrace' }"
      hint  = "EMIT_MODE=ddtrace … --value 900"
    }
    otel = {
      title = "[lab-first-mile] Fault ping (>=900) otel"
      dql   = "M::`otel_service`:(last(`truewatch_lab_first_mile.ping`)) { path = 'otel' }"
      hint  = "EMIT_MODE=otel … --value 900"
    }
  }
}

resource "truewatch_monitor" "lab" {
  for_each = var.enable_monitor ? local.lab_fault_monitors : {}

  type               = "trigger"
  status             = 0
  tags               = ["lab-first-mile", "terraform", each.key]
  alert_policy_uuids = var.enable_notify_chain ? [truewatch_alert_policy.lab[0].uuid] : []

  extend = jsonencode({
    isNeedCreateIssue = false
    issueLevelUUID    = ""
    needRecoverIssue  = false
  })

  json_script = {
    type                      = "simpleCheck"
    title                     = each.value.title
    message                   = "> Lab fault inject: ${each.key} ping/value >= 900.\n> Normal emit uses 1.0.\n> Inject: ${each.value.hint}"
    every                     = "1m"
    interval                  = 300
    recover_need_period_count = 2
    disable_check_end_time    = false
    group_by                  = []
    channels                  = []
    at_accounts               = []
    at_no_data_accounts       = []

    targets = [
      {
        alias = "Result"
        dql   = each.value.dql
        qtype = "dql"
      },
    ]

    checker_opt = {
      info_event = false
      rules = [
        {
          condition_logic = "and"
          status          = "critical"
          conditions = [
            { alias = "Result", operator = ">=", operands = ["900"] },
          ]
        },
      ]
    }
  }

  depends_on = [
    truewatch_alert_policy.lab,
  ]
}
