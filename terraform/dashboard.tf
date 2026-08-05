resource "truewatch_dashboard" "lab" {
  count = var.enable_dashboard ? 1 : 0

  name      = var.name_prefix
  desc      = "Lab first-mile: four-path metrics (one chart) + APM (Dashboard B)."
  is_public = 0

  tag_names = [
    "lab-first-mile",
    "terraform",
  ]

  # Content SSOT: edit terraform/json/dashboard.json then plan/apply.
  template_info = file("${path.module}/json/dashboard.json")
}
