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
        Update brain intensity based on EEG data from all sensors with heatmap effect.
        Maps each sensor to specific brain regions with:
        - Area coverage based on signal_strength (stronger signal = larger area)
        - Radial fade effect (intensity decreases from center outward)
        
        Sensor mapping based on EEG standard positions:
        - Sensor A: P3 - Left Parietal Lobe
        - Sensor B: F3 - Left Frontal Cortex 
        - Sensor C: FPz - Midline Forehead (Ground)
        - Sensor D: F4 - Right Frontal Cortex
        - Sensor E: P2 - Right Parietal Lobe (between Pz and T6)
        
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
        
        # Brain dimensions for distance calculations
        brain_size_r = np.sqrt((x_max_r - x_min_r)**2 + (y_max_r - y_min_r)**2 + (z_max_r - z_min_r)**2)
        brain_size_l = np.sqrt((x_max_l - x_min_l)**2 + (y_max_l - y_min_l)**2 + (z_max_l - z_min_l)**2)
        
        # Process each sensor
        for sensor_name, sensor_data in all_sensors_data.items():
            if sensor_name == 'uid':  # Skip uid field
                continue
                
            # Extract sensor values
            attention = sensor_data.get('attention', 50)
            meditation = sensor_data.get('meditation', 50)
            signal_strength = sensor_data.get('signal_strength', 50)
            
            # Normalize attention and meditation to -6 to 6 range
            attention_norm = (attention - 50) * 6 / 50
            meditation_norm = (meditation - 50) * 6 / 50
            
            # Signal strength controls area coverage (0-100 → 0.1-1.0)
            coverage_factor = (signal_strength / 100.0) * 0.9 + 0.1  # Min 10%, Max 100%
            
            # Map sensors to brain regions with heatmap effect based on EEG standard positions
            if sensor_name == 'sensor_a':  # P3 - Left Parietal Lobe
                # Define center point for P3 position (left parietal - posterior region)
                center_l = np.array([x_min_l + (x_max_l - x_min_l) * 0.3, 
                                   y_min_l + (y_max_l - y_min_l) * 0.2,  # Posterior (back)
                                   z_min_l + (z_max_l - z_min_l) * 0.7])
                
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.25 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * attention_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_b':  # F3 - Left Frontal Cortex
                # Define center point for F3 position (left frontal - anterior region)
                center_l = np.array([x_min_l + (x_max_l - x_min_l) * 0.3, 
                                   y_max_l - (y_max_l - y_min_l) * 0.2,  # Anterior (front)
                                   z_min_l + (z_max_l - z_min_l) * 0.6])
                
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.25 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * attention_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_c':  # FPz - Midline Forehead (Ground)
                # Define center points for FPz position (midline frontal - very front)
                center_r = np.array([((x_min_r + x_max_r) / 2) * 0.4, 
                                   (y_max_r - (y_max_r - y_min_r)) * -0.62,  # Very anterior (front)
                                   z_max_r * 0.21])  # Top of the brain
                center_l = np.array([((x_min_l + x_max_l) / 2) * 0.4, 
                                  ( y_max_l - (y_max_l - y_min_l)) * -0.62 ,  # Very anterior (front)
                                   z_max_l * 0.21])  # Top of the brain
                 # Apply to right hemisphere
                distances_r = np.sqrt(np.sum((coords_right - center_r)**2, axis=1))
                max_distance_r = brain_size_r * 0.2 * coverage_factor
                
                fade_mask_r = distances_r <= max_distance_r
                fade_intensity_r = np.zeros_like(distances_r)
                fade_intensity_r[fade_mask_r] = (1 - distances_r[fade_mask_r] / max_distance_r) * attention_norm
                intensity_right += fade_intensity_r
                
                # Apply to left hemisphere
                distances_l = np.sqrt(np.sum((coords_left - center_l)**2, axis=1))
                max_distance_l = brain_size_l * 0.2 * coverage_factor
                
                fade_mask_l = distances_l <= max_distance_l
                fade_intensity_l = np.zeros_like(distances_l)
                fade_intensity_l[fade_mask_l] = (1 - distances_l[fade_mask_l] / max_distance_l) * meditation_norm
                intensity_left += fade_intensity_l
                
            elif sensor_name == 'sensor_d':  # F4 - Right Frontal Cortex
                # Define center point for F4 position (right frontal - anterior region)
                center_r = np.array([x_max_r - (x_max_r - x_min_r) * 0.3, 
                                   y_max_r - (y_max_r - y_min_r) * 0.2,  # Anterior (front)
                                   z_min_r + (z_max_r - z_min_r) * 0.6])
                
                distances_r = np.sqrt(np.sum((coords_right - center_r)**2, axis=1))
                max_distance_r = brain_size_r * 0.25 * coverage_factor
                
                fade_mask_r = distances_r <= max_distance_r
                fade_intensity_r = np.zeros_like(distances_r)
                fade_intensity_r[fade_mask_r] = (1 - distances_r[fade_mask_r] / max_distance_r) * meditation_norm
                intensity_right += fade_intensity_r
                
            elif sensor_name == 'sensor_e':  # P2 - Right Parietal Lobe (between Pz and T6)
                # Define center point for P2 position (right parietal - posterior region)
                center_r = np.array([x_max_r - (x_max_r - x_min_r) * 0.3, 
                                   y_min_r + (y_max_r - y_min_r) * 0.2,  # Posterior (back)
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