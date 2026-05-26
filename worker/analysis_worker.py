from PySide6.QtCore import QThread, Signal
from analyzer.video_analyzer import VideoAnalyzer


class AnalysisWorker(QThread):
    """
    Worker thread para ejecutar el análisis de vídeo en segundo plano.
    Permite que la UI siga respondiendo durante el análisis.
    """
    
    # Señales
    progress = Signal(int)  # Emite progreso (0-100)
    finished = Signal(dict)  # Emite resultados cuando termina
    error = Signal(str)  # Emite error si algo falla

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.analyzer = VideoAnalyzer()

    def run(self):
        """
        Ejecuta el análisis del vídeo en este thread.
        Emite señales de progreso y resultados.
        """
        try:
            # Ejecutar análisis con callback de progreso
            result = self.analyzer.analyze(
                self.video_path,
                progress_callback=self.progress.emit
            )
            
            # Emitir resultados
            self.finished.emit(result)
            
        except Exception as e:
            # Emitir error
            self.error.emit(str(e))
