#!/bin/bash
# Clean up stale documentation files and commit changes
# Run this on your Mac Terminal

set -e

cd ~/Desktop/isef

echo "=========================================="
echo "Cleanup and Commit"
echo "=========================================="

echo ""
echo "Step 1: Removing stale documentation files..."
rm -f IMPLEMENTATION_SUMMARY.md
rm -f COMPLETE_STATUS_REPORT.md
rm -f MANUAL_GIT_FIX.sh
rm -f fix_and_push.sh
rm -f push_to_github.sh
rm -f push_simple.sh
rm -f sync_with_github.sh
rm -f clean_and_sync.sh
rm -f nuclear_sync.sh
rm -f delete_merged_branch.sh
echo "✓ Stale files removed"

echo ""
echo "Step 2: Staging changes..."
git add -A
echo "✓ Staged"

echo ""
echo "Step 3: Showing what will be committed..."
git status --short

echo ""
echo "Step 4: Committing..."
git commit -m "chore: clean up stale documentation and update status

- Update IMPLEMENTATION_STATUS.md with correct test count (58, not 34/51)
- Add examples 07-09 to documentation
- Update V3 Track A status (items 1-2 complete, verified)
- Document guardrails and caveats clearly
- Remove stale IMPLEMENTATION_SUMMARY.md and COMPLETE_STATUS_REPORT.md
- Remove temporary helper scripts

Status: V3 immersed free-boundary milestone functionally complete and verified"

echo "✓ Committed"

echo ""
echo "Step 5: Deleting merged branch..."
git push origin --delete feat/immersed-free-boundary 2>&1 || echo "Branch already deleted or doesn't exist"
git branch -d feat/immersed-free-boundary 2>&1 || echo "Local branch already deleted"
echo "✓ Branch cleanup attempted"

echo ""
echo "Step 6: Pushing to main..."
git push origin main
echo "✓ Pushed"

echo ""
echo "=========================================="
echo "✅ Cleanup complete!"
echo "=========================================="
echo ""
echo "Changes committed and pushed to main"
