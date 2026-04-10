#!/usr/bin/env bash
set -euo pipefail

echo "== server health =="
date -Is
hostname
uptime

echo
echo "== cpu/mem =="
lscpu | sed -n '1,20p'
free -h

echo
echo "== disk =="
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
df -hT

echo
echo "== services =="
ss -tulpen | sed -n '1,30p'

echo
echo "== rag process =="
ps -ef | grep -E "uvicorn|gunicorn|qdrant|redis|postgres|celery|ollama|vllm" | grep -v grep || true

echo
echo "== app logs last 100 lines =="
if [ -f /var/log/rag-api.log ]; then
  tail -n 100 /var/log/rag-api.log
else
  echo "/var/log/rag-api.log not found"
fi
