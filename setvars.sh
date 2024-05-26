#!/bin/bash
# Path to the JSON file
config="config.json"

# Extract the sidecar port using jq
SIDECAR_PORT=$(jq -r '.sidecar_port' "$config")