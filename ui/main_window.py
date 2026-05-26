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
    QTableWidgetItem,
    QProgressBar
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os

from analyzer.video_analyzer import VideoAnalyzer
from worker.analysis_worker import AnalysisWorker
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
        self.worker_thread = None
        
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
        
        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Etiqueta de estado
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
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
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels([
            "Video", "FPS", "Duración (s)", "Avg Flow",
            "Max Flow", "Estabilidad (%)", "Flicks", 
            "Tracking (%)", "Rating", "Fecha"
        ])
        layout.addWidget(self.history_table)
        
        widget.setLayout(layout)
        return widget

    def load_video(self):
        """Carga un vídeo y realiza el análisis en un thread separado."""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar vídeo",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov)"
        )

        if not file_path:
            return

        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        self.status_label.setText("Analizando vídeo...")
        self.btn_load.setEnabled(False)
        
        # Crear y ejecutar worker thread
        self.worker_thread = AnalysisWorker(file_path)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_analysis_finished)
        self.worker_thread.error.connect(self.on_analysis_error)
        self.worker_thread.start()
        
        self.current_video_name = os.path.basename(file_path)

    def update_progress(self, progress_value):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(progress_value)
        self.status_label.setText(f"Analizando vídeo... {progress_value}%")

    def on_analysis_finished(self, result):
        """Se ejecuta cuando el análisis termina."""
        try:
            self.current_data = result
            
            self.update_stats(result)
            self.update_graph(result)
            
            # Guardar en base de datos
            self.database.save_analysis(result, self.current_video_name)
            
            # Habilitar exportación
            self.btn_export_csv.setEnabled(True)
            self.btn_export_pdf.setEnabled(True)
            
            # Actualizar historial
            self.refresh_history()
            
            # Ocultar progreso
            self.progress_bar.setVisible(False)
            self.status_label.setText("✅ Análisis completado")
            self.status_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")
            
            # Volver a habilitar botón
            self.btn_load.setEnabled(True)
            
            # Ir a pestaña de análisis
            self.tabs.setCurrentIndex(0)
            
        except Exception as e:
            self.on_analysis_error(str(e))

    def on_analysis_error(self, error_msg):
        """Maneja errores del análisis."""
        QMessageBox.critical(
            self,
            "Error",
            f"Error al analizar el vídeo: {error_msg}"
        )
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.btn_load.setEnabled(True)

    def update_stats(self, data):
        """Actualiza las estadísticas mostradas."""
        
        text = f"""
VÍDEO: {self.current_video_name}
{'─' * 50}
INFORMACIÓN:
  • FPS: {data['fps']}
  • Duración: {data['duration']} segundos
  • Frames: {data['frames']}

{'─' * 50}
MOVIMIENTO (Optical Flow):
  • Flujo Promedio: {data['avg_flow']}
  • Flujo Máximo: {data['max_flow']}
  • Desviación Estándar: {data['std_flow']}
  • Estabilidad: {data['stability']}%
  • Flicks detectados: {data['flicks']}

{'─' * 50}
PUNTUACIONES:
  • Tracking: {data['tracking_score']}%
  • Picos de movimiento: {data['motion_peaks']}
  • Cambios bruscos: {data['sharp_changes']}
  • Rating: {data['rating']}
"""
        
        self.stats.setText(text)

    def update_graph(self, data):
        """Actualiza el gráfico de movimiento con Optical Flow."""
        
        self.canvas.ax.clear()
        
        # Graficar flujo óptico (principal)
        self.canvas.ax.plot(
            data['flow_data'],
            linewidth=2,
            color='#2196F3',
            label='Optical Flow'
        )
        self.canvas.ax.fill_between(
            range(len(data['flow_data'])),
            data['flow_data'],
            alpha=0.3,
            color='#2196F3'
        )
        
        # Marcar cambios bruscos
        if data['sharp_change_indices']:
            sharp_y = [data['flow_data'][i] for i in data['sharp_change_indices']]
            self.canvas.ax.scatter(
                data['sharp_change_indices'],
                sharp_y,
                color='red',
                s=50,
                marker='v',
                label='Cambios Bruscos',
                zorder=5
            )
        
        self.canvas.ax.set_title(
            "Movimiento de Cámara (Optical Flow) a lo largo del video",
            fontsize=14,
            fontweight='bold'
        )
        self.canvas.ax.set_xlabel("Frame")
        self.canvas.ax.set_ylabel("Magnitud de Flujo Óptico")
        self.canvas.ax.grid(True, alpha=0.3)
        self.canvas.ax.legend(loc='upper right')
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
                str(analysis[4]),  # avg_motion (ahora avg_flow)
                str(analysis[5]),  # max_motion (ahora max_flow)
                str(analysis[6]),  # stability
                str(analysis[7]),  # flicks
                "N/A",             # tracking_score
                "N/A",             # rating
                str(analysis[8])   # created_at
            ]
            
            for col, item in enumerate(items):
                self.history_table.setItem(row, col, QTableWidgetItem(item))
