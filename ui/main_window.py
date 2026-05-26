from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os

from analyzer.video_analyzer import VideoAnalyzer
from database.db import Database
from utils.exporters import export_analysis_csv, create_report_pdf

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """Canvas para mostrar gráficos de Matplotlib."""

    def __init__(self):
        self.figure = Figure(figsize=(8, 4))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FPS Analyzer - Analiza tu rendimiento")
        self.resize(1200, 800)
        
        self.analyzer = VideoAnalyzer()
        self.database = Database()
        self.current_data = None
        self.current_video_name = None
        
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz gráfica."""
        
        main_layout = QVBoxLayout()
        
        # Título
        title = QLabel("FPS Analyzer - Analiza tu rendimiento en juegos")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Análisis
        analysis_widget = self.create_analysis_tab()
        self.tabs.addTab(analysis_widget, "Análisis")
        
        # Tab 2: Historial
        history_widget = self.create_history_tab()
        self.tabs.addTab(history_widget, "Historial")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def create_analysis_tab(self):
        """Crea la pestaña de análisis."""
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("📁 Cargar vídeo FPS")
        self.btn_load.clicked.connect(self.load_video)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_export_csv = QPushButton("📊 Exportar CSV")
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_csv.setEnabled(False)
        btn_layout.addWidget(self.btn_export_csv)
        
        self.btn_export_pdf = QPushButton("📄 Exportar PDF")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_pdf.setEnabled(False)
        btn_layout.addWidget(self.btn_export_pdf)
        
        layout.addLayout(btn_layout)
        
        # Estadísticas
        self.stats = QLabel("Carga un vídeo para ver el análisis")
        self.stats.setAlignment(Qt.AlignTop)
        self.stats.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.stats)
        
        # Gráfico
        self.canvas = MplCanvas()
        layout.addWidget(self.canvas)
        
        widget.setLayout(layout)
        return widget

    def create_history_tab(self):
        """Crea la pestaña de historial."""
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        btn_refresh = QPushButton("🔄 Actualizar historial")
        btn_refresh.clicked.connect(self.refresh_history)
        layout.addWidget(btn_refresh)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Video", "FPS", "Duración (s)", "Movimiento Medio",
            "Estabilidad (%)", "Flicks", "Puntuación Tracking", "Fecha"
        ])
        layout.addWidget(self.history_table)
        
        widget.setLayout(layout)
        return widget

    def load_video(self):
        """Carga un vídeo y realiza el análisis."""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar vídeo",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov)"
        )

        if not file_path:
            return

        try:
            self.current_video_name = os.path.basename(file_path)
            result = self.analyzer.analyze(file_path)
            self.current_data = result
            
            self.update_stats(result)
            self.update_graph(result["motion_data"])
            
            # Guardar en base de datos
            self.database.save_analysis(result, self.current_video_name)
            
            # Habilitar exportación
            self.btn_export_csv.setEnabled(True)
            self.btn_export_pdf.setEnabled(True)
            
            # Actualizar historial
            self.refresh_history()
            self.tabs.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al analizar el vídeo: {str(e)}"
            )

    def update_stats(self, data):
        """Actualiza las estadísticas mostradas."""
        
        text = f"""
VÍDEO: {self.current_video_name}
─────────────────────────────────────
FPS: {data['fps']}
Duración: {data['duration']} segundos
Frames: {data['frames']}
─────────────────────────────────────
MOVIMIENTO:
  • Media: {data['avg_motion']}
  • Máximo: {data['max_motion']}
  • Estabilidad: {data['stability']}%
  • Flicks detectados: {data['flicks']}
─────────────────────────────────────
PUNTUACIONES:
  • Tracking: {data['tracking_score']}%
  • Picos de movimiento: {data['motion_peaks']}
  • Rating: {data['rating']}
"""
        
        self.stats.setText(text)

    def update_graph(self, motion_data):
        """Actualiza el gráfico de movimiento."""
        
        self.canvas.ax.clear()
        self.canvas.ax.plot(motion_data, linewidth=1.5, color='#2196F3')
        self.canvas.ax.fill_between(range(len(motion_data)), motion_data, alpha=0.3, color='#2196F3')
        self.canvas.ax.set_title("Movimiento de Cámara a lo largo del video", fontsize=14, fontweight='bold')
        self.canvas.ax.set_xlabel("Frame")
        self.canvas.ax.set_ylabel("Intensidad de Movimiento")
        self.canvas.ax.grid(True, alpha=0.3)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def export_csv(self):
        """Exporta el análisis a CSV."""
        
        if not self.current_data:
            QMessageBox.warning(self, "Advertencia", "No hay análisis para exportar")
            return
        
        try:
            export_analysis_csv(self.current_data, self.current_video_name)
            QMessageBox.information(self, "Éxito", "Análisis exportado a CSV correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")

    def export_pdf(self):
        """Exporta el análisis a PDF."""
        
        if not self.current_data:
            QMessageBox.warning(self, "Advertencia", "No hay análisis para exportar")
            return
        
        try:
            create_report_pdf(self.current_data, self.current_video_name)
            QMessageBox.information(self, "Éxito", "Reporte PDF generado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")

    def refresh_history(self):
        """Actualiza la tabla del historial."""
        
        analyses = self.database.get_all_analyses()
        self.history_table.setRowCount(len(analyses))
        
        for row, analysis in enumerate(analyses):
            items = [
                str(analysis[1]),  # video_name
                str(analysis[2]),  # fps
                str(analysis[3]),  # duration
                str(analysis[4]),  # avg_motion
                str(analysis[6]),  # stability
                str(analysis[7]),  # flicks
                "N/A",             # tracking_score (si quieres guardarlo, modificar DB)
                str(analysis[8])   # created_at
            ]
            
            for col, item in enumerate(items):
                self.history_table.setItem(row, col, QTableWidgetItem(item))
