#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo 'usage: bash run.sh CASE_DIRECTORY' >&2
  exit 2
fi
here=$(cd -- "$(dirname -- "$0")" && pwd)
venv=${DECRYPT_VENV:-"$HOME/data/.decrypt-venv"}
if [ ! -x "$venv/bin/python" ]; then
  echo "ERROR: decrypt Python venv missing: $venv" >&2
  exit 2
fi
base_bin=$(sed -n 's/^home = //p' "$venv/pyvenv.cfg" | head -n 1)
if [ -z "$base_bin" ]; then
  echo 'ERROR: no base Python path in pyvenv.cfg' >&2
  exit 2
fi
base_lib=$(dirname "$base_bin")/lib
export LD_LIBRARY_PATH="$base_lib:/usr/local/openssl/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
if [ -z "${SEAL_KEY_IV:-}" ]; then
  IFS= read -r SEAL_KEY_IV || { echo "ERROR: missing key on stdin" >&2; exit 2; }
  export SEAL_KEY_IV
fi
"$venv/bin/python" "$here/restore-small.py"
"$venv/bin/python" "$here/runner.py" "$1"
