#!/usr/bin/env sh
set -eu

if ! command -v rg >/dev/null 2>&1; then
  echo "error: rg is required for temporary test artifact checks." >&2
  exit 2
fi

if [ "$#" -gt 0 ]; then
  targets="$*"
else
  targets="codebases"
fi

pattern='TEMP_TDD|SCRATCH_TEST|TEMP_TEST|TODO_TEMP_TEST|临时测试|探针测试'

matches=$(rg -n --hidden \
  --glob '!**/.git/**' \
  --glob '!**/node_modules/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  --glob '!**/.uni/**' \
  -e "$pattern" \
  $targets || true)

if [ -n "$matches" ]; then
  echo "Temporary TDD/test artifacts found. Remove them or convert them to retained tests before committing:"
  echo "$matches"
  exit 1
fi

echo "No temporary TDD/test artifact markers found."
