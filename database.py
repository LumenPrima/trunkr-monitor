from pymongo import MongoClient
import time
from config import (
    MONGODB_URI, DATABASE_NAME, DEBUG_MODE,
    UNITS_COLLECTION, CALLS_COLLECTION, TALKGROUPS_COLLECTION
)
import threading
from typing import Dict, List, Callable
import logging
import os

# Configure logging based on debug mode
if DEBUG_MODE:
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join("logs", "trunkr.log")),
        ]
    )
else:
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join("logs", "trunkr.log")),
        ]
    )

def debug_log(message):
    """Log debug messages if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        logging.warning(message)

class DatabaseManager:
    """
    Manages MongoDB database connections and real-time data monitoring.
    Implements both change streams and fallback polling mechanisms for
    reliable data updates, with support for callback notifications.
    """
    def __init__(self):
        # Configure MongoDB client
        try:
            # First try without replica set specific options
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DATABASE_NAME]
            
            # Test connection
            self.db.command('ping')
            debug_log("Connected to MongoDB successfully")
            
            # Check if replica set is available (but don't require it)
            try:
                is_replica_set = self.client.admin.command('replSetGetStatus')
                debug_log(f"Connected to replica set: {is_replica_set.get('set')}")
                # If we got here, we're connected to a replica set, so we can use change streams
                self._use_change_streams = True
            except Exception as e:
                debug_log(f"Not connected to a replica set: {str(e)}")
                debug_log("Will use polling mechanism instead of change streams")
                self._use_change_streams = False
                
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {str(e)}")
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")

        self._active_calls: Dict = {}        # Currently active radio calls
        self._recent_calls: List = []        # Recent call history (last 5 minutes)
        self._recent_units = []              # Recent unit activities (last 5 minutes)
        self._callbacks: List[Callable] = [] # Registered update callbacks
        self._running = True                 # Controls background thread execution
        self._last_refresh = 0               # Timestamp of last data refresh
        
        self._load_initial_data()
        if self._use_change_streams:
            self._start_change_streams()
        self._start_fallback_polling()

    def _load_initial_data(self):
        """
        Load initial data from the database for the last 5 minutes.
        Includes both unit activities and call metadata.
        """
        try:
            now = int(time.time())
            
            # Load recent units (last 5 minutes)
            self._recent_units = list(self.db[UNITS_COLLECTION].find(
                {"timestamp": {"$gte": now - 300}},
                sort=[("timestamp", -1)]
            ).limit(100))
            
            # Load recent calls (last 5 minutes)
            self._recent_calls = list(self.db[CALLS_COLLECTION].find(
                {"start_time": {"$gte": now - 300}},
                sort=[("start_time", -1)]
            ).limit(50))
            
            # Update active calls from loaded data
            self._update_active_calls()
            
            debug_log(f"Initial data loaded: {len(self._recent_units)} units, {len(self._recent_calls)} calls")
            
        except Exception as e:
            logging.error(f"Error loading initial data: {str(e)}")

    def _fallback_polling(self):
        """
        Fallback polling mechanism that activates when change streams are unavailable.
        Polls the database every second for new records, but only updates if changes
        haven't been received through change streams recently.
        """
        debug_log("Starting fallback polling mechanism")
        while self._running:
            try:
                now = int(time.time())
                
                # Only refresh if no recent change stream updates (1 second threshold)
                # or if we're not using change streams
                if not self._use_change_streams or now - self._last_refresh >= 1:
                    # Check for new units in last 5 seconds
                    recent_units = list(self.db[UNITS_COLLECTION].find(
                        {"timestamp": {"$gte": now - 5}},
                        sort=[("timestamp", -1)]
                    ))
                    
                    if recent_units:
                        debug_log(f"Fallback: Found {len(recent_units)} new unit records")
                        self._recent_units = list(self.db[UNITS_COLLECTION].find(
                            {"timestamp": {"$gte": now - 300}},
                            sort=[("timestamp", -1)]
                        ).limit(100))
                        self._update_active_calls()
                        self._notify_callbacks()
                    
                    # Check for new calls in last 5 seconds
                    recent_calls = list(self.db[CALLS_COLLECTION].find(
                        {"start_time": {"$gte": now - 5}},
                        sort=[("start_time", -1)]
                    ))
                    
                    if recent_calls:
                        debug_log(f"Fallback: Found {len(recent_calls)} new call records")
                        self._recent_calls = list(self.db[CALLS_COLLECTION].find(
                            {"start_time": {"$gte": now - 300}},
                            sort=[("start_time", -1)]
                        ).limit(50))
                        self._notify_callbacks()
                    
                    self._last_refresh = now
                
                time.sleep(0.1)  # Prevent CPU overutilization
                
            except Exception as e:
                logging.error(f"Error in fallback polling: {str(e)}")
                time.sleep(1)

    def _start_fallback_polling(self):
        """
        Starts the fallback polling mechanism in a separate daemon thread.
        This ensures continuous data updates even if change streams fail.
        """
        thread = threading.Thread(
            target=self._fallback_polling,
            daemon=True,
            name="FallbackPoller"
        )
        thread.start()
        debug_log("Fallback polling thread started")

    def _handle_units_change(self, change_stream):
        """
        Handles unit metadata change stream events.
        Updates recent units list and active calls when relevant changes occur.
        Includes automatic reconnection logic for stream failures.
        """
        debug_log("Units change stream handler started")
        while self._running:
            try:
                for change in change_stream:
                    self._last_refresh = int(time.time())
                    if change['operationType'] in ['insert', 'update']:
                        now = int(time.time())
                        
                        # Update recent units list with last 5 minutes of data
                        self._recent_units = list(self.db[UNITS_COLLECTION].find(
                            {"timestamp": {"$gte": now - 300}},
                            sort=[("timestamp", -1)]
                        ).limit(100))
                        
                        # Update active calls only for call-related changes
                        doc = change.get('fullDocument')
                        if doc and doc.get('action') == 'call':
                            self._update_active_calls()
                        
                        self._notify_callbacks()
                        
            except Exception as e:
                logging.error(f"Error in units change stream: {str(e)}")
                if not self._use_change_streams:
                    break
                # Attempt stream reconnection
                try:
                    change_stream = self.db[UNITS_COLLECTION].watch(
                        pipeline=[{'$match': {'operationType': {'$in': ['insert', 'update']}}}]
                    )
                    debug_log("Reconnected to units change stream")
                except Exception as conn_err:
                    logging.error(f"Units change stream reconnection failed: {str(conn_err)}")
                    time.sleep(1)

    def _handle_calls_change(self, change_stream):
        """
        Handles call metadata change stream events.
        Updates recent calls list when changes occur.
        Includes automatic reconnection logic for stream failures.
        """
        debug_log("Calls change stream handler started")
        while self._running:
            try:
                for change in change_stream:
                    self._last_refresh = int(time.time())
                    if change['operationType'] in ['insert', 'update']:
                        now = int(time.time())
                        
                        # Update recent calls list with last 5 minutes of data
                        self._recent_calls = list(self.db[CALLS_COLLECTION].find(
                            {"start_time": {"$gte": now - 300}},
                            sort=[("start_time", -1)]
                        ).limit(50))
                        
                        self._notify_callbacks()
                        
            except Exception as e:
                logging.error(f"Error in calls change stream: {str(e)}")
                if not self._use_change_streams:
                    break
                # Attempt stream reconnection
                try:
                    change_stream = self.db[CALLS_COLLECTION].watch(
                        pipeline=[{'$match': {'operationType': {'$in': ['insert', 'update']}}}]
                    )
                    debug_log("Reconnected to calls change stream")
                except Exception as conn_err:
                    logging.error(f"Calls change stream reconnection failed: {str(conn_err)}")
                    time.sleep(1)

    def _start_change_streams(self):
        """
        Initializes and starts change stream watchers for both units and calls collections.
        Creates separate daemon threads for each stream to handle updates independently.
        """
        try:
            # Start units change stream with filtering pipeline
            units_change_stream = self.db[UNITS_COLLECTION].watch(
                pipeline=[{'$match': {'operationType': {'$in': ['insert', 'update']}}}],
                full_document='updateLookup'
            )
            units_thread = threading.Thread(
                target=self._handle_units_change,
                args=(units_change_stream,),
                daemon=True,
                name="UnitsChangeStream"
            )
            units_thread.start()
            debug_log("Units change stream started")

            # Start calls change stream with filtering pipeline
            calls_change_stream = self.db[CALLS_COLLECTION].watch(
                pipeline=[{'$match': {'operationType': {'$in': ['insert', 'update']}}}],
                full_document='updateLookup'
            )
            calls_thread = threading.Thread(
                target=self._handle_calls_change,
                args=(calls_change_stream,),
                daemon=True,
                name="CallsChangeStream"
            )
            calls_thread.start()
            debug_log("Calls change stream started")

        except Exception as e:
            logging.error(f"Error starting change streams: {str(e)}")
            debug_log("Falling back to polling mechanism")
            self._use_change_streams = False

    def _update_active_calls(self):
        """
        Updates the active calls dictionary based on recent unit activities.
        Considers calls active if they have activity within the last 3 minutes.
        Includes talkgroup metadata lookup for each active call.
        """
        try:
            now = int(time.time())
            active_records = [
                record for record in self._recent_units 
                if record.get('action') == 'call' and 
                record['timestamp'] >= now - 180  # Last 3 minutes
            ]
            
            # Clear old active calls
            self._active_calls.clear()
            
            # Process new active calls
            for record in active_records:
                tg = str(record["talkgroup"])
                if tg not in self._active_calls:
                    # Fetch talkgroup info from metadata
                    tg_info = self.db[TALKGROUPS_COLLECTION].find_one(
                        {"Decimal": int(tg)},
                        {"Alpha Tag": 1}
                    )
                    
                    self._active_calls[tg] = {
                        'talkgroup': tg,
                        'start_time': record['timestamp'],
                        'latest_time': record['timestamp'],
                        'initiating_unit': record['radio_id'],
                        'alpha_tag': tg_info.get('Alpha Tag') if tg_info else None
                    }
                else:
                    self._active_calls[tg]['latest_time'] = max(
                        self._active_calls[tg]['latest_time'],
                        record['timestamp']
                    )
            
            if active_records and DEBUG_MODE:
                debug_log(f"Updated active calls: {len(self._active_calls)} active")
                
        except Exception as e:
            logging.error(f"Error updating active calls: {str(e)}")

    def _notify_callbacks(self):
        """
        Notifies all registered callbacks of state updates.
        Each callback is executed independently to prevent cascading failures.
        """
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Callback error: {str(e)}")

    def register_callback(self, callback: Callable):
        """
        Registers a callback function to be notified of state updates.
        Immediately executes the callback with current state after registration.
        
        Args:
            callback: Callable function to be executed on state updates
        """
        self._callbacks.append(callback)
        debug_log(f"New callback registered. Total callbacks: {len(self._callbacks)}")
        # Notify immediately of current state
        try:
            callback()
            debug_log("Immediate callback executed successfully")
        except Exception as e:
            logging.error(f"Error in immediate callback: {str(e)}")

    def get_active_calls(self):
        """
        Returns current active calls sorted by talkgroup number.
        
        Returns:
            List of active call dictionaries sorted by talkgroup number
        """
        active_calls = list(self._active_calls.values())
        return sorted(active_calls, key=lambda x: (int(x['talkgroup']), -x['start_time']))

    def get_recent_calls(self):
        """
        Returns the list of recent calls from the last 5 minutes.
        
        Returns:
            List of recent call metadata records
        """
        return self._recent_calls
    
    def get_recent_units(self):
        """
        Returns the list of recent unit activities from the last 5 minutes.
        
        Returns:
            List of recent unit activity records
        """
        return self._recent_units
