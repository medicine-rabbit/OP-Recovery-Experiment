#!/bin/bash

export RESTIC_REPOSITORY=$HOME/restic_repo

# Backup the main experiment directory
restic backup $HOME/OP_Recovery_Experiment \
  --exclude="$HOME/OP_Recovery_Experiment/.git" \
  --password-file=$HOME/.restic_password \
  >> $HOME/restic_backup.log 2>&1

# Cleanup old snapshots to conserve space
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune \
  --repo=$HOME/restic_repo \
  --password-file=$HOME/.restic_password \
  >> $HOME/restic_backup.log 2>&1
