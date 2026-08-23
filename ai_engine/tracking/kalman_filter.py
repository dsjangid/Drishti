"""
JUCC Edge AI Engine - Kalman Filter State Estimator
Module: ai_engine/tracking/kalman_filter.py
Smart India Hackathon Problem Statement PS-26124

Maintains 2D bounding box spatial state [x, y, a, h, vx, vy, va, vh]
with constant velocity motion model for trajectory forecasting.
"""

import numpy as np


class KalmanBoxTracker:
    """
    Standard 8-dimensional state Kalman Filter for bounding box tracking.
    State: [cx, cy, aspect_ratio, height, v_cx, v_cy, v_aspect, v_height]
    """

    count = 0

    def __init__(self, bbox):
        # State vector: 8x1
        self.kf_mean = np.zeros((8, 1))
        # Initial measurement
        self.kf_mean[0:4, 0] = self._bbox_to_z(bbox)
        
        # State covariance
        self.kf_cov = np.eye(8) * 10.0
        self.kf_cov[4:, 4:] *= 100.0

        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def _bbox_to_z(self, bbox):
        """Converts [x, y, w, h] to [center_x, center_y, aspect_ratio, height]"""
        w = float(bbox[2])
        h = float(bbox[3])
        x = float(bbox[0]) + w / 2.0
        y = float(bbox[1]) + h / 2.0
        s = w / max(1.0, h)
        return np.array([x, y, s, h])

    def _z_to_bbox(self, state):
        """Converts [center_x, center_y, aspect_ratio, height] to [x, y, w, h]"""
        x, y, s, h = state[0], state[1], state[2], state[3]
        w = max(1.0, s * h)
        return [int(x - w / 2.0), int(y - h / 2.0), int(w), int(h)]

    def predict(self):
        """Advances state vector using constant velocity model."""
        # Simple velocity integration
        self.kf_mean[0] += self.kf_mean[4]
        self.kf_mean[1] += self.kf_mean[5]
        self.kf_mean[2] += self.kf_mean[6]
        self.kf_mean[3] += self.kf_mean[7]

        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(self._z_to_bbox(self.kf_mean[:4, 0]))
        return self.history[-1]

    def update(self, bbox):
        """Updates state with new observed detection."""
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        
        # Smooth measurement update
        z = self._bbox_to_z(bbox)
        residual = z - self.kf_mean[:4, 0]
        self.kf_mean[:4, 0] += 0.7 * residual
        self.kf_mean[4:, 0] = 0.3 * self.kf_mean[4:, 0] + 0.7 * (residual / max(1, self.time_since_update))

    def get_state(self):
        """Returns current [x, y, w, h] bounding box."""
        return self._z_to_bbox(self.kf_mean[:4, 0])
