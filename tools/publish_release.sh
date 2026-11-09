#!/usr/bin/env bash
set -euo pipefail
version="$(python3 -c 'import json; print(json.load(open("release.json"))["version"])')"
tag="v${version}"
repository="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
target="${GITHUB_SHA:?GITHUB_SHA is required}"
: "${GH_TOKEN:?GH_TOKEN is required}"
notes="release-notes/${tag}.md"
test -f "$notes"
python3 tools/package_release.py --output release-assets
if gh release view "$tag" --repo "$repository" --json isDraft > release-assets-status.json 2>/dev/null; then
  if [ "$(python3 -c 'import json; print(str(json.load(open("release-assets-status.json"))["isDraft"]).lower())')" != "true" ]; then
    echo "Release $tag is already published; keeping its immutable downloads unchanged."
    exit 0
  fi
else
  gh release create "$tag" --repo "$repository" --draft --target "$target" \
    --title "Driving Planner ${version}" --notes-file "$notes"
fi
gh release upload "$tag" release-assets/* --repo "$repository" --clobber
gh release edit "$tag" --repo "$repository" --draft=false --prerelease=false --latest \
  --title "Driving Planner ${version}" --notes-file "$notes"
gh release view "$tag" --repo "$repository" --json url,assets
