import cv2
import numpy as np
from utils.metrics import (
    calculate_tracking_score,
    calculate_motion_peaks,
    calculate_optical_flow_magnitude
)


class VideoAnalyzer:
    """Analizador de vídeos FPS con Optical Flow."""

    def analyze(self, video_path, progress_callback=None):
        """
        Analiza un vídeo FPS y extrae métricas de movimiento usando Optical Flow.
        
        Args:
            video_path (str): Ruta del vídeo a analizar
            progress_callback (callable): Función para reportar progreso (0-100)
        
        Returns:
            dict: Diccionario con todas las métricas calculadas
        """
        
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("No se pudo abrir el vídeo")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        ret, prev_frame = cap.read()

        if not ret:
            raise Exception("No se pudo leer el vídeo")

        # Convertir a escala de grises para Optical Flow
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        motion_values = []
        flow_magnitudes = []
        flow_directions = []
        
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ===== MÉTODO 1: absdiff (mantenido para comparación) =====
            diff = cv2.absdiff(prev_gray, gray)
            motion_score = float(np.mean(diff))
            motion_values.append(motion_score)
            
            # ===== MÉTODO 2: Optical Flow (NUEVO - Principal) =====
            try:
                # Calcular flujo óptico Farneback
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray,
                    gray,
                    None,
                    pyr_scale=0.5,
                    levels=3,
                    winsize=15,
                    iterations=3,
                    n8=5,
                    poly_n=5,
                    poly_sigma=1.2,
                    flags=0
                )
                
                # Calcular magnitud y dirección del flujo
                magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                
                # Promediar magnitud (velocidad del movimiento)
                flow_magnitude = float(np.mean(magnitude))
                flow_magnitudes.append(flow_magnitude)
                
                # Calcular dirección dominante (en grados)
                mean_angle = float(np.degrees(np.mean(angle)))
                flow_directions.append(mean_angle)
                
            except Exception as e:
                # Si falla Optical Flow, usar 0
                flow_magnitudes.append(0)
                flow_directions.append(0)
            
            prev_gray = gray
            frame_index += 1
            
            # Reportar progreso
            if progress_callback:
                progress = int((frame_index / frame_count) * 100)
                progress_callback(progress)

        cap.release()

        if len(flow_magnitudes) == 0:
            flow_magnitudes = [0]
        if len(motion_values) == 0:
            motion_values = [0]

        # ===== CÁLCULOS CON OPTICAL FLOW (Principal) =====
        avg_flow = np.mean(flow_magnitudes)
        max_flow = np.max(flow_magnitudes)
        std_flow = np.std(flow_magnitudes)
        
        # Flicks detectados (cambios bruscos en flujo óptico)
        flicks = sum(1 for x in flow_magnitudes if x > avg_flow * 2.5)
        
        # Estabilidad basada en Optical Flow
        stability = max(0, 100 - (std_flow * 3))
        
        # Tracking score mejorado
        tracking_score = calculate_tracking_score(flow_magnitudes, avg_flow)
        
        # Picos de movimiento
        motion_peaks = calculate_motion_peaks(flow_magnitudes, avg_flow)
        
        # Detección de cambios bruscos (eventos)
        sharp_changes = self._detect_sharp_changes(flow_magnitudes, avg_flow)
        
        # Calificar basado en estabilidad y flujo
        if stability > 80 and max_flow < avg_flow * 3:
            rating = "Excelente"
        elif stability > 60 and max_flow < avg_flow * 4:
            rating = "Buena"
        elif stability > 40:
            rating = "Media"
        else:
            rating = "Mejorable"

        return {
            # Información del vídeo
            "fps": round(fps, 2),
            "duration": round(duration, 2),
            "frames": frame_count,
            
            # Métricas Optical Flow (Principal)
            "avg_flow": round(avg_flow, 2),
            "max_flow": round(max_flow, 2),
            "std_flow": round(std_flow, 2),
            
            # Métricas antiguas (para compatibilidad)
            "avg_motion": round(np.mean(motion_values), 2),
            "max_motion": round(np.max(motion_values), 2),
            
            # Estabilidad y evaluación
            "stability": round(stability, 2),
            "flicks": flicks,
            "tracking_score": round(tracking_score, 2),
            "motion_peaks": len(motion_peaks),
            "sharp_changes": len(sharp_changes),
            "rating": rating,
            
            # Datos para gráficos
            "motion_data": motion_values,
            "flow_data": flow_magnitudes,
            "flow_directions": flow_directions,
            "sharp_change_indices": sharp_changes
        }
    
    def _detect_sharp_changes(self, flow_magnitudes, avg_flow, threshold_multiplier=2.5):
        """
        Detecta cambios bruscos en el flujo óptico.
        Útil para identificar momentos de acción o enfrentamientos.
        
        Args:
            flow_magnitudes (list): Lista de magnitudes de flujo
            avg_flow (float): Promedio de flujo
            threshold_multiplier (float): Multiplicador para el umbral
        
        Returns:
            list: Índices donde ocurren cambios bruscos
        """
        sharp_changes = []
        threshold = avg_flow * threshold_multiplier
        
        for index, value in enumerate(flow_magnitudes):
            if value > threshold:
                sharp_changes.append(index)
        
        return sharp_changes
