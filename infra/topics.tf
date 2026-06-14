# Pub/Sub topics internos — doc 01 §2
resource "google_pubsub_topic" "video_recebido" {
  name    = "video-recebido"
  project = var.project_id

  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}

resource "google_pubsub_topic" "item_produzido" {
  name    = "item-produzido"
  project = var.project_id

  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}

resource "google_pubsub_topic" "item_aprovado" {
  name    = "item-aprovado"
  project = var.project_id

  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}

resource "google_pubsub_topic" "publicacao_executada" {
  name    = "publicacao-executada"
  project = var.project_id

  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}

resource "google_pubsub_topic" "custo_alerta" {
  name    = "custo-alerta"
  project = var.project_id

  depends_on = [google_project_service.apis["pubsub.googleapis.com"]]
}
