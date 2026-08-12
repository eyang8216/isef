#!/bin/bash
# Delete the merged feat/immersed-free-boundary branch
# Run this on your Mac Terminal

cd ~/Desktop/isef

echo "Deleting merged branch from remote..."
git push origin --delete feat/immersed-free-boundary

echo "Deleting local branch..."
git branch -d feat/immersed-free-boundary

echo "✓ Branch cleanup complete"
