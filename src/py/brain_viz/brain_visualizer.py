"""
Brain 3D visualization component using nilearn and plotly.
Adapted from test3.py for live EEG data visualization.
"""

import numpy as np
import plotly.graph_objects as go

class BrainVisualizer:
    """
    3D Brain visualizer using nilearn surface data and plotly for rendering.
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
            
            # Load fsaverage surface data
            self.fsaverage = datasets.fetch_surf_fsaverage()
            
            # Load sample motor activation data for reference
            motor_img = datasets.load_sample_motor_activation_image()
            
            # Load meshes for both hemispheres
            self.mesh_right = surface.load_surf_mesh(self.fsaverage.pial_right)
            self.mesh_left = surface.load_surf_mesh(self.fsaverage.pial_left)
            
            # Get reference activation maps
            self.reference_map_right = surface.vol_to_surf(motor_img, self.mesh_right)
            self.reference_map_left = surface.vol_to_surf(motor_img, self.mesh_left)
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Warning: Could not initialize nilearn components: {e}")
            return False
        
    def create_brain_figure(self, intensity_right=None, intensity_left=None, title_suffix=""):
        """
        Create a 3D brain figure with optional custom intensity maps.
        
        Parameters:
        - intensity_right: Custom intensity values for right hemisphere
        - intensity_left: Custom intensity values for left hemisphere
        - title_suffix: Additional text for the title
        
        Returns:
        - plotly.graph_objects.Figure: 3D brain visualization
        """
        
        # Try to initialize nilearn components
        if not self._lazy_init():
            return self._create_fallback_figure()
        
        # Use provided intensity or fall back to reference
        map_right = intensity_right if intensity_right is not None else self.reference_map_right
        map_left = intensity_left if intensity_left is not None else self.reference_map_left
        
        # Create new figure
        fig = go.Figure()
        
        # Add right hemisphere with colorbar
        fig.add_trace(go.Mesh3d(
            x=self.mesh_right.coordinates[:, 0],
            y=self.mesh_right.coordinates[:, 1],
            z=self.mesh_right.coordinates[:, 2],
            i=self.mesh_right.faces[:, 0],
            j=self.mesh_right.faces[:, 1],
            k=self.mesh_right.faces[:, 2],
            intensity=map_right,
            colorscale="RdBu_r",  # Blue = negative, Red = positive
            cmin=-6,              # Min scale
            cmax=6,               # Max scale
            colorbar=dict(
                title=dict(text="Activación"),
                thickness=15,
                len=0.75
            ),
            showscale=True,
            name="Right Hemisphere",
            opacity=1
        ))
        
        # Add left hemisphere without colorbar
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
            showscale=False,  # Avoid second colorbar
            name="Left Hemisphere",
            opacity=1
        ))
        
        # Update layout with dynamic title
        title = f"Cerebro 3D - Visualización EEG en Tiempo Real{title_suffix}"
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor="white"
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=600
        )
        
        self.fig = fig
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
    
    def update_brain_intensity(self, all_sensors_data):
        """
        Update brain intensity based on EEG data from all sensors.
        Maps each sensor to specific brain regions:
        - Sensor A: Centro del cerebro
        - Sensor B: Lateral superior izquierdo 
        - Sensor C: Lateral superior derecho
        - Sensor D: Lateral inferior izquierdo
        - Sensor E: Lateral inferior derecho
        
        Parameters:
        - all_sensors_data: Dictionary with all sensor data
        
        Returns:
        - tuple: (intensity_right, intensity_left) arrays
        """
        if not self._initialized:
            return None, None
            
        # Initialize intensity maps with zeros
        intensity_right = np.zeros_like(self.reference_map_right)
        intensity_left = np.zeros_like(self.reference_map_left)
        
        # Get brain mesh coordinates for region mapping
        coords_right = self.mesh_right.coordinates
        coords_left = self.mesh_left.coordinates
        
        # Calculate brain bounds for region mapping
        x_min_r, x_max_r = coords_right[:, 0].min(), coords_right[:, 0].max()
        y_min_r, y_max_r = coords_right[:, 1].min(), coords_right[:, 1].max()
        z_min_r, z_max_r = coords_right[:, 2].min(), coords_right[:, 2].max()
        
        x_min_l, x_max_l = coords_left[:, 0].min(), coords_left[:, 0].max()
        y_min_l, y_max_l = coords_left[:, 1].min(), coords_left[:, 1].max()
        z_min_l, z_max_l = coords_left[:, 2].min(), coords_left[:, 2].max()
        
        # Process each sensor
        for sensor_name, sensor_data in all_sensors_data.items():
            if sensor_name == 'uid':  # Skip uid field
                continue
                
            # Extract attention and meditation values
            attention = sensor_data.get('attention', 50)
            meditation = sensor_data.get('meditation', 50)
            
            # Normalize to -6 to 6 range
            attention_norm = (attention - 50) * 6 / 50
            meditation_norm = (meditation - 50) * 6 / 50
            
            # Map sensors to brain regions
            if sensor_name == 'sensor_a':  # Centro del cerebro
                # Center region for both hemispheres (middle Y values)
                y_center_r = (y_min_r + y_max_r) / 2
                y_center_l = (y_min_l + y_max_l) / 2
                
                # Right hemisphere center
                mask_r = (coords_right[:, 1] >= y_center_r - (y_max_r - y_min_r) * 0.15) & \
                        (coords_right[:, 1] <= y_center_r + (y_max_r - y_min_r) * 0.15)
                intensity_right[mask_r] = attention_norm
                
                # Left hemisphere center  
                mask_l = (coords_left[:, 1] >= y_center_l - (y_max_l - y_min_l) * 0.15) & \
                        (coords_left[:, 1] <= y_center_l + (y_max_l - y_min_l) * 0.15)
                intensity_left[mask_l] = meditation_norm
                
            elif sensor_name == 'sensor_b':  # Lateral superior izquierdo
                # Upper left region (high Z, left side)
                z_upper_l = z_min_l + (z_max_l - z_min_l) * 0.6
                mask_l = coords_left[:, 2] >= z_upper_l
                intensity_left[mask_l] = attention_norm
                
            elif sensor_name == 'sensor_c':  # Lateral superior derecho
                # Upper right region (high Z, right side)
                z_upper_r = z_min_r + (z_max_r - z_min_r) * 0.6
                mask_r = coords_right[:, 2] >= z_upper_r
                intensity_right[mask_r] = attention_norm
                
            elif sensor_name == 'sensor_d':  # Lateral inferior izquierdo
                # Lower left region (low Z, left side)
                z_lower_l = z_min_l + (z_max_l - z_min_l) * 0.4
                mask_l = coords_left[:, 2] <= z_lower_l
                intensity_left[mask_l] = meditation_norm
                
            elif sensor_name == 'sensor_e':  # Lateral inferior derecho
                # Lower right region (low Z, right side)
                z_lower_r = z_min_r + (z_max_r - z_min_r) * 0.4
                mask_r = coords_right[:, 2] <= z_lower_r
                intensity_right[mask_r] = meditation_norm
        
        return intensity_right, intensity_left
    
    def create_live_brain_figure(self, all_sensors_data):
        """
        Create brain figure with live EEG data from sensors.
        
        Parameters:
        - all_sensors_data: Dictionary with sensor data (can be one or multiple sensors)
        
        Returns:
        - plotly.graph_objects.Figure: Updated 3D brain visualization
        """
        if not self._lazy_init():
            return self._create_fallback_figure()
            
        intensity_right, intensity_left = self.update_brain_intensity(all_sensors_data)
        
        # Determine title suffix based on data
        sensor_count = len([k for k in all_sensors_data.keys() if k != 'uid'])
        if sensor_count == 1:
            sensor_name = [k for k in all_sensors_data.keys() if k != 'uid'][0]
            title_suffix = f" - {sensor_name.upper()}"
        else:
            title_suffix = f" - Todos los Sensores ({sensor_count})"
            
        return self.create_brain_figure(intensity_right, intensity_left, title_suffix)

# Global brain visualizer instance
brain_viz = BrainVisualizer()