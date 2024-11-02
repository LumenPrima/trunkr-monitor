#!/bin/bash

# Configuration variables
db_name="trunkr_database"
json_collection="calls_metadata"
gridfs_collection="calls_audio"
mongodb_uri="mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1"
whisper_api_url="http://127.0.0.1:8000/v1/audio/transcriptions"
whisper_model="Systran/faster-whisper-large-v3"
whisper_language="en"
whisper_token="YOUR_ACCESS_TOKEN"

# Function to process a single file
process_file() {
    local json_file="$1"
    local processed_list="$2"
    local basename="${json_file%.*}"
    local audio_file="${basename}.wav"
    local compressed_file="${basename}.m4a"

    # Check if file has been processed already
    if grep -q "$(basename "$json_file")" "$processed_list"; then
        return
    fi

    # Check if JSON file exists
    if [ ! -f "$json_file" ]; then
        echo "Error: Missing JSON file $json_file"
        return
    fi

    # Check call length
    local call_length=$(jq -r '.call_length' "$json_file")
    if [ "$call_length" -eq 0 ]; then
        return
    fi

    # Check and perform compression if needed
    if [ ! -f "$compressed_file" ]; then
        if ! ffmpeg -i "$audio_file" -c:a aac -b:a 128k "$compressed_file" 2>/dev/null; then
            echo "Error: Failed to compress $audio_file"
            return
        fi
    fi

    # Check and perform transcription if needed
    if ! jq -e '.transcription' "$json_file" > /dev/null 2>&1; then
        local response=$(curl -s -w "%{http_code}" -o /tmp/tmpresponse.json -X POST "$whisper_api_url" \
            -F "model=$whisper_model" \
            -F "language=$whisper_language" \
            -F "file=@$compressed_file")

        if [ $? -ne 0 ] || [ "$response" -ne 200 ]; then
            echo "Error: Transcription failed for $compressed_file"
            return
        fi

        local transcription=$(jq -r '.text' /tmp/tmpresponse.json)
        if [ -z "$transcription" ]; then
            echo "Error: Empty transcription for $compressed_file"
            return
        fi

        # Add transcription to JSON
        jq --arg transcription "$transcription" '. + {transcription: $transcription}' "$json_file" > "$json_file.tmp" && mv "$json_file.tmp" "$json_file"
    fi

    # Add audio filename to JSON if not present
    if ! jq -e '.audio_file' "$json_file" > /dev/null 2>&1; then
        local audio_filename=$(basename "$compressed_file")
        jq --arg audio_file "$audio_filename" '. + {audio_file: $audio_file}' "$json_file" > "$json_file.tmp" && mv "$json_file.tmp" "$json_file"
    fi

    # Add hash to the JSON file if not present
    if ! jq -e '.hash' "$json_file" > /dev/null 2>&1; then
        local start_time=$(jq -r '.start_time' "$json_file")
        local talkgroup=$(jq -r '.talkgroup' "$json_file")
        start_time=${start_time:-$(date +%Y-%m-%dT%H:%M:%S)}
        talkgroup=${talkgroup:-"default"}
        local hash=$(echo -n "${start_time}${talkgroup}" | openssl dgst -sha256 | awk '{print $2}')
        jq --arg hash "$hash" '. + {hash: $hash}' "$json_file" > "$json_file.tmp" && mv "$json_file.tmp" "$json_file"
    fi

    # Upload JSON to MongoDB
    if ! mongoimport --uri "$mongodb_uri" --db "$db_name" --collection "$json_collection" --file "$json_file"; then
        echo "Error: Failed to upload JSON for $json_file"
        return
    fi

    # Upload compressed audio file to MongoDB GridFS
    local audio_filename=$(basename "$compressed_file")
    if ! mongofiles --uri "$mongodb_uri" --db "$db_name" --prefix "$gridfs_collection" put "$audio_filename" --local "$compressed_file" --quiet; then
        echo "Error: Failed to upload audio for $compressed_file"
        return
    fi

    echo "Processed: $json_file"
    echo "$(basename "$json_file")" >> "$processed_list"
}

# Function to process a folder
process_folder() {
    local folder_path="$1"
    local processed_list="$folder_path/.processed_files.txt"

    # Create the processed files list if it doesn't exist
    touch "$processed_list"

    # Process each JSON file in the folder
    find "$folder_path" -maxdepth 1 -name "*.json" | while read -r json_file; do
        process_file "$json_file" "$processed_list"
    done

    # Recursively process subfolders
    find "$folder_path" -mindepth 1 -type d | while read -r subfolder; do
        process_folder "$subfolder"
    done
}

# Main script
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

root_folder="$1"

if [ ! -d "$root_folder" ]; then
    echo "Error: Folder $root_folder does not exist."
    exit 1
fi

echo "Processing folder: $root_folder"
process_folder "$root_folder"
echo "Processing complete."
