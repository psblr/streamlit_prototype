import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
from stpyvista.utils import is_the_app_embedded, start_xvfb
import numpy as np
import os
import time

start_xvfb()


# Function to save uploaded files
def save_uploaded_file(uploaded_file, save_dir="uploaded_files"):
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# Function to generate STL file (supports binary and ASCII)
def generate_stl_file(model_name, binary=True):
    filename = f"{model_name}.stl"
    filepath = os.path.join("output", filename)
    os.makedirs("output", exist_ok=True)
    
    # Generate a simple cube as STL model
    points = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom square
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],  # Top square
    ])
    faces = np.hstack([
        [4, 0, 1, 2, 3],  # Bottom face
        [4, 4, 5, 6, 7],  # Top face
        [4, 0, 1, 5, 4],  # Side faces
        [4, 1, 2, 6, 5],
        [4, 2, 3, 7, 6],
        [4, 3, 0, 4, 7],
    ])
    
    mesh = pv.PolyData(points, faces)
    if binary:
        mesh.save(filepath)  # Save as binary STL
    else:
        mesh.save(filepath, binary=False)  # Save as ASCII STL
    return filepath

# Simulate RAG functionality (placeholder)
def retrieve_and_generate_response(query, document_paths):
    # Placeholder for RAG logic
    response = f"Generated a response for '{query}' using {len(document_paths)} document(s)."
    return response

def main():
    

    # Streamlit Interface
    st.title("CAD Generater 3000")
    st.subheader("Upload documents and describe your CAD model requirements.")

    # Section: STL Format Selection
    st.sidebar.header("STL File Format")
    binary_stl = st.sidebar.radio(
        "Select STL file format:",
        ("Binary", "Human-readable (ASCII)")
    )

    # Section: File Upload
    st.sidebar.header("Upload Relevant Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload documents (PDF, DOCX, etc.)", accept_multiple_files=True
    )

    if uploaded_files:
        st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded.")
        saved_file_paths = [save_uploaded_file(f) for f in uploaded_files]
        print(saved_file_paths)

    # Section: CAD Model Description and Generation
    st.header("Generate CAD Models in .STL Format")
    model_description = st.text_input("Describe the CAD model you need:")

    if st.button("Generate Model"):
        if model_description.strip():
            with st.spinner("Generating your CAD model..."):
                time.sleep(2)
                stl_file_path = generate_stl_file(
                    model_name=model_description,
                    binary=(binary_stl == "Binary")
                )
                st.success(f"Model '{model_description}' generated successfully!")
                
                st.subheader("3D CAD Model Visualization")
                mesh = pv.read(stl_file_path)
                ## Add some scalar field associated to the mesh

                plotter = pv.Plotter(window_size=[400, 400])
                plotter.add_mesh(mesh, color="green")
                plotter.show_axes()
                stpyvista(plotter)  # Display the 3D model in Streamlit

                st.subheader("Model description")
                st.write("""
                    A Cube has been generated. It is green. Your description was ignored.
                """)


                with open(stl_file_path, "rb") as stl_file:
                    st.download_button(
                        label="Download STL File",
                        data=stl_file,
                        file_name=os.path.basename(stl_file_path),
                        mime="application/vnd.ms-pki.stl",
                    )
        else:
            st.error("Please provide a description of the model.")

if __name__ == "__main__":
    if "IS_XVFB_RUNNING" not in st.session_state:
        start_xvfb()
        st.session_state.IS_XVFB_RUNNING = True 
    main()
