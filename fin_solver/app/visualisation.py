import plotly.graph_objects as go
import numpy as np
from fin_solver.app.models import Config


def get_vertices_3d(root, tip, height, thickness, sweep):
    """
    Returns 8 vertices for a 3D trapezoidal fin aligned vertically (Z-axis).
    The fin extends radially (Y-axis) and sweep affects the tip's Y-offset.
    """
    # Define 4 midplane vertices of the trapezoid
    p1 = np.array([0, 0, -root/2])                      # root bottom
    p2 = np.array([0, 0, root/2])                   # root top
    p3 = np.array([height, 0, root/2 - sweep])      # tip top
    p4 = np.array([height, 0, root/2 - sweep - tip])# tip bottom

    # Offset in the ±X direction for thickness
    offset = np.array([0, thickness / 2, 0])

    # Compute front and back face vertices
    bottom = [p1 - offset, p2 - offset, p3 - offset, p4 - offset]
    top    = [p1 + offset, p2 + offset, p3 + offset, p4 + offset]

    return bottom + top





def rotate(vertices, angle_rad, radius):
    """
    Rotate a set of vertices around the Z-axis and offset by body radius.
    """
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return [
        (x * c - y * s + radius * c, x * s + y * c + radius * s, z)
        for x, y, z in vertices
    ]


def create_body_tube_mesh(radius, height, segments=30):
    """
    Generate a cylindrical body tube using Mesh3d.
    """
    theta = np.linspace(0, 2 * np.pi, segments)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z_bottom = np.zeros(segments) - np.ones(segments) * height/2
    z_top = np.full(segments, height/2)

    # Combine bottom and top
    x_all = np.concatenate([x, x])
    y_all = np.concatenate([y, y])
    z_all = np.concatenate([z_bottom, z_top])

    faces = []
    for i in range(segments):
        next_i = (i + 1) % segments
        # side faces
        faces.append((i, next_i, segments + next_i))
        faces.append((i, segments + next_i, segments + i))

    i_faces, j_faces, k_faces = zip(*faces)
    return go.Mesh3d(
        x=x_all, y=y_all, z=z_all,
        i=i_faces, j=j_faces, k=k_faces,
        color='gray', opacity=0.2, name='Body Tube'
    )


def create_3d_fin_layup_render(config: Config):
    num_fins = config.general_parameters.number_of_fins.value
    body_radius = config.general_parameters.body_tube_OD.value / 2

    fig = go.Figure()
    z_stack = 0.0

    # ─── Render Core ─────────────────────────────
    core_geom = config.core.geometry
    verts = get_vertices_3d(
        root=core_geom.root_chord.value,
        tip=core_geom.tip_chord.value,
        height=core_geom.height.value,
        thickness=core_geom.thickness.value,
        sweep=core_geom.sweep_length.value
    )

    for i in range(num_fins):
        angle = 2 * np.pi * i / num_fins
        v = rotate(verts, angle, body_radius)
        x, y, z = zip(*v)
        faces = [
            [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
            [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]
        ]
        i_faces, j_faces, k_faces = zip(*faces)
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i_faces, j=j_faces, k=k_faces,
            opacity=0.7, color='lightblue', name="Core"
        ))
    z_stack += core_geom.thickness.value

    # ─── Render Layers ───────────────────────────
    for idx, layer in enumerate(config.layers):
        geom = layer.geometry

        # TODO We need to offset the layer due to the previous layers and also mirror it as the layup is on both sides, could just add the thickness!?!
        additional_thickness = 0
        for idx_minor, layer_minor in enumerate(config.layers):
            if idx_minor < idx:
                additional_thickness += layer_minor.geometry.thickness


        verts = get_vertices_3d(
            root=geom.root_chord.value,
            tip=geom.tip_chord.value,
            height=geom.height.value,
            thickness=geom.thickness.value + additional_thickness,
            sweep=geom.sweep_length.value
        )


        for i in range(num_fins):
            angle = 2 * np.pi * i / num_fins
            v = rotate(verts, angle, body_radius)
            x, y, z = zip(*v)
            faces = [
                [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
                [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]
            ]
            i_faces, j_faces, k_faces = zip(*faces)
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i_faces, j=j_faces, k=k_faces,
                opacity=0.5, color='orange', name=f"Layer {idx+1}"
            ))
        z_stack += geom.thickness.value

    # ─── Render Body Tube ────────────────────────
    tube_height = core_geom.root_chord.value
    tube_mesh = create_body_tube_mesh(body_radius, tube_height)
    fig.add_trace(tube_mesh)

    # Plot layout
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        title="3D Fin Layup with Body Tube",
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False
    )
    return fig
