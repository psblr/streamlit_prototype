import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
from stpyvista.utils import start_xvfb
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

# Function to Generate .stl file file (supports binary and ASCII)
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

def exec_button(model_description, message="Generating your CAD model..."):
    if model_description.strip():
        with st.spinner(message):
            time.sleep(2)
            stl_binary_file_path = generate_stl_file(
                model_name=model_description + "_binary",
                binary=True
            )
            stl_ascii_file_path = generate_stl_file(
                model_name=model_description + "_ascii",
                binary=False
            )

            view_model_path = "utah_teapot.stl"
            st.success(f"Model '{model_description}' generated successfully!")
            
            st.subheader("3D CAD Model Visualization")
            mesh = pv.read(view_model_path)
            # Scale the mesh down (adjust the factor as needed)
            scale_factor = 0.1
            mesh.scale([scale_factor, scale_factor, scale_factor])  # Apply uniform scaling
            
            # Center the mesh by shifting it to the origin
            center = np.array(mesh.center) 
            mesh.translate(-center)  # Translate so the center is at (0, 0, 0)
            
            # Normalize the mesh to fit within a unit cube (optional, for extreme cases)
            bounds = mesh.bounds
            max_dimension = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
            mesh.scale([1.0 / max_dimension] * 3)  # Scale to fit into a unit box
            
            # Add a scalar field (optional, for visualization)
            mesh["Height"] = mesh.points[:, 2]  # Use Z-coordinates as scalar values

            # Visualize the mesh with PyVista
            plotter = pv.Plotter(window_size=[600, 400])
            plotter.add_mesh(mesh, scalars="Height", cmap="coolwarm", show_edges=True)
            plotter.show_axes()
            

            # Explicitly adjust the camera
            bounds = mesh.bounds  # Get mesh bounds: (xmin, xmax, ymin, ymax, zmin, zmax)
            x_range = bounds[1] - bounds[0]
            y_range = bounds[3] - bounds[2]
            z_range = bounds[5] - bounds[4]

            # Compute the diagonal size of the bounding box for a better zoom level
            diagonal = np.sqrt(x_range**2 + y_range**2 + z_range**2)
            
            # Set the camera position relative to the center
            plotter.camera_position = [
                (center[0] + 2 * diagonal, center[1] + 2 * diagonal, center[2] + 2 * diagonal),  # Camera location
                (center[0], center[1], center[2]),  # Focal point (center of the mesh)
                (0, 0, 1)  # View up direction
            ]

            # Reset the camera to update the view
            plotter.reset_camera()


            stpyvista(plotter)  # Display the 3D model in Streamlit
            st.subheader("Model description")
            st.write("""
                As this is just a protoype, your description was ignored and A Teapot has been generated.
            """)

            col1, col2 = st.columns(2)
            with col1:
                with open(stl_binary_file_path, "rb") as stl_file:
                    st.download_button(
                        label="Download binary STL File",
                        data=stl_file,
                        file_name=os.path.basename(stl_binary_file_path),
                        mime="application/vnd.ms-pki.stl",
                    )

            with col2:
                with open(stl_ascii_file_path, "rb") as stl_file:
                    st.download_button(
                        label="Download ASCII STL File",
                        data=stl_file,
                        file_name=os.path.basename(stl_ascii_file_path),
                        mime="application/vnd.ms-pki.stl",
                    )
    else:
        st.error("Please provide a description of the model.")

def main():
    

    # Streamlit Interface
    st.title("CAD Generater 3000")
    st.text("This is a clickable prototype for a CAD Engineering assistant. The current functionality is limited to generating a demo .stl file in ASCII and binary format.")
    st.text("In the final version, you will be able to create ASCII and binary CAD files based on your custom prompt or refine existing .stl files.")

    st.sidebar.title("")
    page = st.sidebar.radio("What do you want to do?:", ["Generate .stl file", "Refine .stl file"])


    # Section: File Upload
    st.sidebar.header("Upload Relevant Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload documents (PDF, DOCX, etc.)", 
        accept_multiple_files=True,
        help="Upload documents to provide context for the CAD model generation. This could be existing .stl files of company-internal designs or other relevant documents."
    )

    if uploaded_files:
        st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded.")
        saved_file_paths = [save_uploaded_file(f) for f in uploaded_files]
        print(saved_file_paths)

    
    if page == "Generate .stl file":
        # Section: CAD Model Description and Generation
        st.header("Generate CAD Models in .STL Format")
        st.text("Upload documents and describe your CAD model requirements.")
        model_description = st.text_input("Describe the CAD model you need:", placeholder="e.g. Teapot with a handle",
                                          help="Provide a brief description of the CAD model you need.")

        if st.button("Generate Model"):
            exec_button(model_description)
            
    elif page == "Refine .stl file":
        st.header("Refine Existing .stl Files")
        uploaded_files = st.file_uploader(
        label="Upload your .stl file", accept_multiple_files=True
        )

        model_description = st.text_input("Describe the refinements:", placeholder="e.g. Remove the handle of the teapot", 
                                          help="Provide a brief description of the refinements which shall be applied to your uploaded model.")

        

        if uploaded_files:
            st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded.")
            saved_file_paths = [save_uploaded_file(f) for f in uploaded_files]

        if st.button("Refine Model"):
            exec_button(model_description, message="Refining your CAD model...")


if __name__ == "__main__":
    main()
