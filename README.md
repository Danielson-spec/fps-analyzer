# FPS Analyzer

Analizador avanzado de rendimiento en videojuegos FPS. Carga tus grabaciones de gameplay y obtén métricas detalladas sobre movimiento de cámara, estabilidad y técnica de aim.

## Características

✅ **Análisis de Movimiento de Cámara**
- Detecta flicks y movimientos rápidos
- Calcula estabilidad y suavidad
- Mide intensidad de movimiento

✅ **Métricas Avanzadas**
- FPS y duración del vídeo
- Puntuación de tracking
- Picos de movimiento
- Rating automático

✅ **Historial y Exportación**
- Base de datos SQLite
- Exportación a CSV
- Generación de reportes PDF
- Historial de análisis

✅ **Interfaz Moderna**
- Interfaz gráfica con PySide6
- Gráficos interactivos con Matplotlib
- Diseño intuitivo y responsivo

## Requisitos

- Python 3.8+
- OpenCV
- PySide6
- Matplotlib
- Pandas
- ReportLab
- NumPy

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/Danielson-spec/fps-analyzer.git
cd fps-analyzer
```

2. Crea un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

### Workflow

1. **Abre la aplicación**
   - Se abre la ventana principal

2. **Carga un vídeo**
   - Click en "📁 Cargar vídeo FPS"
   - Selecciona un vídeo (.mp4, .avi, .mkv, .mov)
   - El análisis comienza automáticamente

3. **Visualiza los resultados**
   - Estadísticas detalladas en la pestaña "Análisis"
   - Gráfico de movimiento a lo largo del vídeo
   - Evaluación automática

4. **Exporta los resultados**
   - CSV para datos sin procesar
   - PDF para reportes formales

5. **Consulta el historial**
   - Pestaña "Historial" con todos los análisis previos

## Estructura del Proyecto

```
fps-analyzer/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
│
├── analyzer/
│   └── video_analyzer.py  # Lógica de análisis
│
├── ui/
│   └── main_window.py     # Interfaz gráfica
│
├── database/
│   └── db.py              # Gestión de base de datos
│
└── utils/
    ├── metrics.py         # Cálculos de métricas
    └── exporters.py       # Exportación a CSV/PDF
```

## Métricas Explicadas

### Movimiento Medio
Promedio de intensidad de cambio entre fotogramas. Valores bajos indican cámara estable.

### Movimiento Máximo
Pico de intensidad de movimiento en el vídeo completo. Indica el movimiento más brusco.

### Estabilidad (%)
Porcentaje que indica cuán consistente es el movimiento. Valores altos = cámara suave.

### Flicks
Número de movimientos rápidos detectados (por encima de 2x el promedio).

### Tracking Score (%)
Porcentaje de frames con movimiento suave (0.5x - 1.5x el promedio).

### Picos de Movimiento
Cantidad de momentos con cambios abruptos de cámara.

## Próximas Mejoras

- [ ] Comparación de múltiples vídeos
- [ ] Análisis de patrones de aim
- [ ] Recomendaciones automáticas
- [ ] Soporte para streaming en vivo
- [ ] Instalador .exe para Windows
- [ ] API REST para integración

## Licencia

MIT License - Ver LICENSE.txt para más detalles

## Contacto

Para soporte o sugerencias, abre un issue en GitHub.

---

**FPS Analyzer** - Mejora tu juego, analiza tu rendimiento. 🎮
