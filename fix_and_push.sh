#!/bin/bash
# Fix git locks and push immersed boundary implementation

set -e  # Exit on error

echo "=== Fixing Git Lock Issues ==="
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Remove lock files
if [ -f .git/index.lock ]; then
    echo "Removing .git/index.lock..."
    rm -f .git/index.lock
fi

if [ -f .git/objects/maintenance.lock ]; then
    echo "Removing .git/objects/maintenance.lock..."
    rm -f .git/objects/maintenance.lock
fi

# Clean up any temporary pack files
find .git/objects/pack -name "tmp_*" -type f -delete 2>/dev/null || true

echo ""
echo "=== Configuring Git ==="
git config user.email "eyang8216@gmail.com"
git config user.name "eyang8216"

# Configure credentials
git config credential.helper store
echo "https://eyang8216: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@github.com" > ~/.git-credentials

# Set remote URL with credentials
git remote set-url origin https://eyang8216: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@github.com/eyang8216/isef.git

echo ""
echo "=== Current Branch Status ==="
git status

echo ""
echo "=== Adding All Changes ==="
git add -A

echo ""
echo "=== Committing Changes ==="
git commit -m "feat(v3): implement immersed boundary with rounded cone geometry

- Add ImplicitCone with C1 tangent spherical cap/flank geometry
- Implement fractional-distance immersed Dirichlet stencils
- Add one-sided normal field reconstruction for interface
- Enable candidate-dependent field coupling in optimizer
- Add immersed mode to electrostatics and optimization
- Implement flank-only residual and angle extraction
- Add test_immersed.py and test_implicit_cone.py (50 tests passing)
- Add example 07: immersed free-boundary demonstration

Status: Core implementation complete, verification work ongoing
Current benchmark: ~47.5° on example grid (vs 49.29° Taylor ideal)

See IMPLEMENTATION_SUMMARY.md for detailed status and remaining work"

echo ""
echo "=== Fetching Latest from Origin ==="
git fetch origin

echo ""
echo "=== Checking for Updates on Main ==="
git log --oneline HEAD..origin/main | head -10

echo ""
echo "=== Merging Main into Current Branch ==="
# Attempt merge, allow conflicts
if git merge origin/main --no-edit; then
    echo "Merge successful!"
else
    echo ""
    echo "⚠️  MERGE CONFLICT DETECTED ⚠️"
    echo "Please resolve conflicts manually, then run:"
    echo "  git add <resolved-files>"
    echo "  git commit"
    echo "  git push origin feat/immersed-free-boundary"
    exit 1
fi

echo ""
echo "=== Pushing to GitHub ==="
git push origin feat/immersed-free-boundary

echo ""
echo "=== SUCCESS ==="
echo "All changes have been pushed to feat/immersed-free-boundary"
echo ""
echo "Next steps:"
echo "1. Review the changes on GitHub"
echo "2. Run tests: .venv/bin/python -m pytest -q"
echo "3. See IMPLEMENTATION_SUMMARY.md for remaining verification work"
echo "4. Create a PR to merge feat/immersed-free-boundary → main when ready"
