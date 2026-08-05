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

output "monitor_uuid" {
  value       = try(truewatch_monitor_json.lab[0].uuid, null)
  description = "Lab monitor UUID (null while enable_monitor=false)"
}
