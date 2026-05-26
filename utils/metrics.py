import numpy as np


def calculate_motion_peaks(motion_values, avg_motion):
    """Calcula los picos de movimiento por encima del umbral."""
    
    motion_peaks = []
    threshold = avg_motion * 2
    
    for index, value in enumerate(motion_values):
        if value > threshold:
            motion_peaks.append(index)
    
    return motion_peaks


def calculate_tracking_score(motion_values, avg_motion):
    """
    Calcula la puntuación de tracking (movimiento suave).
    Mide el porcentaje de frames con movimiento consistente.
    """
    
    smooth_frames = 0
    
    for value in motion_values:
        if avg_motion * 0.5 < value < avg_motion * 1.5:
            smooth_frames += 1
    
    tracking_score = (smooth_frames / len(motion_values)) * 100 if len(motion_values) > 0 else 0
    
    return tracking_score


def calculate_optical_flow_magnitude(flow_data):
    """
    Calcula estadísticas de magnitud de flujo óptico.
    
    Args:
        flow_data (list): Lista de magnitudes de flujo
    
    Returns:
        dict: Estadísticas de flujo
    """
    
    if not flow_data:
        return {
            'mean': 0,
            'max': 0,
            'min': 0,
            'std': 0
        }
    
    return {
        'mean': float(np.mean(flow_data)),
        'max': float(np.max(flow_data)),
        'min': float(np.min(flow_data)),
        'std': float(np.std(flow_data))
    }


def get_stability_rating(stability):
    """Obtiene una calificación basada en la estabilidad."""
    
    if stability > 80:
        return "Excelente"
    elif stability > 60:
        return "Buena"
    elif stability > 40:
        return "Media"
    else:
        return "Mejorable"


def detect_events(flow_magnitudes, threshold_multiplier=2.5):
    """
    Detecta eventos de movimiento brusco (cambios de cámara rápidos).
    Útil para identificar momentos de acción o enfrentamientos.
    
    Args:
        flow_magnitudes (list): Magnitudes de flujo óptico
        threshold_multiplier (float): Multiplicador para el umbral
    
    Returns:
        list: Índices de eventos detectados
    """
    
    if not flow_magnitudes:
        return []
    
    avg = np.mean(flow_magnitudes)
    threshold = avg * threshold_multiplier
    
    events = [i for i, value in enumerate(flow_magnitudes) if value > threshold]
    
    return events
