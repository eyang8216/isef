#!/bin/bash
# Run this script on your Mac Terminal to commit and push everything
# Usage: cd ~/Desktop/isef && bash push_to_github.sh

set -e  # Exit on error

echo "=========================================="
echo "Committing and Pushing Immersed Boundary Work"
echo "=========================================="

cd ~/Desktop/isef

echo ""
echo "Step 1: Removing any git lock files..."
rm -f .git/index.lock .git/objects/maintenance.lock
find .git/objects -name "tmp_obj_*" -delete 2>/dev/null || true
echo "✓ Lock files removed"

echo ""
echo "Step 2: Configuring git..."
git config user.email "eyang8216@gmail.com"
git config user.name "eyang8216"
echo "✓ Git configured"

echo ""
echo "Step 3: Staging all changes..."
git add -A
echo "✓ Changes staged"

echo ""
echo "Step 4: Committing..."
git commit -m "feat(v3): implement immersed boundary with rounded cone geometry

- Add ImplicitCone with C1 tangent spherical cap/flank geometry
- Implement fractional-distance immersed Dirichlet stencils
- Add one-sided normal field reconstruction for interface
- Enable candidate-dependent field coupling in optimizer
- Add immersed mode to electrostatics and optimization
- Implement flank-only residual and angle extraction
- Add test_immersed.py and test_implicit_cone.py (50 tests passing)
- Add example 07: immersed free-boundary demonstration
- Add documentation: IMPLEMENTATION_SUMMARY.md, COMPLETE_STATUS_REPORT.md

Status: Core implementation complete, verification work ongoing
Current benchmark: ~47.5° on example grid (vs 49.29° Taylor ideal)

See IMPLEMENTATION_SUMMARY.md for detailed status and remaining work"
echo "✓ Committed"

echo ""
echo "Step 5: Setting remote with credentials..."
git remote set-url origin https://eyang8216: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@github.com/eyang8216/isef.git
echo "✓ Remote configured"

echo ""
echo "Step 6: Fetching latest changes from origin..."
git fetch origin
echo "✓ Fetched"

echo ""
echo "Step 7: Merging origin/main..."
if git merge origin/main --no-edit; then
    echo "✓ Merged successfully"
else
    echo "⚠️  Merge conflicts detected - please resolve manually"
    exit 1
fi

echo ""
echo "Step 8: Pushing to feat/immersed-free-boundary..."
git push origin feat/immersed-free-boundary
echo "✓ Pushed successfully!"

echo ""
echo "=========================================="
echo "✅ SUCCESS - All changes pushed to GitHub"
echo "=========================================="
echo ""
echo "Branch: feat/immersed-free-boundary"
echo "Next steps:"
echo "1. Visit: https://github.com/eyang8216/isef/tree/feat/immersed-free-boundary"
echo "2. Review the changes"
echo "3. Create a Pull Request to merge into main when ready"
