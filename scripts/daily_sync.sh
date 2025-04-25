#!/bin/bash

# Navigate to the repo
cd ~/OP_Recovery_Experiment || exit

# Generate today's date parts
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
MONTH_NAME=$(date +%b)

# Construct log path
LOG_PATH=~/OP_Recovery_Experiment/logs/${YEAR}/${MONTH}-${MONTH_NAME}/${DAY}

# Create the directory if it doesn't exist
mkdir -p "$LOG_PATH"

# Stage all changes
git add .

# Commit with timestamp
git commit -m "Daily sync: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin main
