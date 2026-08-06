output "notify_object_uuid" {
  value       = try(truewatch_notify_object.lab_email[0].uuid, null)
  description = "mailGroup notify object UUID"
}

output "alert_policy_uuid" {
  value       = try(truewatch_alert_policy.lab[0].uuid, null)
  description = "Lab alert policy UUID"
}

output "dashboard_uuid" {
  value       = try(truewatch_dashboard.lab[0].uuid, null)
  description = "Lab dashboard UUID"
}

output "monitor_uuids" {
  value       = { for k, m in truewatch_monitor.lab : k => m.uuid }
  description = "Lab monitor UUIDs by path (dataway/datakit/ddtrace/otel)"
}
