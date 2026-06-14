# Cloud Billing Budget — doc 05 §3
# Thresholds: 33% (~R$200), 66% (~R$400), 100% (~R$600)
# Publica em custo-alerta (Pub/Sub) para a função guardiã consumir

data "google_billing_account" "main" {
  display_name = var.billing_account_name
}

resource "google_billing_budget" "monthly" {
  billing_account = data.google_billing_account.main.id
  display_name    = "aisocialz-platform-monthly"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_monthly_usd)
    }
  }

  threshold_rules {
    threshold_percent = 0.33
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.66
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }

  all_updates_rule {
    pubsub_topic = google_pubsub_topic.custo_alerta.id
  }
}
