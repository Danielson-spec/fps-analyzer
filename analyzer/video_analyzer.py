import cv2
import numpy as np
from utils.metrics import calculate_tracking_score, calculate_motion_peaks


class VideoAnalyzer:

    def analyze(self, video_path):
        """Analiza un vídeo FPS y extrae métricas de movimiento."""
        
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("No se pudo abrir el vídeo")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        ret, prev_frame = cap.read()

        if not ret:
            raise Exception("No se pudo leer el vídeo")

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        motion_values = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(prev_gray, gray)
            motion_score = float(np.mean(diff))
            motion_values.append(motion_score)
            prev_gray = gray

        cap.release()

        if len(motion_values) == 0:
            motion_values = [0]

        # Cálculos de métricas
        avg_motion = np.mean(motion_values)
        max_motion = np.max(motion_values)
        flicks = sum(1 for x in motion_values if x > avg_motion * 2)
        
        stability = max(0, 100 - (np.std(motion_values) * 2))
        tracking_score = calculate_tracking_score(motion_values, avg_motion)
        motion_peaks = calculate_motion_peaks(motion_values, avg_motion)
        
        # Calificar basado en estabilidad
        if stability > 80:
            rating = "Excelente"
        elif stability > 60:
            rating = "Buena"
        elif stability > 40:
            rating = "Media"
        else:
            rating = "Mejorable"

        return {
            "fps": round(fps, 2),
            "duration": round(duration, 2),
            "frames": frame_count,
            "avg_motion": round(avg_motion, 2),
            "max_motion": round(max_motion, 2),
            "stability": round(stability, 2),
            "flicks": flicks,
            "tracking_score": round(tracking_score, 2),
            "motion_peaks": len(motion_peaks),
            "rating": rating,
            "motion_data": motion_values
        }
