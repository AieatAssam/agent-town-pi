#!/usr/bin/env bash
# initContainer: install bot tools into the per-namespace PVC at /opt/tools.
# Re-runnable: each tool is skipped when it is already present.
# Runs as root in node:22-bookworm-slim. Only the downloader (curl) is apt-installed,
# and only when missing, because the base image lacks it.
set -euo pipefail

T=/opt/tools
CLAUDE_CODE_VERSION=2.1.327
CODEX_VERSION=0.170.0
KUBECTL_VERSION=v1.37.2
JQ_VERSION=1.7.1
PY_TAG=20250317
PY_VERSION=3.12.9
PILLOW_VERSION=11.3.0
PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PY_TAG}/cpython-${PY_VERSION}+${PY_TAG}-aarch64-unknown-linux-gnu-install_only.tar.gz"
JQ_URL="https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/jq-linux-arm64"
KUBECTL_URL="https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/arm64/kubectl"

mkdir -p "$T/bin"

if ! command -v curl >/dev/null 2>&1; then
  apt-get update -qq >/dev/null
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq curl ca-certificates >/dev/null
fi
# The slim image has no CA store; Rust/Python tools (codex) need one. turn.sh sets SSL_CERT_FILE.
cp /etc/ssl/certs/ca-certificates.crt "$T/ca-certificates.crt"

# python3 (relocatable build): tar extracts to $T/python
if [ ! -x "$T/python/bin/python3" ]; then
  echo "installing python ${PY_VERSION}"
  rm -rf "$T/python"
  curl -fsSL "$PY_URL" | tar -xz -C "$T"
fi
ln -sfn "$T/python/bin/python3" "$T/bin/python3"

# Pillow, for bots that draw images. Installed into the tools python; a failure only warns,
# so the init container still succeeds without it.
if ! "$T/python/bin/python3" -c 'import PIL' >/dev/null 2>&1; then
  echo "installing pillow ${PILLOW_VERSION}"
  "$T/python/bin/python3" -m pip install --disable-pip-version-check --quiet --no-cache-dir \
    "pillow==${PILLOW_VERSION}" || echo "warning: pillow install failed; image drawing unavailable"
fi

if [ ! -x "$T/bin/jq" ]; then
  echo "installing jq ${JQ_VERSION}"
  curl -fsSL -o "$T/bin/jq.tmp" "$JQ_URL" && mv "$T/bin/jq.tmp" "$T/bin/jq"
  chmod 755 "$T/bin/jq"
fi

if [ ! -x "$T/bin/kubectl" ]; then
  echo "installing kubectl ${KUBECTL_VERSION}"
  curl -fsSL -o "$T/bin/kubectl.tmp" "$KUBECTL_URL" && mv "$T/bin/kubectl.tmp" "$T/bin/kubectl"
  chmod 755 "$T/bin/kubectl"
fi

if [ ! -x "$T/npm/node_modules/.bin/claude" ] || [ ! -x "$T/npm/node_modules/.bin/codex" ]; then
  echo "installing claude-code ${CLAUDE_CODE_VERSION} and codex ${CODEX_VERSION}"
  npm install --prefix "$T/npm" --no-audit --no-fund --loglevel=error \
    "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" "@openai/codex@${CODEX_VERSION}"
fi
ln -sfn "$T/npm/node_modules/.bin/claude" "$T/bin/claude"
ln -sfn "$T/npm/node_modules/.bin/codex" "$T/bin/codex"

echo "tools ready:"
"$T/bin/python3" --version
"$T/python/bin/python3" -c 'import PIL; print("pillow", PIL.__version__)' 2>/dev/null || echo "pillow: not installed"
"$T/bin/jq" --version
"$T/bin/kubectl" version --client=true 2>/dev/null | sed -n 1p  # not head: SIGPIPE under pipefail kills the init container
"$T/bin/claude" --version
"$T/bin/codex" --version
