import math
from typing import List, Dict

# Predefined high-density urban transit corridor routes
WAYPOINTS_MAP: Dict[str, List[List[float]]] = {
    "BUS-001": [[26.9239, 75.8267], [26.9150, 75.8180], [26.9050, 75.8050], [26.8920, 75.7950], [26.8850, 75.7900]],
    "BUS-002": [[26.8950, 75.7450], [26.8870, 75.7580], [26.8800, 75.7720], [26.8650, 75.7890], [26.8520, 75.8050]],
    "BUS-003": [[26.9124, 75.7873], [26.8920, 75.7980], [26.8720, 75.8080], [26.8450, 75.8150], [26.8200, 75.8250]],
    "BUS-004": [[26.9600, 75.7700], [26.9450, 75.7820], [26.9300, 75.7920], [26.9180, 75.8000], [26.9050, 75.8100]],
    "BUS-005": [[26.9200, 75.8300], [26.9120, 75.8450], [26.9000, 75.8600], [26.8850, 75.8750], [26.8700, 75.8900]],
    "BUS-006": [[26.9180, 75.7800], [26.9100, 75.7650], [26.9020, 75.7500], [26.8950, 75.7350], [26.8880, 75.7200]],
    "BUS-007": [[26.8600, 75.7700], [26.8500, 75.7850], [26.8400, 75.8000], [26.8300, 75.8150], [26.8200, 75.8300]],
    "BUS-008": [[26.9350, 75.7850], [26.9250, 75.7980], [26.9100, 75.8120], [26.8950, 75.8250], [26.8800, 75.8380]],
    "BUS-009": [[26.8750, 75.8200], [26.8650, 75.8350], [26.8550, 75.8500], [26.8450, 75.8650], [26.8350, 75.8800]],
    "BUS-010": [[26.9400, 75.8100], [26.9300, 75.8200], [26.9200, 75.8300], [26.9100, 75.8400], [26.9000, 75.8500]],
}

class FleetSimulator:
    """Simulates realistic GPS movement & velocity curves across 10 municipal transit corridors."""

    @staticmethod
    def get_interpolated_position(bus_id: str, step_fraction: float) -> Dict[str, float]:
        waypoints = WAYPOINTS_MAP.get(bus_id, WAYPOINTS_MAP["BUS-001"])
        num_segments = len(waypoints) - 1
        
        # Ping-pong loop calculation
        norm_t = (math.sin(step_fraction * 2 * math.pi) + 1.0) / 2.0
        segment_idx = min(int(norm_t * num_segments), num_segments - 1)
        local_t = (norm_t * num_segments) - segment_idx
        
        p1 = waypoints[segment_idx]
        p2 = waypoints[segment_idx + 1]
        
        lat = round(p1[0] + (p2[0] - p1[0]) * local_t, 6)
        lng = round(p1[1] + (p2[1] - p1[1]) * local_t, 6)
        speed = round(22.0 + 12.0 * math.cos(step_fraction * 4 * math.pi), 1)
        
        return {"lat": lat, "lng": lng, "speed": max(12.0, speed)}
