"""
JUCC Dashboard - Sample Video Generator
Module: generate_sample_videos.py

Generates 4 high-definition (1280x720 @ 24fps) sample road videos with realistic
motion, textures, and anomalies for direct drag-and-drop testing in the Dashboard AI Video Lab:
1. rad_pothole_corridor.mp4
2. hit_and_run_intercept.mp4
3. school_zone_pedestrians.mp4
4. urban_traffic_pcu_flow.mp4
"""

import os
import cv2
import numpy as np


OUTPUT_DIR = "/Users/meydivyansh/dashboard/sample_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_writer(filename, fps=24, res=(1280, 720)):
    filepath = os.path.join(OUTPUT_DIR, filename)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    writer = cv2.VideoWriter(filepath, fourcc, fps, res)
    return writer, filepath


def draw_road_perspective(frame, f_idx, road_color=(45, 52, 48)):
    h, w = frame.shape[:2]
    # Sky / Horizon
    frame[:int(h * 0.38), :] = [60, 68, 62]

    # Road polygon
    pts = np.array([
        [int(w * 0.36), int(h * 0.38)],
        [int(w * 0.64), int(h * 0.38)],
        [w, h],
        [0, h]
    ], np.int32)
    cv2.fillPoly(frame, [pts], road_color)

    # Road curb / shoulders
    cv2.line(frame, (int(w * 0.36), int(h * 0.38)), (0, h), (100, 110, 105), 4)
    cv2.line(frame, (int(w * 0.64), int(h * 0.38)), (w, h), (100, 110, 105), 4)

    # Center Dashed Line
    dash_speed = (f_idx * 12) % 60
    for y_step in range(int(h * 0.38), h, 50):
        y1 = y_step + dash_speed
        y2 = y1 + 25
        if y1 > h:
            continue
        scale1 = (y1 - h * 0.38) / (h * 0.62)
        scale2 = (min(y2, h) - h * 0.38) / (h * 0.62)
        x1 = int(w * 0.5)
        x2 = int(w * 0.5)
        thick = max(2, int(scale1 * 8))
        cv2.line(frame, (x1, int(y1)), (x2, int(min(y2, h))), (230, 235, 230), thick)


def create_pothole_video(num_frames=120):
    writer, path = get_writer("rad_pothole_corridor.mp4")
    print(f"[*] Generating RAD Pothole Corridor Video ({num_frames} frames)...")

    for i in range(num_frames):
        frame = np.full((720, 1280, 3), 50, dtype=np.uint8)
        draw_road_perspective(frame, i)

        # Approaching Pothole 1 (starts distant, moves closer)
        progress1 = (i % 60) / 60.0
        y1 = int(720 * (0.42 + progress1 * 0.52))
        x1 = int(1280 * (0.58 + progress1 * 0.12))
        rx = max(10, int(progress1 * 95))
        ry = max(5, int(progress1 * 45))

        if 0.1 < progress1 < 0.95:
            # Asphalt crater
            cv2.ellipse(frame, (x1, y1), (rx, ry), 10, 0, 360, (20, 20, 20), -1)
            cv2.ellipse(frame, (x1, y1), (rx + 4, ry + 2), 10, 0, 360, (10, 10, 10), 2)
            # Water / Depth shadow
            cv2.ellipse(frame, (x1 - int(rx*0.2), y1 + int(ry*0.1)), (int(rx*0.6), int(ry*0.5)), 10, 0, 360, (12, 14, 15), -1)

        # Fissure / Longitudinal Crack on left lane
        progress2 = ((i + 30) % 60) / 60.0
        if 0.15 < progress2 < 0.90:
            y2 = int(720 * (0.40 + progress2 * 0.50))
            x2 = int(1280 * (0.42 - progress2 * 0.18))
            pts = np.array([
                [x2, y2],
                [x2 + int(progress2 * 20), y2 + int(progress2 * 40)],
                [x2 - int(progress2 * 10), y2 + int(progress2 * 80)],
                [x2 + int(progress2 * 30), y2 + int(progress2 * 120)]
            ], np.int32)
            cv2.polylines(frame, [pts], False, (18, 18, 18), max(2, int(progress2 * 5)))

        writer.write(frame)

    writer.release()
    print(f"[✓] Created: {path} ({os.path.getsize(path)/(1024*1024):.2f} MB)")


def create_hit_and_run_video(num_frames=120):
    writer, path = get_writer("hit_and_run_intercept.mp4")
    print(f"[*] Generating Hit & Run Intercept Video ({num_frames} frames)...")

    for i in range(num_frames):
        frame = np.full((720, 1280, 3), 48, dtype=np.uint8)
        draw_road_perspective(frame, i)

        # White SUV fleeing ahead
        progress = (i / float(num_frames))
        # SUV moves ahead rapidly with lateral sway
        y_pos = int(720 * (0.55 - progress * 0.12))
        x_pos = int(1280 * (0.50 + np.sin(i * 0.15) * 0.08))
        scale = 0.85 - progress * 0.25

        car_w = int(240 * scale)
        car_h = int(150 * scale)
        top_left = (x_pos - car_w // 2, y_pos - car_h)
        bottom_right = (x_pos + car_w // 2, y_pos)

        # SUV Chassis
        cv2.rectangle(frame, top_left, bottom_right, (235, 238, 240), -1)
        cv2.rectangle(frame, top_left, bottom_right, (40, 40, 40), 2)
        # Rear Windshield
        cv2.rectangle(frame, (top_left[0] + int(car_w*0.1), top_left[1] + int(car_h*0.1)),
                             (bottom_right[0] - int(car_w*0.1), top_left[1] + int(car_h*0.5)), (30, 40, 45), -1)
        # Tail Lights
        cv2.rectangle(frame, (top_left[0] + 5, top_left[1] + int(car_h*0.55)),
                             (top_left[0] + int(car_w*0.25), top_left[1] + int(car_h*0.75)), (0, 0, 220), -1)
        cv2.rectangle(frame, (bottom_right[0] - int(car_w*0.25), top_left[1] + int(car_h*0.55)),
                             (bottom_right[0] - 5, top_left[1] + int(car_h*0.75)), (0, 0, 220), -1)
        # Number Plate
        plate_tl = (x_pos - int(car_w*0.22), y_pos - int(car_h*0.35))
        plate_br = (x_pos + int(car_w*0.22), y_pos - int(car_h*0.12))
        cv2.rectangle(frame, plate_tl, plate_br, (250, 250, 250), -1)
        cv2.rectangle(frame, plate_tl, plate_br, (0, 0, 0), 1)
        if scale > 0.65:
            cv2.putText(frame, "RJ-14-CE-8821", (plate_tl[0] + 4, plate_br[1] - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35 * scale, (0, 0, 0), 1)

        writer.write(frame)

    writer.release()
    print(f"[✓] Created: {path} ({os.path.getsize(path)/(1024*1024):.2f} MB)")


def create_school_zone_video(num_frames=120):
    writer, path = get_writer("school_zone_pedestrians.mp4")
    print(f"[*] Generating School Zone Pedestrians Video ({num_frames} frames)...")

    for i in range(num_frames):
        frame = np.full((720, 1280, 3), 48, dtype=np.uint8)
        draw_road_perspective(frame, i)

        # Zebra Crossing Stripes
        zebra_y = int(720 * (0.68 + np.sin(i * 0.05) * 0.02))
        for zx in range(300, 980, 70):
            cv2.rectangle(frame, (zx, zebra_y), (zx + 40, zebra_y + 40), (220, 225, 220), -1)

        # School Pedestrians crossing
        ped_progress = (i / float(num_frames))
        ped_x = int(250 + ped_progress * 550)
        ped_y = zebra_y - 20

        # Pedestrian 1
        cv2.circle(frame, (ped_x, ped_y - 65), 14, (220, 190, 170), -1)  # Head
        cv2.rectangle(frame, (ped_x - 10, ped_y - 50), (ped_x + 10, ped_y), (180, 50, 50), -1)  # Uniform
        cv2.line(frame, (ped_x - 5, ped_y), (ped_x - 8, ped_y + 35), (20, 20, 20), 3)  # Legs
        cv2.line(frame, (ped_x + 5, ped_y), (ped_x + 8, ped_y + 35), (20, 20, 20), 3)

        # Pedestrian 2 (Child)
        c_x = ped_x - 30
        cv2.circle(frame, (c_x, ped_y - 45), 10, (220, 190, 170), -1)
        cv2.rectangle(frame, (c_x - 8, ped_y - 35), (c_x + 8, ped_y), (40, 120, 200), -1)
        cv2.line(frame, (c_x - 4, ped_y), (c_x - 6, ped_y + 25), (20, 20, 20), 2)
        cv2.line(frame, (c_x + 4, ped_y), (c_x + 6, ped_y + 25), (20, 20, 20), 2)

        # School Zone Warning Signboard on curb
        cv2.line(frame, (1050, 720), (1050, 480), (120, 120, 120), 6)
        cv2.rectangle(frame, (1010, 420), (1090, 480), (0, 215, 255), -1)
        cv2.putText(frame, "SCHOOL", (1018, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        cv2.putText(frame, "25 KM/H", (1018, 468), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)

        writer.write(frame)

    writer.release()
    print(f"[✓] Created: {path} ({os.path.getsize(path)/(1024*1024):.2f} MB)")


def create_traffic_flow_video(num_frames=120):
    writer, path = get_writer("urban_traffic_pcu_flow.mp4")
    print(f"[*] Generating Urban Traffic PCU Flow Video ({num_frames} frames)...")

    for i in range(num_frames):
        frame = np.full((720, 1280, 3), 48, dtype=np.uint8)
        draw_road_perspective(frame, i)

        # Auto Rickshaw in left lane
        auto_y = 520
        auto_x = int(320 + np.sin(i * 0.1) * 10)
        cv2.rectangle(frame, (auto_x - 60, auto_y - 90), (auto_x + 60, auto_y), (20, 200, 230), -1)
        cv2.rectangle(frame, (auto_x - 50, auto_y - 80), (auto_x + 50, auto_y - 45), (30, 40, 40), -1)
        cv2.rectangle(frame, (auto_x - 60, auto_y - 45), (auto_x + 60, auto_y), (20, 140, 40), -1)

        # Sedan Car in center lane
        car_y = 480
        car_x = int(640 + np.cos(i * 0.08) * 25)
        cv2.rectangle(frame, (car_x - 90, car_y - 80), (car_x + 90, car_y), (200, 80, 30), -1)
        cv2.rectangle(frame, (car_x - 70, car_y - 75), (car_x + 70, car_y - 40), (20, 20, 30), -1)

        # Two-Wheeler Motorbike in right lane (moving faster)
        bike_progress = (i * 1.5) % 120
        bike_y = int(720 * (0.42 + (bike_progress / 120.0) * 0.52))
        bike_x = int(1280 * (0.65 + (bike_progress / 120.0) * 0.15))
        b_scale = max(0.3, bike_progress / 120.0)

        bw = int(30 * b_scale)
        bh = int(60 * b_scale)
        cv2.rectangle(frame, (bike_x - bw, bike_y - bh), (bike_x + bw, bike_y), (40, 40, 220), -1)
        cv2.circle(frame, (bike_x, bike_y - bh - int(10*b_scale)), int(8*b_scale), (240, 200, 0), -1)  # Helmet

        writer.write(frame)

    writer.release()
    print(f"[✓] Created: {path} ({os.path.getsize(path)/(1024*1024):.2f} MB)")


def main():
    print("=" * 70)
    print("  GENERATING 4 SAMPLE TEST VIDEOS FOR DASHBOARD AI VIDEO LAB")
    print(f"  Destination Directory: {OUTPUT_DIR}")
    print("=" * 70)

    create_pothole_video(num_frames=120)
    create_hit_and_run_video(num_frames=120)
    create_school_zone_video(num_frames=120)
    create_traffic_flow_video(num_frames=120)

    print("\n[✓] All 4 sample videos created successfully in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
