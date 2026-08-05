terraform {
  required_version = ">= 1.0"

  required_providers {
    truewatch = {
      source  = "TrueWatchTech/truewatch"
      version = ">= 0.1.1"
    }
  }

  # Lab default: local state (gitignored). Forkers may add a remote backend block.
}

provider "truewatch" {
  # Prefer env (do not commit secrets):
  #   TRUEWATCH_ACCESS_TOKEN  — API Key Secret (same class as OWL_TOKEN)
  #   TRUEWATCH_END_POINT     — e.g. https://id1-openapi.truewatch.com
  #   TRUEWATCH_REGION        — optional if end_point is set
  end_point = var.truewatch_end_point
}
