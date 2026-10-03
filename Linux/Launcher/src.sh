#!/bin/bash
# Linux Launcher for iz4c810/tools

REPO_OWNER="iz4c810"
REPO_NAME="tools"
API_URL="https://github.com"

echo "Fetching available Linux tools..."

# Fetch directory list using GitHub API
RESPONSE=$(curl -s "$API_URL")

# Extract directory names (requires jq)
if ! command -v jq &> /dev/null; then
    echo "Error: 'jq' is required to parse the tool list. Please install it (e.g., sudo apt install jq)."
    exit 1
fi

TOOLS=($(echo "$RESPONSE" | jq -r '.[] | select(.type=="dir") | .name'))

if [ ${#TOOLS[@]} -eq 0 ]; then
    echo "No tools found in the Linux directory."
    exit 1
fi

# Display Menu
echo ""
echo "=== Select a Tool to Launch ==="
for i in "${!TOOLS[@]}"; do
    echo "[$((i+1))] ${TOOLS[$i]}"
done
echo "[Q] Quit"

read -p "Enter your choice: " CHOICE

if [[ "$CHOICE" =~ ^[qQ]$ ]]; then
    exit 0
fi

INDEX=$((CHOICE-1))

if [ "$INDEX" -ge 0 ] && [ "$INDEX" -lt "${#TOOLS[@]}" ]; then
    SELECTED_TOOL=${TOOLS[$INDEX]}
    echo "Launching $SELECTED_TOOL..."
    
    # Fetch files inside the chosen tool folder
    TOOL_API_URL="https://github.com/$SELECTED_TOOL"
    DOWNLOAD_URL=$(curl -s "$TOOL_API_URL" | jq -r '.[] | select(.name | startswith("src.")) | .download_url' | head -n 1)

    if [ -n "$DOWNLOAD_URL" ] && [ "$DOWNLOAD_URL" != "null" ]; then
        # Download and run the script in memory without saving it to disk
        curl -sL "$DOWNLOAD_URL" | bash
    else
        echo "Could not find a 'src.*' script in Linux/$SELECTED_TOOL/"
    fi
else
    echo "Invalid selection."
fi
