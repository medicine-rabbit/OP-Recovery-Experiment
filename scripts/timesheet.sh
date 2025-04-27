#!/bin/bash

# Path to save YAML logs
LOG_DIR="$HOME/OP_Recovery_Experiment/logs/modeling_sessions"
mkdir -p "$LOG_DIR"

COMMAND=$1
SUBCOMMAND=$2

# --- [ CHECK DEPENDENCIES ] ---
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please run: sudo dnf install jq"
    exit 1
fi

if ! command -v timew &> /dev/null; then
    echo "Error: timew (Timewarrior) is not installed. Please install it first."
    exit 1
fi

# --- [ MAIN LOGIC ] ---
if [ "$COMMAND" == "start" ] && [ "$SUBCOMMAND" == "modeling" ]; then
    timew start modeling
    echo "Started modeling session."
elif [ "$COMMAND" == "pause" ]; then
    timew stop
    echo "Paused session."
elif [ "$COMMAND" == "resume" ]; then
    timew continue modeling
    echo "Resumed modeling session."
elif [ "$COMMAND" == "complete" ]; then
    # Stop timer
    timew stop

    # Extract last session info
    LAST_SESSION=$(timew export | jq '.[-1]')
    START=$(echo "$LAST_SESSION" | jq -r '.start')
    END=$(echo "$LAST_SESSION" | jq -r '.end')

    # Calculate duration
    START_TIMESTAMP=$(date -d "$START" +%s)
    END_TIMESTAMP=$(date -d "$END" +%s)
    TOTAL_MINUTES=$(( (END_TIMESTAMP - START_TIMESTAMP) / 60 ))

    # Ask for task focus
    echo "Enter a short description for task_focus:"
    read TASK_FOCUS

    # Create YAML file
    FILE_NAME="$LOG_DIR/modeling_$(date +%Y%m%dT%H%M%S).yaml"

    cat <<EOF > "$FILE_NAME"
activity_type: Open-Ended Modeling Work
start_time: $START
end_time: $END
total_duration_minutes: $TOTAL_MINUTES
task_focus: "$TASK_FOCUS"
