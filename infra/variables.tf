variable "project_id" {
  description = "GCP project ID da plataforma de conteúdo"
  type        = string
  default     = "aisocialz-project"
}

variable "region" {
  description = "Região principal dos serviços"
  type        = string
  default     = "us-central1"
}

variable "budget_monthly_usd" {
  description = "Orçamento mensal em USD (equivalente a R$600 com margem)"
  type        = number
  default     = 120 # ~R$600 a R$5/USD
}

variable "billing_account_name" {
  description = "Display name da billing account do GCP"
  type        = string
}

variable "environment" {
  description = "Ambiente: sandbox ou production"
  type        = string
  default     = "sandbox"
}
