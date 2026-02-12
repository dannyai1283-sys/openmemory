#!/bin/bash
# OpenMemory GitHub Setup Script

echo "🚀 OpenMemory GitHub Setup"
echo "=========================="
echo ""

# Step 1: Check if repo exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote configured"
    exit 1
fi

echo "✅ Remote configured:"
git remote -v
echo ""

# Step 2: Check branch
echo "📋 Current branch:"
git branch
echo ""

# Step 3: Check status
echo "📊 Repository status:"
git status --short
echo ""

# Step 4: Commit count
echo "📝 Total commits:"
git log --oneline | wc -l
echo ""

# Step 5: Push instructions
echo "🎯 Next steps to push to GitHub:"
echo ""
echo "1. Create GitHub repository:"
echo "   https://github.com/new"
echo "   Name: openmemory"
echo "   Visibility: Public"
echo "   ❌ DON'T initialize with README"
echo ""
echo "2. Set remote with token:"
echo "   git remote set-url origin https://TOKEN@github.com/openmemory/openmemory.git"
echo ""
echo "3. Push code:"
echo "   git push -u origin main"
echo ""
echo "4. Verify:"
echo "   https://github.com/openmemory/openmemory"
