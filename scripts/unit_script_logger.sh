#!/bin/bash
# Usage: ./unit_script_logger.sh shortName radioID action [talkgroup] [patchedTalkgroups|source]
# Example: ./unit_script_logger.sh p25sys 1234 join 4567 "6655,7744"

# Assign input parameters to variables
SHORT_NAME="$1"
RADIO_ID="$2"
ACTION="$3"
TALKGROUP="$4"
PATCHED_TALKGROUPS="$5"

# Generate timestamp (in epoch format)
TIMESTAMP=$(date +%s)

# Generate a hash based on all relevant fields
HASH_INPUT="$SHORT_NAME$RADIO_ID$ACTION$TALKGROUP$PATCHED_TALKGROUPS"
HASH=$(echo -n "$HASH_INPUT" | sha256sum | cut -d' ' -f1)

# Initialize JSON structure
JSON_DATA="{\"short_name\": \"$SHORT_NAME\", \"radio_id\": \"$RADIO_ID\", \"action\": \"$ACTION\", \"timestamp\": $TIMESTAMP, \"event_hash\": \"$HASH\""

# Handle optional parameters based on action
if [[ "$ACTION" == "join" || "$ACTION" == "call" ]]; then
    if [[ -n "$TALKGROUP" ]]; then
        JSON_DATA+=", \"talkgroup\": \"$TALKGROUP\""
    fi
    if [[ -n "$PATCHED_TALKGROUPS" ]]; then
        JSON_DATA+=", \"patched_talkgroups\": \"$PATCHED_TALKGROUPS\""
    fi
elif [[ "$ACTION" == "ans_req" ]]; then
    if [[ -n "$TALKGROUP" ]]; then
        JSON_DATA+=", \"source\": \"$TALKGROUP\""
    fi
fi

# Close the JSON structure
JSON_DATA+="}"

# Set the deduplication window (in seconds)
DEDUP_WINDOW=5
WINDOW_START=$((TIMESTAMP - DEDUP_WINDOW))

# Use mongo shell to check for duplicates and insert if none found
MONGO_RESULT=$(mongosh --quiet --eval "
    db = db.getSiblingDB('trunkr_database');
    
    // Ensure compound index exists (event_hash and timestamp)
    db.units_metadata.createIndex({ event_hash: 1, timestamp: 1 });
    
    // Remove the unique index on hash if it exists
    try {
        db.units_metadata.dropIndex('hash_1');
    } catch (e) {
        // Index doesn't exist, ignore
    }
    
    // Check for duplicates and insert if none found
    var doc = $JSON_DATA;
    var existingDoc = db.units_metadata.findOne({
        event_hash: doc.event_hash,
        timestamp: { \$gte: $WINDOW_START, \$lte: doc.timestamp }
    });
    
    if (!existingDoc) {
        db.units_metadata.insertOne(doc);
        'New document inserted.';
    } else {
        'Duplicate found within the last $DEDUP_WINDOW seconds. No insertion made.';
    }
" 2>/dev/null)

#echo "$MONGO_RESULT"
#echo "Script done."