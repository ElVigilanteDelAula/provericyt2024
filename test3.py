from nilearn import datasets, surface
import plotly.graph_objects as go

# Cargar fsaverage y dataset (usando la nueva función recomendada)
fsaverage = datasets.fetch_surf_fsaverage()
motor_img = datasets.load_sample_motor_activation_image()

# ---- Hemisferio derecho ----
mesh_r = surface.load_surf_mesh(fsaverage.pial_right)
map_r = surface.vol_to_surf(motor_img, mesh_r)

# ---- Hemisferio izquierdo ----
mesh_l = surface.load_surf_mesh(fsaverage.pial_left)
map_l = surface.vol_to_surf(motor_img, mesh_l)

# Crear figura plotly
fig = go.Figure()

# Añadir hemisferio derecho con barra de color
fig.add_trace(go.Mesh3d(
    x=mesh_r.coordinates[:, 0],
    y=mesh_r.coordinates[:, 1],
    z=mesh_r.coordinates[:, 2],
    i=mesh_r.faces[:, 0],
    j=mesh_r.faces[:, 1],
    k=mesh_r.faces[:, 2],
    intensity=map_r,
    colorscale="RdBu_r",  # Azul = negativo, rojo = positivo
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

# Añadir hemisferio izquierdo sin barra de color
fig.add_trace(go.Mesh3d(
    x=mesh_l.coordinates[:, 0],
    y=mesh_l.coordinates[:, 1],
    z=mesh_l.coordinates[:, 2],
    i=mesh_l.faces[:, 0],
    j=mesh_l.faces[:, 1],
    k=mesh_l.faces[:, 2],
    intensity=map_l,
    colorscale="RdBu_r",
    cmin=-6,
    cmax=6,
    showscale=False,  # 👈 evita la segunda barra
    name="Left Hemisphere",
    opacity=1
))

# Ajustar layout
fig.update_layout(
    title="Ambos hemisferios con colorbar compartido (-6 azul / +6 rojo)",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False)
    ),
    margin=dict(l=0, r=0, t=40, b=0)
)

fig.show()
