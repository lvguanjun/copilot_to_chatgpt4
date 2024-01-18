#!/bin/bash

# Function to update config.py only if the environment variable is set
update_config() {
    local key=$1
    local env_var_value=$(eval echo \$"$2")
    if [ ! -z "$env_var_value" ]; then
        sed -i "s/^$key = .*/$key = \"$env_var_value\"/" config.py
    fi
}

# Copy the sample config to be the actual config
cp config.py.sample config.py

# Update the config.py with environment variables if they are set
update_config "COPILOT_CHAT_URL" "COPILOT_CHAT_URL"
update_config "COPILOT_CHAT_ROUTE" "COPILOT_CHAT_ROUTE"
update_config "GITHUB_TOKEN_URL" "GITHUB_TOKEN_URL"

# Start Uvicorn with live reload
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
