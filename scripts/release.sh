#!/usr/bin/env bash
# Build and locally verify release artifacts.
# Usage: bash scripts/release.sh
set -euo pipefail

rm -rf dist build ./*.egg-info

python -m pip install --upgrade build twine
python -m build
twine check dist/*

echo
echo "Artifacts built in ./dist:"
ls -1 dist
echo
echo "To publish a release, push a tag, e.g.:"
echo "  git tag v\$(python -c 'import synthforge; print(synthforge.__version__)')"
echo "  git push origin --tags"
