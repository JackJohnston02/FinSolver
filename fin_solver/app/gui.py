import streamlit as st
from dataclasses import fields, is_dataclass
from fin_solver.app.models import Config, Parameter, Layer
from dataclasses import asdict
from fin_solver.app.visualisation import create_3d_fin_layup_render


def render_parameter(param: Parameter, key_prefix: str = "") -> None:
    key = f"{key_prefix}_{param.name.replace(' ', '_')}"
    if isinstance(param.value, (int, float)):
        param.value = st.number_input(
            label=f"{param.name} ({param.units})" if param.units else param.name,
            value=param.value,
            min_value=param.min,
            max_value=param.max,
            step=param.step,
            help=param.tooltip,
            key=key
        )
    elif isinstance(param.value, str):
        param.value = st.text_input(
            label=param.name,
            value=param.value,
            help=param.tooltip,
            key=key
        )
    else:
        st.warning(f"Unsupported type for {param.name}")


def render_object_fields(obj, key_prefix: str = "") -> None:
    for field in fields(obj):
        val = getattr(obj, field.name)
        if isinstance(val, Parameter):
            render_parameter(val, key_prefix=key_prefix)
        elif is_dataclass(val):
            st.subheader(field.name.replace("_", " ").title())
            render_object_fields(val, key_prefix=f"{key_prefix}_{field.name}")


def run_gui():
    if "config" not in st.session_state:
        st.session_state.config = Config()

    config: Config = st.session_state.config

    st.title("Fin Flutter Configuration Tool")

    # Layout
    col1, col2 = st.columns([1.2, 2])

    # ─── LEFT COLUMN: Input ──────────────────────────────────────────
    with col1:
        st.header("Input Parameters")

        st.subheader("General Configuration")
        render_object_fields(config.general_parameters, key_prefix="general")

        st.divider()

        st.subheader("Core")

        with st.expander("Core Fin Section", expanded=True):
            render_object_fields(config.core.geometry, key_prefix="core_geom")
            render_object_fields(config.core.material, key_prefix="core_mat")

        st.divider()
        st.subheader("Additional Layers")

        if st.button("➕ Add Layer"):
            config.layers.append(Layer(name=f"Layer {len(config.layers) + 1}"))
            st.rerun()


        # Track layers to delete
        layers_to_delete = []

        for i, layer in enumerate(config.layers):
            with st.expander(f"Layer {i + 1}: {layer.name}"):
                # Instep checkbox
                layer.instep_from_previous_layer = st.checkbox(
                    "Instep from previous layer",
                    value=layer.instep_from_previous_layer,
                    help="Enable this to shift this layer inward from the one below.",
                    key=f"layer{i}_instep"
                )

                if layer.instep_from_previous_layer:
                    render_parameter(layer.instep_distance, key_prefix=f"layer{i}_instep_dist")
                    base_geom = config.core.geometry if i == 0 else config.layers[i - 1].geometry
                    layer.apply_instep(base_geom)
                    thickness_param = layer.geometry.thickness
                    thickness_param.name = "Thickness"
                    render_parameter(thickness_param, key_prefix=f"layer{i}_thickness")
                else:
                    render_object_fields(layer.geometry, key_prefix=f"layer{i}_geom")

                render_object_fields(layer.material, key_prefix=f"layer{i}_mat")

                # 🔻 Delete button now placed at the bottom
                st.markdown("---")
                if st.button(f"🗑️ Delete Layer {i + 1}", key=f"delete_layer_{i}"):
                    layers_to_delete.append(i)

        # Apply deletions after the loop
        for idx in sorted(layers_to_delete, reverse=True):
            del config.layers[idx]
            st.rerun()









    # ─── RIGHT COLUMN: Output ─────────────────────────────────────────
    with col2:
        st.header("Results & Visualisation")
        st.info("Solver output and plots will be displayed here.")
        
        st.subheader("3D Fin Layup Preview")
        fig = create_3d_fin_layup_render(config)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to render fin layup. Check that geometry is valid.")


        with st.expander("Show Raw Config Data", expanded=False):
            st.json(asdict(config))
