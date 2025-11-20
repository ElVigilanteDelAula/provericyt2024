"""
Componente de visualización 3D del cerebro usando nilearn y plotly.
"""

import numpy as np
import plotly.graph_objects as go


def _compute_bounds(coords):
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]
    return {
        'x_min': float(x.min()),
        'x_max': float(x.max()),
        'y_min': float(y.min()),
        'y_max': float(y.max()),
        'z_min': float(z.min()),
        'z_max': float(z.max()),
    }


def _brain_span(bounds):
    return np.sqrt(
        (bounds['x_max'] - bounds['x_min']) ** 2
        + (bounds['y_max'] - bounds['y_min']) ** 2
        + (bounds['z_max'] - bounds['z_min']) ** 2
    )


def _normalize_metric(value):
    return (value - 50) * 6 / 50


def _coverage_radius(brain_span, coverage_factor, base_factor):
    return brain_span * base_factor * coverage_factor


def _apply_fade(intensity, coords, center, radius, multiplier):
    if radius <= 0:
        return

    distances = np.linalg.norm(coords - center, axis=1)
    mask = distances <= radius
    if not np.any(mask):
        return

    fade = (1 - distances[mask] / radius) * multiplier
    intensity[mask] += fade


def _center_parietal_left(bounds):
    return np.array([
        bounds['x_min'] + (bounds['x_max'] - bounds['x_min']) * 0.3,
        bounds['y_min'] + (bounds['y_max'] - bounds['y_min']) * 0.2,
        bounds['z_min'] + (bounds['z_max'] - bounds['z_min']) * 0.7,
    ])


def _center_frontal_left(bounds):
    return np.array([
        bounds['x_min'] + (bounds['x_max'] - bounds['x_min']) * 0.3,
        bounds['y_max'] - (bounds['y_max'] - bounds['y_min']) * 0.2,
        bounds['z_min'] + (bounds['z_max'] - bounds['z_min']) * 0.6,
    ])


def _center_front_midline(bounds):
    x_center = (bounds['x_min'] + bounds['x_max']) / 2
    return np.array([
        x_center * 0.4,
        bounds['y_min'] * -0.62,
        bounds['z_max'] * 0.21,
    ])


def _center_frontal_right(bounds):
    return np.array([
        bounds['x_max'] - (bounds['x_max'] - bounds['x_min']) * 0.3,
        bounds['y_max'] - (bounds['y_max'] - bounds['y_min']) * 0.2,
        bounds['z_min'] + (bounds['z_max'] - bounds['z_min']) * 0.6,
    ])


def _center_parietal_right(bounds):
    return np.array([
        bounds['x_max'] - (bounds['x_max'] - bounds['x_min']) * 0.3,
        bounds['y_min'] + (bounds['y_max'] - bounds['y_min']) * 0.2,
        bounds['z_min'] + (bounds['z_max'] - bounds['z_min']) * 0.7,
    ])


_SENSOR_CONFIG = {
    'sensor_a': [{'side': 'left', 'center_fn': _center_parietal_left, 'metric': 'attention', 'base_factor': 0.25}],
    'sensor_b': [{'side': 'left', 'center_fn': _center_frontal_left, 'metric': 'attention', 'base_factor': 0.25}],
    'sensor_c': [
        {'side': 'right', 'center_fn': _center_front_midline, 'metric': 'attention', 'base_factor': 0.2},
        {'side': 'left', 'center_fn': _center_front_midline, 'metric': 'attention', 'base_factor': 0.2},
    ],
    'sensor_d': [{'side': 'right', 'center_fn': _center_frontal_right, 'metric': 'meditation', 'base_factor': 0.25}],
    'sensor_e': [{'side': 'right', 'center_fn': _center_parietal_right, 'metric': 'meditation', 'base_factor': 0.25}],
}

class BrainVisualizer:
    """
    Visualizador 3D del cerebro usando datos de superficie de nilearn y plotly para el renderizado.
    """
    
    def __init__(self):
        """Inicializar el visualizador del cerebro con carga diferida."""
        self.fsaverage = None
        self.mesh_right = None
        self.mesh_left = None
        self.reference_map_right = None
        self.reference_map_left = None
        self.fig = None
        self.coords_right = None
        self.coords_left = None
        self.bounds_right = None
        self.bounds_left = None
        self.brain_span_right = 0.0
        self.brain_span_left = 0.0
        self._initialized = False
        
    def _lazy_init(self):
        """Inicialización diferida de los componentes de nilearn."""
        if self._initialized:
            return True
            
        try:
            from nilearn import datasets, surface
            
            # Cargar datos de superficie fsaverage
            self.fsaverage = datasets.fetch_surf_fsaverage()
            
            # Cargar datos de muestra de activación motora para referencia
            motor_img = datasets.load_sample_motor_activation_image()
            
            # Cargar mallas para ambos hemisferios
            self.mesh_right = surface.load_surf_mesh(self.fsaverage.pial_right)
            self.mesh_left = surface.load_surf_mesh(self.fsaverage.pial_left)
            
            # Obtener mapas de activación de referencia
            self.reference_map_right = surface.vol_to_surf(motor_img, self.mesh_right)
            self.reference_map_left = surface.vol_to_surf(motor_img, self.mesh_left)

            # Pre-calcular metadatos geométricos para minimizar trabajo posterior
            self.coords_right = self.mesh_right.coordinates
            self.coords_left = self.mesh_left.coordinates
            self.bounds_right = _compute_bounds(self.coords_right)
            self.bounds_left = _compute_bounds(self.coords_left)
            self.brain_span_right = _brain_span(self.bounds_right)
            self.brain_span_left = _brain_span(self.bounds_left)
            
            self._initialized = True
            return True
            
        except Exception as e:
            # Silently fail if nilearn components cannot be initialized
            return False
        
    def create_brain_figure(self, intensity_right=None, intensity_left=None, title_suffix=""):
        """
        Crear una figura 3D del cerebro con mapas de intensidad personalizados opcionales.
        
        Parámetros:
        - intensity_right: Valores de intensidad personalizados para el hemisferio derecho
        - intensity_left: Valores de intensidad personalizados para el hemisferio izquierdo
        
        Retorna:
        - plotly.graph_objects.Figure: Visualización 3D del cerebro
        """
        
        # Intentar inicializar componentes de nilearn
        if not self._lazy_init():
            return self._create_fallback_figure()
        
        # Usar intensidad proporcionada o usar referencia por defecto
        map_right = intensity_right if intensity_right is not None else self.reference_map_right
        map_left = intensity_left if intensity_left is not None else self.reference_map_left
        
        # Crear nueva figura
        fig = go.Figure()
        
        # Agregar hemisferio derecho con barra de color
        fig.add_trace(go.Mesh3d(
            x=self.mesh_right.coordinates[:, 0],
            y=self.mesh_right.coordinates[:, 1],
            z=self.mesh_right.coordinates[:, 2],
            i=self.mesh_right.faces[:, 0],
            j=self.mesh_right.faces[:, 1],
            k=self.mesh_right.faces[:, 2],
            intensity=map_right,
            colorscale="RdBu_r",  # Azul = negativo, Rojo = positivo
            cmin=-6,              # Escala mínima
            cmax=6,               # Escala máxima
            colorbar=dict(
                title=dict(text="Activación"),
                thickness=15,
                len=0.75
            ),
            showscale=True,
            name="Right Hemisphere",
            opacity=1
        ))
        
        # Agregar hemisferio izquierdo sin barra de color
        fig.add_trace(go.Mesh3d(
            x=self.mesh_left.coordinates[:, 0],
            y=self.mesh_left.coordinates[:, 1],
            z=self.mesh_left.coordinates[:, 2],
            i=self.mesh_left.faces[:, 0],
            j=self.mesh_left.faces[:, 1],
            k=self.mesh_left.faces[:, 2],
            intensity=map_left,
            colorscale="RdBu_r",
            cmin=-6,
            cmax=6,
            showscale=False,  # Evitar segunda barra de color
            name="Left Hemisphere",
            opacity=1
        ))
        
         # Actualizar diseño con configuración original y uirevision
        fig.update_layout(
            scene=dict(
               xaxis=dict(visible=False),
               yaxis=dict(visible=False),
               zaxis=dict(visible=False),
               bgcolor="white",
               uirevision="brain_camera"  # Mantener la posición de la cámara
            ),
           margin=dict(l=0, r=0, t=40, b=0),
           height=600,
           uirevision="brain_layout"  # Mantener el layout general
        )
        
        self.fig = fig
        return fig
        
    def _create_fallback_figure(self):
        """Crear una figura de respaldo cuando nilearn no está disponible."""
        fig = go.Figure()
        
        fig.add_annotation(
            text="Cerebro 3D no disponible<br>Instale nilearn para visualización completa",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=20)
        )
        
        fig.update_layout(
            title="Cerebro 3D - Modo Fallback",
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def update_brain_intensity(self, all_sensors_data):
        """
        Actualizar la intensidad del cerebro basada en datos EEG de todos los sensores con efecto de mapa de calor.
        Mapea cada sensor a regiones específicas del cerebro con:
        - Cobertura de área basada en signal_strength (señal más fuerte = área más grande)
        - Efecto de desvanecimiento radial (intensidad disminuye desde el centro hacia afuera)
        
        Mapeo de sensores basado en posiciones estándar de EEG:
        - Sensor A: P3 - Lóbulo Parietal Izquierdo
        - Sensor B: F3 - Corteza Frontal Izquierda 
        - Sensor C: FPz - Línea Media de la Frente
        - Sensor D: F4 - Corteza Frontal Derecha
        - Sensor E: P2 - Lóbulo Parietal Derecho
        
        Parámetros:
        - all_sensors_data: Diccionario con datos de todos los sensores
        
        Retorna:
        - tuple: (intensity_right, intensity_left) arreglos
        """
        if not self._initialized:
            return None, None

        intensity_right = np.zeros_like(self.reference_map_right)
        intensity_left = np.zeros_like(self.reference_map_left)

        side_data = {
            'left': {
                'intensity': intensity_left,
                'coords': self.coords_left,
                'bounds': self.bounds_left,
                'span': self.brain_span_left,
            },
            'right': {
                'intensity': intensity_right,
                'coords': self.coords_right,
                'bounds': self.bounds_right,
                'span': self.brain_span_right,
            },
        }

        for sensor_name, sensor_data in all_sensors_data.items():
            if sensor_name == 'uid' or not sensor_data:
                continue

            attention_norm = _normalize_metric(sensor_data.get('attention', 50))
            meditation_norm = _normalize_metric(sensor_data.get('meditation', 50))
            coverage_factor = (sensor_data.get('signal_strength', 50) / 100.0) * 0.9 + 0.1

            for config in _SENSOR_CONFIG.get(sensor_name, []):
                side = side_data.get(config['side'])
                if not side or side['span'] <= 0:
                    continue

                center = config['center_fn'](side['bounds'])
                radius = _coverage_radius(side['span'], coverage_factor, config['base_factor'])
                multiplier = attention_norm if config['metric'] == 'attention' else meditation_norm
                _apply_fade(side['intensity'], side['coords'], center, radius, multiplier)

        return intensity_right, intensity_left
    
    def create_live_brain_figure(self, all_sensors_data):
        """
        Crear figura del cerebro con datos EEG en vivo de los sensores.
        
        Parámetros:
        - all_sensors_data: Diccionario con datos de sensores (puede ser uno o múltiples sensores)
        
        Retorna:
        - plotly.graph_objects.Figure: Visualización 3D del cerebro actualizada
        """
        if not self._lazy_init():
            return self._create_fallback_figure()
            
        intensity_right, intensity_left = self.update_brain_intensity(all_sensors_data)
        
        # Determinar sufijo del título basado en los datos
        sensor_count = len([k for k in all_sensors_data.keys() if k != 'uid'])
        if sensor_count == 1:
            sensor_name = [k for k in all_sensors_data.keys() if k != 'uid'][0]
            title_suffix = f" - {sensor_name.upper()}"
        else:
            title_suffix = f" - Todos los Sensores ({sensor_count})"
            
        return self.create_brain_figure(intensity_right, intensity_left, title_suffix)
    
    def update_live_brain_intensity(self, all_sensors_data):
        """
        Actualizar solo la intensidad del cerebro para preservar la posición de la cámara.
        Retorna datos para actualización incremental sin recrear la figura.
        
        Parámetros:
        - all_sensors_data: Diccionario con datos de sensores
        
        Retorna:
        - dict: Datos de actualización para Plotly (formato extendData)
        """
        if not self._initialized:
            return None
            
        intensity_right, intensity_left = self.update_brain_intensity(all_sensors_data)
        
        if intensity_right is None or intensity_left is None:
            return None
            
        # Retornar datos de actualización en formato para Plotly extendData/restyle
        return {
            'intensity_right': intensity_right,
            'intensity_left': intensity_left,
            'trace_indices': [0, 1]  # Índices de las trazas del hemisferio derecho e izquierdo
        }

# Instancia global del visualizador de cerebro
brain_viz = BrainVisualizer()