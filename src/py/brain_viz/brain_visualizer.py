"""
Componente de visualización 3D del cerebro usando nilearn y plotly.
"""

import numpy as np
import plotly.graph_objects as go

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
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Advertencia: No se pudieron inicializar los componentes de nilearn: {e}")
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
            
        # Inicializar mapas de intensidad con ceros
        intensity_right = np.zeros_like(self.reference_map_right)
        intensity_left = np.zeros_like(self.reference_map_left)
        
        # Obtener coordenadas de malla del cerebro para mapeo de regiones
        coords_right = self.mesh_right.coordinates
        coords_left = self.mesh_left.coordinates
        
        # Calcular límites del cerebro para mapeo de regiones
        x_min_r, x_max_r = coords_right[:, 0].min(), coords_right[:, 0].max()
        y_min_r, y_max_r = coords_right[:, 1].min(), coords_right[:, 1].max()
        z_min_r, z_max_r = coords_right[:, 2].min(), coords_right[:, 2].max()
        
        x_min_l, x_max_l = coords_left[:, 0].min(), coords_left[:, 0].max()
        y_min_l, y_max_l = coords_left[:, 1].min(), coords_left[:, 1].max()
        z_min_l, z_max_l = coords_left[:, 2].min(), coords_left[:, 2].max()
        
        # Dimensiones del cerebro para cálculos de distancia
        brain_size_r = np.sqrt((x_max_r - x_min_r)**2 + (y_max_r - y_min_r)**2 + (z_max_r - z_min_r)**2)
        brain_size_l = np.sqrt((x_max_l - x_min_l)**2 + (y_max_l - y_min_l)**2 + (z_max_l - z_min_l)**2)
        
        # Procesar cada sensor
        for sensor_name, sensor_data in all_sensors_data.items():
            if sensor_name == 'uid':  # Omitir campo uid
                continue
                
            # Extraer valores del sensor
            attention = sensor_data.get('attention', 50)
            meditation = sensor_data.get('meditation', 50)
            signal_strength = sensor_data.get('signal_strength', 50)
            
            # Normalizar atención y meditación al rango -6 a 6
            attention_norm = (attention - 50) * 6 / 50
            meditation_norm = (meditation - 50) * 6 / 50
            
            # La fuerza de la señal controla la cobertura del área (0-100 → 0.1-1.0)
            coverage_factor = (signal_strength / 100.0) * 0.9 + 0.1  # Mín 10%, Máx 100%
            
            # Mapear sensores a regiones del cerebro con efecto de mapa de calor basado en posiciones estándar de EEG
            if sensor_name == 'sensor_a':  # P3 - Lóbulo Parietal Izquierdo
                # Definir punto central para posición P3 (parietal izquierdo - región posterior)
                center_l = np.array([x_min_l + (x_max_l - x_min_l) * 0.3, 
                                   y_min_l + (y_max_l - y_min_l) * 0.2,  # Posterior (atrás)
                                   z_min_l + (z_max_l - z_min_l) * 0.7])
                
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.25 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * attention_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_b':  # F3 - Corteza Frontal Izquierda
                # Definir punto central para posición F3 (frontal izquierdo - región anterior)
                center_l = np.array([x_min_l + (x_max_l - x_min_l) * 0.3, 
                                   y_max_l - (y_max_l - y_min_l) * 0.2,  # Anterior (frente)
                                   z_min_l + (z_max_l - z_min_l) * 0.6])
                
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.25 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * attention_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_c':  # FPz - Línea Media de la Frente (Tierra)
                # Definir puntos centrales para posición FPz (frontal de línea media - muy adelante)
                center_r = np.array([((x_min_r + x_max_r) / 2) * 0.4, 
                                   (y_max_r - (y_max_r - y_min_r)) * -0.62,  # Muy anterior (frente)
                                   z_max_r * 0.21])  # Parte superior del cerebro
                center_l = np.array([((x_min_l + x_max_l) / 2) * 0.4, 
                                  ( y_max_l - (y_max_l - y_min_l)) * -0.62 ,  # Muy anterior (frente)
                                   z_max_l * 0.21])  # Parte superior del cerebro
                 # Aplicar al hemisferio derecho
                distances_r = np.sqrt(np.sum((coords_right - center_r)**2, axis=1))
                max_distance_r = brain_size_r * 0.2 * coverage_factor
                
                fade_mask_r = distances_r <= max_distance_r
                fade_intensity_r = np.zeros_like(distances_r)
                fade_intensity_r[fade_mask_r] = (1 - distances_r[fade_mask_r] / max_distance_r) * attention_norm
                intensity_right += fade_intensity_r
                
                # Aplicar al hemisferio izquierdo
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.2 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * attention_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_d':  # F4 - Corteza Frontal Derecha
                # Definir punto central para posición F4 (frontal derecho - región anterior)
                center_r = np.array([x_max_r - (x_max_r - x_min_r) * 0.3, 
                                   y_max_r - (y_max_r - y_min_r) * 0.2,  # Anterior (frente)
                                   z_min_r + (z_max_r - z_min_r) * 0.6])
                
                distances_r = np.sqrt(np.sum((coords_right - center_r)**2, axis=1))
                max_distance_r = brain_size_r * 0.25 * coverage_factor
                
                fade_mask_r = distances_r <= max_distance_r
                fade_intensity_r = np.zeros_like(distances_r)
                fade_intensity_r[fade_mask_r] = (1 - distances_r[fade_mask_r] / max_distance_r) * meditation_norm
                intensity_right += fade_intensity_r
                
            elif sensor_name == 'sensor_e':  # P2 - Lóbulo Parietal Derecho (entre Pz y T6)
                # Definir punto central para posición P2 (parietal derecho - región posterior)
                center_r = np.array([x_max_r - (x_max_r - x_min_r) * 0.3, 
                                   y_min_r + (y_max_r - y_min_r) * 0.2,  # Posterior (atrás)
                                   z_min_r + (z_max_r - z_min_r) * 0.7])
                
                distances_r = np.sqrt(np.sum((coords_right - center_r)**2, axis=1))
                max_distance_r = brain_size_r * 0.25 * coverage_factor
                
                fade_mask_r = distances_r <= max_distance_r
                fade_intensity_r = np.zeros_like(distances_r)
                fade_intensity_r[fade_mask_r] = (1 - distances_r[fade_mask_r] / max_distance_r) * meditation_norm
                intensity_right += fade_intensity_r
        
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