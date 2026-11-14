#!/usr/bin/env bash
# Builds the image and deploys it to the AWS Lightsail container service: make deploy
# Needs: aws CLI v2 with credentials, the lightsailctl plugin, docker, jq.
# Secrets come from the environment or .env; they go to the service, never to git.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"

service="${LIGHTSAIL_SERVICE:-grabbit}"
power="${LIGHTSAIL_POWER:-micro}"
export AWS_REGION="${AWS_REGION:-eu-north-1}"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi
for var in GEMINI_API_KEY GEMINI_MODEL; do
  [ -n "${!var:-}" ] || { echo "deploy: $var is empty (set it in .env)" >&2; exit 1; }
done
for tool in aws docker jq lightsailctl; do
  command -v "$tool" >/dev/null || { echo "deploy: missing $tool" >&2; exit 1; }
done

if ! aws lightsail get-container-services --service-name "$service" >/dev/null 2>&1; then
  echo "Creating container service $service ($power) in $AWS_REGION"
  aws lightsail create-container-service --service-name "$service" \
    --power "$power" --scale 1 >/dev/null
fi
until [ "$(aws lightsail get-container-services --service-name "$service" \
  --query 'containerServices[0].state' --output text)" != "PENDING" ]; do
  echo "Waiting for $service to leave PENDING"; sleep 10
done

make docker
aws lightsail push-container-image --service-name "$service" --label app \
  --image grabbit:latest >/dev/null
image="$(aws lightsail get-container-images --service-name "$service" \
  --query 'containerImages[0].image' --output text)"

# Secrets go through a private temp file, not the command line (visible in ps).
containers="$(mktemp)"
trap 'rm -f "$containers"' EXIT
IMAGE="$image" CALA_MODE="${DEPLOY_CALA_MODE:-replay}" LLM_MODE="${DEPLOY_LLM_MODE:-gemini}" \
  jq -n '{app: {image: env.IMAGE, ports: {"8000": "HTTP"}, environment: {
     CALA_API_KEY: (env.CALA_API_KEY // ""), CONTEXT_DEV_API_KEY: (env.CONTEXT_DEV_API_KEY // ""),
     GEMINI_API_KEY: env.GEMINI_API_KEY, GEMINI_MODEL: env.GEMINI_MODEL,
     CALA_MODE: env.CALA_MODE, LLM_MODE: env.LLM_MODE, DEMO_MODE: "1",
     DATABASE_PATH: "/app/data/grabbit.db"}}}' > "$containers"
endpoint='{"containerName": "app", "containerPort": 8000,
  "healthCheck": {"path": "/api/health", "successCodes": "200"}}'

aws lightsail create-container-service-deployment --service-name "$service" \
  --containers "file://$containers" --public-endpoint "$endpoint" >/dev/null
echo "Deploying $image. State and URL:"
aws lightsail get-container-services --service-name "$service" \
  --query 'containerServices[0].[state, url]' --output text
