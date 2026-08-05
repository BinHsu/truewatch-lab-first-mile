variable "lab_alert_email" {
  type        = string
  description = "N3 mailbox for mailGroup notify object. Set via TF_VAR_lab_alert_email or terraform.tfvars (gitignored)."
  sensitive   = true
}

variable "truewatch_end_point" {
  type        = string
  description = "TrueWatch Open API endpoint for the workspace site."
  default     = "https://id1-openapi.truewatch.com"
}

variable "name_prefix" {
  type        = string
  description = "Resource name prefix for lab objects."
  default     = "lab-first-mile"
}

variable "rule_timezone" {
  type        = string
  description = "Alert policy timezone."
  default     = "Asia/Shanghai"
}

variable "enable_notify_chain" {
  type        = bool
  description = "Create mailGroup notify object + alert policy."
  default     = true
}

variable "enable_dashboard" {
  type        = bool
  description = "Create/replace lab dashboard from json/dashboard.json."
  default     = true
}

variable "enable_monitor" {
  type        = bool
  description = "Manage monitor from json/monitor.checker.json (designed with dashboard; default on)."
  default     = true
}
