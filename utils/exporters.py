import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os


def export_analysis_csv(data, video_name):
    """Exporta el análisis a un archivo CSV."""
    
    export_data = {
        "Video": [video_name],
        "FPS": [data["fps"]],
        "Duración (s)": [data["duration"]],
        "Frames": [data["frames"]],
        "Movimiento Medio": [data["avg_motion"]],
        "Movimiento Máximo": [data["max_motion"]],
        "Estabilidad (%)": [data["stability"]],
        "Flicks": [data["flicks"]],
        "Tracking Score (%)": [data["tracking_score"]],
        "Picos de Movimiento": [data["motion_peaks"]],
        "Rating": [data["rating"]],
        "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }
    
    df = pd.DataFrame(export_data)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}.csv"
    
    df.to_csv(filename, index=False)
    return filename


def create_report_pdf(data, video_name):
    """Crea un reporte PDF del análisis."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=(8.5*inch, 11*inch))
    styles = getSampleStyleSheet()
    
    # Estilo personalizado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2196F3'),
        spaceAfter=30,
        alignment=1  # Centro
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    content = []
    
    # Título
    content.append(Paragraph("FPS Analyzer Report", title_style))
    content.append(Spacer(1, 12))
    
    # Información del vídeo
    content.append(Paragraph("Información del Vídeo", heading_style))
    
    video_data = [
        ["Archivo", video_name],
        ["FPS", str(data["fps"])],
        ["Duración", f"{data['duration']} segundos"],
        ["Frames", str(data["frames"])],
        ["Fecha de análisis", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    video_table = Table(video_data, colWidths=[2*inch, 4*inch])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    content.append(video_table)
    content.append(Spacer(1, 12))
    
    # Métricas de movimiento
    content.append(Paragraph("Métricas de Movimiento", heading_style))
    
    metrics_data = [
        ["Movimiento Medio", str(data["avg_motion"])],
        ["Movimiento Máximo", str(data["max_motion"])],
        ["Estabilidad", f"{data['stability']}%"],
        ["Flicks Detectados", str(data["flicks"])],
        ["Tracking Score", f"{data['tracking_score']}%"],
        ["Picos de Movimiento", str(data["motion_peaks"])]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 4*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3E5F5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    content.append(metrics_table)
    content.append(Spacer(1, 12))
    
    # Evaluación
    content.append(Paragraph("Evaluación", heading_style))
    content.append(Paragraph(f"<b>Rating:</b> {data['rating']}", styles['Normal']))
    content.append(Spacer(1, 12))
    
    content.append(Paragraph(
        f"<i>Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
        styles['Normal']
    ))
    
    doc.build(content)
    return filename
