"""
Brain 3D visualization component - VERSIÓN SIMPLE
Mantiene el modelo exacto de test3.py con opción de mostrar marcadores de sensores
"""

import numpy as np
import plotly.graph_objects as go

class BrainVisualizer:
    """
    3D Brain visualizer - versión simplificada que mantiene el modelo original
    """
    
    def __init__(self):
        """Initialize the brain visualizer with lazy loading."""
        self.fsaverage = None
        self.mesh_right = None
        self.mesh_left = None
        self.reference_map_right = None
        self.reference_map_left = None
        self.fig = None
        self._initialized = False
        
    def _lazy_init(self):
        """Lazy initialization of nilearn components."""
        if self._initialized:
            return True
            
        try:
            from nilearn import datasets, surface
            
            # Load fsaverage surface data (exactly like test3.py)
            self.fsaverage = datasets.fetch_surf_fsaverage()
            motor_img = datasets.load_sample_motor_activation_image()
            
            # Load meshes for both hemispheres (exactly like test3.py)
            self.mesh_right = surface.load_surf_mesh(self.fsaverage.pial_right)
            self.mesh_left = surface.load_surf_mesh(self.fsaverage.pial_left)
            
            # Get reference activation maps (exactly like test3.py)
            self.reference_map_right = surface.vol_to_surf(motor_img, self.mesh_right)
            self.reference_map_left = surface.vol_to_surf(motor_img, self.mesh_left)
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Warning: Could not initialize nilearn components: {e}")
            return False
    
    def create_brain_figure_original(self):
        """
        Create the EXACT same brain figure as test3.py
        """
        if not self._lazy_init():
            return self._create_fallback_figure()
        
        # Create figure exactly like test3.py
        fig = go.Figure()
        
        # Add right hemisphere with colorbar (exactly like test3.py)
        fig.add_trace(go.Mesh3d(
            x=self.mesh_right.coordinates[:, 0],
            y=self.mesh_right.coordinates[:, 1],
            z=self.mesh_right.coordinates[:, 2],
            i=self.mesh_right.faces[:, 0],
            j=self.mesh_right.faces[:, 1],
            k=self.mesh_right.faces[:, 2],
            intensity=self.reference_map_right,
            colorscale="RdBu_r",
            cmin=-6,
            cmax=6,
            colorbar=dict(
                title=dict(text="Activación"),
                thickness=15,
                len=0.75
            ),
            showscale=True,
            name="Right Hemisphere",
            opacity=1
        ))
        
        # Add left hemisphere without colorbar (exactly like test3.py)
        fig.add_trace(go.Mesh3d(
            x=self.mesh_left.coordinates[:, 0],
            y=self.mesh_left.coordinates[:, 1],
            z=self.mesh_left.coordinates[:, 2],
            i=self.mesh_left.faces[:, 0],
            j=self.mesh_left.faces[:, 1],
            k=self.mesh_left.faces[:, 2],
            intensity=self.reference_map_left,
            colorscale="RdBu_r",
            cmin=-6,
            cmax=6,
            showscale=False,
            name="Left Hemisphere",
            opacity=1
        ))
        
        # Layout exactly like test3.py
        fig.update_layout(
            title="Cerebro 3D - Visualización EEG en Tiempo Real",
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def add_sensor_markers_to_figure(self, fig):
        """
        Agrega marcadores de sensores a una figura existente (OPCIONAL)
        """
        if not self._initialized:
            return fig
            
        try:
            # Get brain bounds for marker positioning
            coords_right = self.mesh_right.coordinates
            coords_left = self.mesh_left.coordinates
            
            x_min_r, x_max_r = coords_right[:, 0].min(), coords_right[:, 0].max()
            y_min_r, y_max_r = coords_right[:, 1].min(), coords_right[:, 1].max()
            z_min_r, z_max_r = coords_right[:, 2].min(), coords_right[:, 2].max()
            
            x_min_l, x_max_l = coords_left[:, 0].min(), coords_left[:, 0].max()
            y_min_l, y_max_l = coords_left[:, 1].min(), coords_left[:, 1].max()
            z_min_l, z_max_l = coords_left[:, 2].min(), coords_left[:, 2].max()
            
            # Simple sensor positions
            sensors = [
                # Sensor A - Centro
                {
                    'name': 'Sensor A',
                    'color': 'gold', 
                    'x': (x_min_r + x_max_r) / 2,
                    'y': (y_min_r + y_max_r) / 2, 
                    'z': (z_min_r + z_max_r) / 2
                },
                # Sensor B - Superior izquierdo
                {
                    'name': 'Sensor B',
                    'color': 'lime',
                    'x': (x_min_l + x_max_l) / 2,
                    'y': y_max_l * 0.9,
                    'z': z_min_l + (z_max_l - z_min_l) * 0.8
                },
                # Sensor C - Superior derecho
                {
                    'name': 'Sensor C',
                    'color': 'cyan',
                    'x': (x_min_r + x_max_r) / 2,
                    'y': y_max_r * 0.9,
                    'z': z_min_r + (z_max_r - z_min_r) * 0.8
                },
                # Sensor D - Inferior izquierdo
                {
                    'name': 'Sensor D',
                    'color': 'magenta',
                    'x': (x_min_l + x_max_l) / 2,
                    'y': y_min_l * 0.9,
                    'z': z_min_l + (z_max_l - z_min_l) * 0.2
                },
                # Sensor E - Inferior derecho
                {
                    'name': 'Sensor E',
                    'color': 'orange',
                    'x': (x_min_r + x_max_r) / 2,
                    'y': y_min_r * 0.9,
                    'z': z_min_r + (z_max_r - z_min_r) * 0.2
                }
            ]
            
            # Add each marker
            for sensor in sensors:
                fig.add_trace(go.Scatter3d(
                    x=[sensor['x']],
                    y=[sensor['y']],
                    z=[sensor['z']],
                    mode='markers',
                    marker=dict(
                        size=6,
                        color=sensor['color'],
                        line=dict(width=1, color='black')
                    ),
                    name=sensor['name'],
                    showlegend=True
                ))
                
        except Exception as e:
            print(f"Warning: Could not add sensor markers: {e}")
            
        return fig
    
    def create_brain_figure_with_markers(self):
        """
        Crear figura original + marcadores de sensores
        """
        fig = self.create_brain_figure_original()
        if fig:
            fig = self.add_sensor_markers_to_figure(fig)
        return fig
    
    def _create_fallback_figure(self):
        """Create a fallback figure when nilearn is not available."""
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

# Global instance
brain_viz_simple = BrainVisualizer()