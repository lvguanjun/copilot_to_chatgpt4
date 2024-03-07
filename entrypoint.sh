#!/bin/bash

# Function to update config.py only if the environment variable is set
update_config() {
    local key=$1
    local env_var_value=$(eval echo \$$2)
    local delimiter="|"
    if [ ! -z "$env_var_value" ]; then
        # Use the variable as the delimiter in the sed command
        sed -i "s${delimiter}^$key = .*${delimiter}$key = '$env_var_value'${delimiter}" config.py
    fi
}

# Copy the sample config to be the actual config
cp config.py.sample config.py

# Update the config.py with environment variables if they are set
update_config "COPILOT_CHAT_URL" "COPILOT_CHAT_URL"
update_config "COPILOT_CHAT_ROUTE" "COPILOT_CHAT_ROUTE"
update_config "GITHUB_TOKEN_URL" "GITHUB_TOKEN_URL"
update_config "SALT" "SALT"
update_config "TOKEN_URLS_TYPE" "TOKEN_URLS_TYPE"
update_config "TOKEN_URLS" "TOKEN_URLS"
update_config "RATE_LIMIT_TIME" "RATE_LIMIT_TIME"

# Start Uvicorn with live reload
exec uvicorn main:app --host 0.0.0.0 --port 8080 --reload
