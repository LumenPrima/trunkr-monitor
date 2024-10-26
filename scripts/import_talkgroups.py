#!/usr/bin/env python3
"""
Script to import talkgroups CSV file from trunk-recorder into MongoDB.
Usage: python import_talkgroups.py <csv_file>
"""

import sys
import csv
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

def import_talkgroups(csv_file):
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection details from environment
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    database_name = os.getenv('DATABASE_NAME', 'trunkr_database')
    collection_name = os.getenv('TALKGROUPS_COLLECTION', 'talkgroups_list')
    
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]
    
    # Create index on decimal field
    collection.create_index([("decimal", pymongo.ASCENDING)], unique=True)
    
    # Read and import CSV
    with open(csv_file, 'r') as f:
        csv_reader = csv.DictReader(f)
        records = []
        for row in csv_reader:
            # Convert decimal to integer
            row['decimal'] = int(row['decimal'])
            # Convert hex to uppercase string without '0x' prefix
            row['hex'] = row['hex'].upper()
            records.append(row)
        
        try:
            # Delete existing records
            collection.delete_many({})
            # Insert new records
            collection.insert_many(records)
            print(f"Successfully imported {len(records)} talkgroups")
        except Exception as e:
            print(f"Error importing talkgroups: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_talkgroups.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found")
        sys.exit(1)
    
    import_talkgroups(csv_file)
