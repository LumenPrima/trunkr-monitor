from pymongo import MongoClient
import time
from config import MONGODB_URI, DATABASE_NAME, MAX_RECORDS

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]

    def get_active_calls(self):
        """Get active calls from units_metadata"""
        now = int(time.time())
        pipeline = [
            {
                "$match": {
                    "action": "call",
                    "timestamp": {"$gte": now - 180}  # Last 3 minutes
                }
            },
            {
                "$group": {
                    "_id": "$talkgroup",
                    "start_time": {"$min": "$timestamp"},
                    "initiating_unit": {"$first": "$radio_id"},
                    "latest_time": {"$max": "$timestamp"}
                }
            },
            {
                "$lookup": {
                    "from": "talkgroups_list",
                    "let": {"tg": {"$toInt": "$_id"}},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$Decimal", "$$tg"]}
                            }
                        }
                    ],
                    "as": "talkgroup_info"
                }
            },
            {
                "$project": {
                    "talkgroup": "$_id",
                    "start_time": 1,
                    "initiating_unit": 1,
                    "latest_time": 1,
                    "alpha_tag": {"$arrayElemAt": ["$talkgroup_info.Alpha Tag", 0]}
                }
            },
            {
                "$sort": {
                    "latest_time": -1,
                    "talkgroup": 1
                }
            }
        ]
        return list(self.db.units_metadata.aggregate(pipeline))

    def get_recent_calls(self):
        """Get recent completed calls"""
        now = int(time.time())
        return list(self.db.calls_metadata.find(
            {"start_time": {"$gte": now - 300}},
            sort=[("start_time", 1)],
            limit=MAX_RECORDS
        ))
