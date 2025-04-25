#!/bin/bash

# Navigate to the repo
cd ~/OP_Recovery_Experiment || exit

# Stage all changes
git add .

# Commit with timestamp
git commit -m "Daily sync: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin main
