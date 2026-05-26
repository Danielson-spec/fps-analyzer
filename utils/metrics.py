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
    """Calcula la puntuación de tracking (movimiento suave)."""
    
    smooth_frames = 0
    
    for value in motion_values:
        if avg_motion * 0.5 < value < avg_motion * 1.5:
            smooth_frames += 1
    
    tracking_score = (smooth_frames / len(motion_values)) * 100 if len(motion_values) > 0 else 0
    
    return tracking_score


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
