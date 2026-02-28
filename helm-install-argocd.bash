#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

helm upgrade \
  --install \
  --namespace argocd \
  --create-namespace \
  --repo https://argoproj.github.io/argo-helm \
  argocd \
  argo-cd \
  --version 9.4.5 \
  --values argocd-values.yaml \
  ;
