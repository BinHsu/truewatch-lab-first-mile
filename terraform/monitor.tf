resource "truewatch_monitor_json" "lab" {
  count = var.enable_monitor ? 1 : 0

  type         = "trigger"
  checker_json = file("${path.module}/json/monitor.checker.json")
}
