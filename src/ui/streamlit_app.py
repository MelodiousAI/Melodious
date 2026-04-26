"""Streamlit MVP for the Week 4 Melodious integration flow."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PAYLOAD_ROOT = PROJECT_ROOT / "sample_detections"
BACKEND_TIMEOUT_SECONDS = 60
SAMPLE_GROUPS = {
    "Reference payloads": SAMPLE_PAYLOAD_ROOT / "reference",
    "Real YOLO payloads": SAMPLE_PAYLOAD_ROOT / "model_outputs_quick",
    "MUSCIMA reference payloads": SAMPLE_PAYLOAD_ROOT / "muscima_reference",
}


def build_sample_index() -> dict[str, Path]:
    """Return a label-to-path map for all bundled sample payloads."""
    sample_index: dict[str, Path] = {}

    for group_label, group_path in SAMPLE_GROUPS.items():
        if not group_path.exists():
            continue

        for payload_path in sorted(group_path.glob("*.json")):
            sample_index[f"{group_label}: {payload_path.name}"] = payload_path

    return sample_index


def load_json_file(json_path: Path) -> dict:
    """Load one JSON payload from disk."""
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_uploaded_payload(uploaded_file) -> dict:
    """Load one uploaded JSON payload from the Streamlit file uploader."""
    return json.loads(uploaded_file.getvalue().decode("utf-8"))


def parse_optional_staff_regions(raw_text: str) -> list[list[int]] | None:
    """Parse the optional staff-region JSON field used by the backend."""
    normalized_text = raw_text.strip()

    if not normalized_text:
        return None

    parsed = json.loads(normalized_text)

    if parsed is None:
        return None

    if not isinstance(parsed, list):
        raise ValueError("staff_regions must be a JSON list like [[120, 180], [240, 300]].")

    return parsed


def call_backend(base_url: str, endpoint: str, body: dict | None = None) -> dict:
    """Call the FastAPI backend and return the decoded JSON response."""
    normalized_base_url = base_url.rstrip("/")
    url = f"{normalized_base_url}{endpoint}"

    if body is None:
        response = requests.get(url, timeout=BACKEND_TIMEOUT_SECONDS)
    else:
        response = requests.post(url, json=body, timeout=BACKEND_TIMEOUT_SECONDS)

    response.raise_for_status()
    return response.json()


def render_health_panel(health_response: dict) -> None:
    """Render the Week 4 backend readiness section."""
    gnn_status = health_response["gnn_status"]
    status_columns = st.columns(4)
    status_columns[0].metric("Stage", health_response["stage"])
    status_columns[1].metric("Service", health_response["service"])
    status_columns[2].metric("Default Mode", health_response["default_assembly_mode"])
    status_columns[3].metric("GNN Ready", "Yes" if gnn_status["ready"] else "No")

    st.subheader("GNN Readiness")
    st.write(gnn_status["message"])
    st.json(gnn_status, expanded=False)


def render_assemble_panel(assemble_response: dict) -> None:
    """Render the `/assemble` response for the Week 4 demo."""
    graph_stats = assemble_response["graph_statistics"]
    assembly_mode = assemble_response["assembly_mode"]

    metric_columns = st.columns(4)
    metric_columns[0].metric("Detections", assemble_response["detection_count"])
    metric_columns[1].metric("Nodes", graph_stats["num_nodes"])
    metric_columns[2].metric("Edges", graph_stats["num_edges"])
    metric_columns[3].metric("Avg Degree", f"{graph_stats['average_degree']:.2f}")

    st.subheader("Assembly Mode")
    st.json(assembly_mode, expanded=False)

    st.subheader("Assembly Summary")
    st.json(assemble_response["assembly_summary"], expanded=False)

    attention_preview = assemble_response["attention_preview"]
    st.subheader("Attention Preview")
    if attention_preview["available"]:
        st.dataframe(attention_preview["top_edges"], use_container_width=True)
    else:
        st.info(attention_preview["message"])

    if assemble_response["alignment_summary"] is not None:
        st.subheader("Alignment Summary")
        st.json(assemble_response["alignment_summary"], expanded=False)

    if assemble_response["warnings"]:
        st.subheader("Warnings")
        for warning in assemble_response["warnings"]:
            st.warning(warning)

    with st.expander("Raw /assemble response"):
        st.json(assemble_response, expanded=False)


def render_export_panel(export_response: dict) -> None:
    """Render the `/midi` response and expose download actions."""
    meta_columns = st.columns(4)
    meta_columns[0].metric("Format", export_response["output_format"])
    meta_columns[1].metric("Detections", export_response["detection_count"])
    meta_columns[2].metric("Assembly Mode", export_response["assembly_mode"]["applied_mode"])
    meta_columns[3].metric("Encoding", export_response["content_encoding"])

    st.subheader("Assembly Summary")
    st.json(export_response["assembly_summary"], expanded=False)

    attention_preview = export_response["attention_preview"]
    st.subheader("Attention Preview")
    if attention_preview["available"]:
        st.dataframe(attention_preview["top_edges"], use_container_width=True)
    else:
        st.info(attention_preview["message"])

    if export_response["warnings"]:
        st.subheader("Warnings")
        for warning in export_response["warnings"]:
            st.warning(warning)

    document_name = export_response["document_name"] or "melodious_export"

    if export_response["output_format"] == "musicxml":
        xml_content = export_response["content"]
        st.subheader("MusicXML Preview")
        st.code(xml_content[:4000], language="xml")
        st.download_button(
            "Download MusicXML",
            data=xml_content.encode("utf-8"),
            file_name=f"{document_name}.musicxml",
            mime=export_response["content_type"],
        )
    else:
        midi_bytes = base64.b64decode(export_response["content"])
        st.subheader("MIDI Output")
        st.download_button(
            "Download MIDI",
            data=midi_bytes,
            file_name=f"{document_name}.mid",
            mime=export_response["content_type"],
        )
        st.caption(f"Decoded MIDI size: {len(midi_bytes)} bytes")

    with st.expander("Raw /midi response"):
        st.json(export_response, expanded=False)


def main() -> None:
    """Run the Streamlit Week 4 integration MVP."""
    st.set_page_config(page_title="Melodious Week 4 MVP", layout="wide")
    st.title("Melodious Week 4 MVP")
    st.caption("FastAPI + GNN-ready backend status, assembly, and export demo.")

    sample_index = build_sample_index()

    with st.sidebar:
        st.header("Backend")
        backend_url = st.text_input("FastAPI base URL", value="http://127.0.0.1:8000")

        st.header("Payload")
        uploaded_file = st.file_uploader("Upload detector payload JSON", type=["json"])
        selected_sample = st.selectbox(
            "Or choose a bundled sample payload",
            options=["None"] + list(sample_index.keys()),
        )

        payload_kind = st.selectbox("Payload kind", options=["auto", "generic", "muscima_reference"], index=0)
        assembly_mode = st.selectbox("Assembly mode", options=["auto", "heuristic", "gnn"], index=0)
        run_alignment = st.checkbox("Run alignment (MUSCIMA only)", value=False)
        include_graph_data = st.checkbox("Include serialized graph arrays", value=False)
        output_format = st.selectbox("Export format", options=["musicxml", "midi"], index=0)
        document_name = st.text_input("Document name override", value="")
        export_title = st.text_input("Export title override", value="")
        staff_regions_text = st.text_area(
            "Optional staff_regions JSON",
            value="",
            help="Example: [[120, 180], [240, 300]]",
        )

    payload = None

    try:
        if uploaded_file is not None:
            payload = load_uploaded_payload(uploaded_file)
        elif selected_sample != "None":
            payload = load_json_file(sample_index[selected_sample])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        st.error(f"Could not load payload: {exc}")

    if payload is None:
        st.warning("Select a bundled sample payload or upload one JSON file to begin.")
        return

    try:
        staff_regions = parse_optional_staff_regions(staff_regions_text)
    except ValueError as exc:
        st.error(str(exc))
        return
    except json.JSONDecodeError as exc:
        st.error(f"staff_regions must be valid JSON: {exc}")
        return

    with st.expander("Loaded payload", expanded=False):
        st.json(payload, expanded=False)

    request_base = {
        "payload": payload,
        "payload_kind": payload_kind,
        "assembly_mode": assembly_mode,
    }

    if document_name.strip():
        request_base["document_name"] = document_name.strip()

    if staff_regions is not None:
        request_base["staff_regions"] = staff_regions

    left_column, right_column = st.columns(2)

    with left_column:
        st.header("Backend Status")
        if st.button("Call /health", use_container_width=True):
            try:
                st.session_state["health_response"] = call_backend(backend_url, "/health")
                st.session_state.pop("health_error", None)
            except requests.RequestException as exc:
                st.session_state["health_error"] = str(exc)

        if "health_error" in st.session_state:
            st.error(st.session_state["health_error"])
        elif "health_response" in st.session_state:
            render_health_panel(st.session_state["health_response"])

        st.header("Graph Assembly")
        if st.button("Call /assemble", use_container_width=True):
            assemble_request = dict(request_base)
            assemble_request["run_alignment"] = run_alignment
            assemble_request["include_graph_data"] = include_graph_data

            try:
                st.session_state["assemble_response"] = call_backend(
                    backend_url,
                    "/assemble",
                    assemble_request,
                )
                st.session_state.pop("assemble_error", None)
            except requests.RequestException as exc:
                st.session_state["assemble_error"] = str(exc)

        if "assemble_error" in st.session_state:
            st.error(st.session_state["assemble_error"])
        elif "assemble_response" in st.session_state:
            render_assemble_panel(st.session_state["assemble_response"])

    with right_column:
        st.header("Export")
        if st.button("Call /midi", use_container_width=True):
            export_request = dict(request_base)
            export_request["output_format"] = output_format

            if export_title.strip():
                export_request["title"] = export_title.strip()

            try:
                st.session_state["export_response"] = call_backend(
                    backend_url,
                    "/midi",
                    export_request,
                )
                st.session_state.pop("export_error", None)
            except requests.RequestException as exc:
                st.session_state["export_error"] = str(exc)

        if "export_error" in st.session_state:
            st.error(st.session_state["export_error"])
        elif "export_response" in st.session_state:
            render_export_panel(st.session_state["export_response"])


if __name__ == "__main__":
    main()
