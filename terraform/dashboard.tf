resource "truewatch_dashboard" "lab" {
  count = var.enable_dashboard ? 1 : 0

  name      = var.name_prefix
  desc      = "Lab first-mile: four-path metrics (one chart) + APM (Dashboard B)."
  # 1 = visible to workspace members in console (0 = private to API-key creator only).
  is_public = 1

  tag_names = [
    "lab-first-mile",
    "terraform",
  ]

  # Content SSOT: edit terraform/json/dashboard.json then plan/apply.
  template_info = file("${path.module}/json/dashboard.json")
}
