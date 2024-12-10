import json
from datetime import datetime

class LocationTracker:
    def __init__(self):
        self.locations = []

    def add_pothole(self, lat, lon, severity):
        """Add a new pothole location with timestamp and severity."""
        pothole = {
            'latitude': lat,
            'longitude': lon,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.locations.append(pothole)
        self._save_locations()

    def get_all_potholes(self):
        """Return all recorded pothole locations."""
        return self.locations

    def _save_locations(self):
        """Save pothole locations to a JSON file."""
        with open('pothole_locations.json', 'w') as f:
            json.dump(self.locations, f)