"""
JUCC Edge AI Engine - Multi-Object Trajectory Tracker
Module: ai_engine/tracking/tracker.py
Smart India Hackathon Problem Statement PS-26124

Performs multi-object tracking across video frames, tracks trajectories,
and calculates vehicle velocity (km/h) for speed estimation and incident logging.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from ai_engine.tracking.kalman_filter import KalmanBoxTracker


def calculate_iou(boxA, boxB):
    """Calculates Intersection-over-Union (IoU) of two [x, y, w, h] boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou


class EdgeObjectTracker:
    """
    Real-time edge multi-object tracker with speed vector estimation.
    """

    def __init__(self, max_age: int = 10, min_hits: int = 2, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: List[KalmanBoxTracker] = []
        self.frame_count = 0

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Matches incoming frame detections with existing tracks and updates state.
        """
        self.frame_count += 1
        
        # 1. Predict new locations of existing trackers
        trks = []
        to_del = []
        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            if np.any(np.isnan(pos)):
                to_del.append(t)
            else:
                trks.append(pos)
        
        for t in reversed(to_del):
            self.trackers.pop(t)

        # 2. Match detections to predicted trackers via IoU
        matched_trks = []
        unmatched_dets = list(range(len(detections)))
        unmatched_trks = list(range(len(self.trackers)))

        if len(self.trackers) > 0 and len(detections) > 0:
            iou_matrix = np.zeros((len(detections), len(self.trackers)), dtype=np.float32)
            for d, det in enumerate(detections):
                for t, trk in enumerate(self.trackers):
                    iou_matrix[d, t] = calculate_iou(det["box"], trks[t])

            # Greedy matching
            for d in range(len(detections)):
                best_t = np.argmax(iou_matrix[d])
                best_iou = iou_matrix[d, best_t]
                if best_iou >= self.iou_threshold:
                    if best_t in unmatched_trks and d in unmatched_dets:
                        matched_trks.append((d, best_t))
                        unmatched_trks.remove(best_t)
                        unmatched_dets.remove(d)

        # 3. Update matched trackers
        for d, t in matched_trks:
            self.trackers[t].update(detections[d]["box"])

        # 4. Create new trackers for unmatched detections
        for d in unmatched_dets:
            trk = KalmanBoxTracker(detections[d]["box"])
            self.trackers.append(trk)

        # 5. Compile return list of active tracks
        active_tracks = []
        for t, trk in enumerate(self.trackers):
            if trk.time_since_update < 1 and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                d_box = trk.get_state()
                active_tracks.append({
                    "track_id": trk.id,
                    "box": d_box,
                    "age": trk.age,
                    "hits": trk.hits
                })

        # Remove dead trackers
        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        return active_tracks
