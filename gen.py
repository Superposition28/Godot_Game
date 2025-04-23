import os
import shutil
import subprocess

"""
godot node scheme

each node corresponds to a scene file
each scene file corresponds to a folder
each scene folder contains the files contained in that scene node

- Node4D : Node4D.tscn
    - Node3D : Node4D/Node3D.tscn
    - Node2D : Node4D/Node2D.tscn
        - Control : Node4D/Node2D/Control.tscn

Folder Structure:

res://assets
- Node4D/
    - Node2D/
        - Control/
        - Control.tscn
    - Node2D.tscn

    - Node3D/
    - Node3D.tscn

- Node4D.tscn

"""

def write_scene_file(base_dir, relative_path, node_type="Node", children=None):
    """
    Creates a .tscn file at base_dir/relative_path.tscn
    Ensures all parent directories exist.
    Optionally adds child scene instances.
    children should be a list of dicts: [{'path': 'res://path/to/child.tscn', 'name': 'ChildNodeName'}]
    """
    print(f"\nWriting scene file: {base_dir} {relative_path}\n")
    path_parts = relative_path.split('/')
    print("path_parts:", path_parts)
    node_name = path_parts[-1]
    print("node_name: ", node_name)
    scene_file_path = os.path.join(base_dir, *path_parts) + ".tscn"
    print("scene_file_path: ", scene_file_path)

    os.makedirs(os.path.dirname(scene_file_path), exist_ok=True)
    print(f"Creating directories for {scene_file_path}")

    # Build content string
    content_lines = ["[gd_scene load_steps={} format=3]".format(len(children) + 1 if children else 1)] # +1 for the main node

    # Add external resources for children
    ext_resources = {}
    if children:
        for i, child in enumerate(children):
            resource_id = f"ext_resource_{i+1}"
            ext_resources[child['path']] = resource_id
            content_lines.append(f'[ext_resource type="PackedScene" uid="{child[\'path\']}" id="{resource_id}"]')

    # Add the main node definition
    content_lines.append(f'[node name="{node_name}" type="{node_type}"]')

    # Add child node instances
    if children:
        for child in children:
            resource_id = ext_resources[child['path']]
            content_lines.append(f'[node name="{child[\'name\']}" parent="." instance=ExtResource("{resource_id}")]')

    content = "\n".join(content_lines) + "\n" # Add trailing newline
    print("content: ", content)

    with open(scene_file_path, 'w') as f:
        f.write(content)
        print(f"Writing scene file: {scene_file_path}")
    print(f"Scene written: {scene_file_path}")


def create_godot_project(project_name, project_path, assets_path, godot_executable="godot"):
    project_dir = os.path.join(project_path, project_name)
    assets_dir = os.path.join(project_dir, "assets")

    os.makedirs(assets_dir, exist_ok=True)

    # Create a basic project.godot
    # Ensure the main scene path uses forward slashes for Godot compatibility
    main_scene_godot_path = "res://Node4D.tscn"
    project_file_content = f"""
    [gd_engine]
    config_version=5

    [application]
    config/name="{project_name}"
    run/main_scene="{main_scene_godot_path}"
    config/features=PackedStringArray("4.3", "Forward Plus")
    config/icon="res://icon.svg"
    """


    with open(os.path.join(project_dir, "project.godot"), "w") as f:
        f.write(project_file_content.strip()) # Use strip() to remove leading/trailing whitespace

    # Copy assets
    if os.path.exists(assets_path):
        for item in os.listdir(assets_path):
            s = os.path.join(assets_path, item)
            d = os.path.join(assets_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print("Assets copied.")
    else:
        print(f"Assets path does not exist: {assets_path}")

    print("write_scene_file")

    # Define scene paths relative to the project root (res://)
    node4d_scene_path = "Node4D"
    node3d_scene_path = "Node4D/Node3D"
    node2d_scene_path = "Node4D/Node2D"
    control_scene_path = "Node4D/Node2D/Control"

    # Create leaf scenes first
    write_scene_file(project_dir, node3d_scene_path, "Node3D")
    write_scene_file(project_dir, control_scene_path, "Control")

    # Create Node2D scene and link Control scene as a child
    node2d_children = [
        {'path': f'res://{control_scene_path}.tscn', 'name': 'Control'}
    ]
    write_scene_file(project_dir, node2d_scene_path, "Node2D", children=node2d_children)

    # Create Node4D (root) scene and link Node2D and Node3D scenes as children
    node4d_children = [
        {'path': f'res://{node2d_scene_path}.tscn', 'name': 'Node2D'},
        {'path': f'res://{node3d_scene_path}.tscn', 'name': 'Node3D'}
    ]
    write_scene_file(project_dir, node4d_scene_path, "Node", children=node4d_children) # Use "Node" as base type


    print("write_scene_file done")

    # Run Godot CLI to import assets (if needed) and open the editor
    # Using --headless might be better if you only need asset importing without opening the editor
    # subprocess.run([godot_executable, "--headless", "--path", project_dir, "--import"])
    # print("Godot asset import process initiated.")
    # Or open the editor directly:
    subprocess.run([godot_executable, "--editor", "--path", project_dir])
    print("Godot editor opened for project.")

# Example usage:
if __name__ == "__main__":

    # locate project.ini in this or parent or parent parent directory
    # and use that as the project path
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # if current dir contains project.ini set asset_path ./GameFiles/Models/tmp
    # else if parent dir contains project.ini set asset_path Modules/Model/GameFiles/Models/tmp
    project_path = None
    assets_path = None
    search_dir = current_dir
    for i in range(3):
        potential_path = os.path.join(search_dir, 'project.ini')
        if os.path.exists(potential_path):
            project_path = search_dir
            if i == 0:
                # current dir
                assets_path = os.path.join(search_dir, 'GameFiles', 'Models', 'tmp')
            elif i > 0:
                # parent dir
                assets_path = os.path.join(search_dir, 'GameFiles', 'Models')
                project_path = os.path.join(search_dir, 'GameFiles', 'GodotGame')
            else:
                # fallback, just use a default or None
                assets_path = None
            break
        search_dir = os.path.dirname(search_dir)

    # tmp path
    assets_path = ".\\Modules\\Model\\GameFiles\\Main\\PS3_GAME\\Blender_TMP_OUTPUT\\"

    if project_path is None or assets_path is None:
        print("Could not locate project.ini or determine assets_path.")
    else:
        create_godot_project(
            project_name="Game",
            project_path=project_path,
            assets_path=assets_path,
            godot_executable="A:\\Godot_v4.4.1-stable_mono_win64\\Godot_v4.4.1-stable_mono_win64_console.exe"
        )
