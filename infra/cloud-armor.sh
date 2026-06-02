#!/usr/bin/env bash
# Cloud Armor policy para constituicao.tech
#
# Configura proteção de borda na frente do Load Balancer.
# Cobre: rate limiting, OWASP, geo-blocking opcional.

set -euo pipefail
POLICY="${POLICY:-constituicao-tech-armor}"

gcloud compute security-policies create "$POLICY" \
  --description="Edge protection for constituicao.tech" 2>/dev/null || true

# Regra 1000: rate limit 60 req/min por IP no endpoint da API
gcloud compute security-policies rules create 1000 \
  --security-policy="$POLICY" \
  --expression="request.path.matches('/v1/.*')" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=60 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP

# Regra 2000: OWASP — SQL injection
gcloud compute security-policies rules create 2000 \
  --security-policy="$POLICY" \
  --expression="evaluatePreconfiguredExpr('sqli-v33-stable')" \
  --action=deny-403

# Regra 2100: OWASP — XSS
gcloud compute security-policies rules create 2100 \
  --security-policy="$POLICY" \
  --expression="evaluatePreconfiguredExpr('xss-v33-stable')" \
  --action=deny-403

# Regra 2200: OWASP — Local file inclusion
gcloud compute security-policies rules create 2200 \
  --security-policy="$POLICY" \
  --expression="evaluatePreconfiguredExpr('lfi-v33-stable')" \
  --action=deny-403

# Regra 2300: protocol attacks
gcloud compute security-policies rules create 2300 \
  --security-policy="$POLICY" \
  --expression="evaluatePreconfiguredExpr('protocolattack-v33-stable')" \
  --action=deny-403

# Regra default: permitir
echo "Cloud Armor configurado. Aplique ao backend service:"
echo "  gcloud compute backend-services update constituicao-api-backend \\"
echo "    --security-policy=$POLICY --global"
