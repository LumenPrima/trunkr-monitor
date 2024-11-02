#!/bin/bash

# Usage:
# This script processes audio recordings from trunk-recorder and uploads them to MongoDB
#
# Command: ./process_audio_upload_no_transcription.sh <audio_filename>
#
# Parameters:
#   <audio_filename>: Path to the .wav audio file to process
#
# Requirements:
#   - Corresponding .json metadata file must exist (same name as audio file but .json extension)
#   - MongoDB must be running and accessible
#   - ffmpeg must be installed for audio compression
#
# Example:
#   ./process_audio_upload_no_transcription.sh /path/to/recording_20240101_120000.wav
#
# The script will:
#   1. Compress the audio file to M4A format
#   2. Add metadata including hash
#   3. Upload both audio and metadata to MongoDB
#
# Note: This script is designed to work with trunk-recorder's output format

db_name="trunkr_database"
json_collection="calls_metadata"
gridfs_collection="calls_audio"
mongodb_uri="mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1"

if [ -z "$1" ]; then
  echo "Usage: $0 <audio_filename>"
  exit 1
fi

filename="$1"
basename="${filename%.*}"
json="$basename.json"
compressed_filename="$basename.m4a"

if [ ! -f "$filename" ]; then
  echo "Error: Audio file $filename does not exist."
  exit 1
fi

if [ ! -f "$json" ]; then
  echo "Error: JSON file $json does not exist."
  exit 1
fi

call_length=$(jq -r '.call_length' "$json")
if [ "$call_length" -eq 0 ]; then
  echo "Skipping: The call length for $filename is zero."
  exit 0
fi

if [ ! -f "$compressed_filename" ]; then
  if ! ffmpeg -i "$filename" -c:a aac -b:a 128k "$compressed_filename"; then
    echo "Error compressing audio file."
    exit 1
  fi
fi

# Add audio filename to JSON
audio_filename=$(basename "$compressed_filename")
jq --arg audio_file "$audio_filename" \
   '. + {audio_file: $audio_file}' "$json" > "$json.tmp" && mv "$json.tmp" "$json"

# Add hash to the JSON file
start_time=$(jq -r '.start_time' "$json")
talkgroup=$(jq -r '.talkgroup' "$json")
start_time=${start_time:-$(date +%Y-%m-%dT%H:%M:%S)}
talkgroup=${talkgroup:-"default"}

hash=$(echo -n "${start_time}${talkgroup}" | openssl dgst -sha256 | awk '{print $2}')
jq --arg hash "$hash" '. + {hash: $hash}' "$json" > "$json.tmp" && mv "$json.tmp" "$json"

# Upload JSON to MongoDB
mongoimport --uri "$mongodb_uri" --db "$db_name" --collection "$json_collection" --file "$json"
if [ $? -ne 0 ]; then
  echo "Error uploading call JSON to MongoDB."
  exit 1
fi

# Upload compressed audio file to MongoDB GridFS without path
audio_filename=$(basename "$compressed_filename")
mongofiles --uri "$mongodb_uri" --db "$db_name" --prefix "$gridfs_collection" put "$audio_filename" --local "$compressed_filename" --quiet
if [ $? -ne 0 ]; then
  echo "Error uploading compressed audio file to MongoDB GridFS."
  exit 1
fi
