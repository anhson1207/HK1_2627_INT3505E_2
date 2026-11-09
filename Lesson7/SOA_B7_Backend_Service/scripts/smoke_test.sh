#!/bin/sh
set -eu
BASE="${BASE_URL:-http://localhost:5000}"

printf 'GET /healthz\n'
curl -fsS "$BASE/healthz"
printf '\nGET /ready\n'
curl -fsS "$BASE/ready"
printf '\nGET /api/v1/products?page=1&size=20\n'
curl -fsS "$BASE/api/v1/products?page=1&size=20"
printf '\nGET /api/v1/orders?page=1&size=20\n'
curl -fsS "$BASE/api/v1/orders?page=1&size=20"
printf '\n'
