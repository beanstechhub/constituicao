#!/usr/bin/env bash
# Deploy de constituicao.tech no GCP
#
# Pré-requisitos:
#   gcloud auth login
#   gcloud config set project SEU-PROJECT-ID
#   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
#       artifactregistry.googleapis.com storage.googleapis.com \
#       compute.googleapis.com
#
# Arquitetura resultante:
#   - Cloud Run (detector): privado, ingress=internal
#   - Cloud Run (api): público, ingress=all, autenticação=permitir todos
#   - Cloud Storage bucket: hospedando web/ estático
#   - Cloud Load Balancer + Cloud Armor: na frente da api e do bucket
#   - Cloud DNS: constituicao.tech → LB

set -euo pipefail

PROJECT="${PROJECT:-constituicao-tech-prod}"
REGION="${REGION:-southamerica-east1}"  # São Paulo
REPO="${REPO:-constituicao-tech}"

echo "==> Configurando Artifact Registry"
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="constituicao.tech containers" 2>/dev/null || true

DETECTOR_IMG="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/detector:latest"
API_IMG="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/api:latest"

echo "==> Build & push detector"
gcloud builds submit detector-py/ --tag="$DETECTOR_IMG" --region="$REGION"

echo "==> Build & push api"
gcloud builds submit api-go/ --tag="$API_IMG" --region="$REGION"

echo "==> Deploy detector (privado)"
gcloud run deploy constituicao-detector \
  --image="$DETECTOR_IMG" \
  --region="$REGION" \
  --platform=managed \
  --ingress=internal \
  --no-allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=20 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=30s

DETECTOR_URL=$(gcloud run services describe constituicao-detector --region="$REGION" --format='value(status.url)')
echo "Detector URL: $DETECTOR_URL"

echo "==> Deploy api (público)"
SALT=$(openssl rand -hex 32)
echo "$SALT" > /tmp/ip_hash_salt.txt  # guarde em Secret Manager em prod!

gcloud run deploy constituicao-api \
  --image="$API_IMG" \
  --region="$REGION" \
  --platform=managed \
  --ingress=all \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --concurrency=80 \
  --min-instances=1 \
  --max-instances=20 \
  --timeout=40s \
  --set-env-vars="DETECTOR_URL=${DETECTOR_URL},AMBIENTE=prod,ALLOWED_ORIGINS=https://constituicao.tech,IP_HASH_SALT=${SALT}"

# Permitir api invocar detector internamente
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')
API_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud run services add-iam-policy-binding constituicao-detector \
  --region="$REGION" \
  --member="serviceAccount:${API_SA}" \
  --role="roles/run.invoker"

echo "==> Upload web estática"
BUCKET="gs://constituicao-tech-web"
gsutil mb -l "$REGION" "$BUCKET" 2>/dev/null || true
gsutil -m rsync -d -r web/ "$BUCKET/"
gsutil iam ch allUsers:objectViewer "$BUCKET"
gsutil web set -m index.html -e index.html "$BUCKET"

cat <<EOF

==> Deploy concluído.

Próximos passos manuais (uma vez):
  1. Reservar IP global:
       gcloud compute addresses create constituicao-tech-ip --global
  2. Configurar Cloud Load Balancer apontando para:
       - Bucket gs://constituicao-tech-web em /*
       - Cloud Run constituicao-api em /v1/*, /health
  3. Anexar Cloud Armor com regras:
       - Rate limit por IP (acima do limite do app)
       - Geo-block opcional
       - OWASP top 10 (preconfigured rules)
  4. Configurar Cloud DNS:
       - constituicao.tech A → IP reservado
       - api.constituicao.tech CNAME → load balancer
  5. Certificado gerenciado para constituicao.tech e api.constituicao.tech

API URL: $(gcloud run services describe constituicao-api --region="$REGION" --format='value(status.url)')
Web bucket: $BUCKET

EOF
