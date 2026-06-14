# Service accounts — uma por função, menor privilégio (doc 01 §4)

resource "google_service_account" "svc_agents" {
  account_id   = "svc-agents"
  display_name = "Service Account — Agentes ADK"
  project      = var.project_id
}

resource "google_service_account" "svc_render" {
  account_id   = "svc-render"
  display_name = "Service Account — Render (Puppeteer/FFmpeg)"
  project      = var.project_id
}

resource "google_service_account" "svc_publisher" {
  account_id   = "svc-publisher"
  display_name = "Service Account — Publisher (única com acesso a secrets de canal)"
  project      = var.project_id
}

resource "google_service_account" "svc_cockpit_api" {
  account_id   = "svc-cockpit-api"
  display_name = "Service Account — Cockpit API (BFF)"
  project      = var.project_id
}

resource "google_service_account" "svc_cost_guardian" {
  account_id   = "svc-cost-guardian"
  display_name = "Service Account — Cost Guardian (altera platform_status)"
  project      = var.project_id
}

# SA para leitura cross-project do AINewz (doc 01 §1)
resource "google_service_account" "sa_ainewz_reader" {
  account_id   = "sa-ainewz-reader"
  display_name = "Service Account — Leitor cross-project AINewz"
  project      = var.project_id
}

# --- Permissões ---

# Agents: Firestore, Vertex AI, Pub/Sub publish
resource "google_project_iam_member" "agents_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.svc_agents.email}"
}

resource "google_project_iam_member" "agents_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.svc_agents.email}"
}

resource "google_project_iam_member" "agents_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.svc_agents.email}"
}

# Publisher: Firestore, Storage, Secret Manager (canais), Pub/Sub
resource "google_project_iam_member" "publisher_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.svc_publisher.email}"
}

resource "google_project_iam_member" "publisher_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.svc_publisher.email}"
}

resource "google_project_iam_member" "publisher_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.svc_publisher.email}"
}

resource "google_project_iam_member" "publisher_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.svc_publisher.email}"
}

# Render: Storage (leitura templates, escrita assets renderizados)
resource "google_project_iam_member" "render_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.svc_render.email}"
}

# Cost Guardian: Firestore (altera platform_status), Pub/Sub subscriber
resource "google_project_iam_member" "guardian_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.svc_cost_guardian.email}"
}

resource "google_project_iam_member" "guardian_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.svc_cost_guardian.email}"
}

# Cockpit API: Firestore (read), Pub/Sub publish
resource "google_project_iam_member" "cockpit_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.svc_cockpit_api.email}"
}
