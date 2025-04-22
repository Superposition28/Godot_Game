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

def write_scene_file(base_dir, relative_path, node_type="Node"):
    """
    Creates a .tscn file at base_dir/relative_path.tscn
    Ensures all parent directories exist.
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

    content = f"""[gd_scene load_steps=2 format=3]
    [node name="{node_name}" type="{node_type}"]
    """
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
    project_file_content = f"""
    [gd_project_settings]
    config_version=4

    [application]
    config/name="{project_name}"
    run/main_scene="res://Node4D.tscn"
    """


    with open(os.path.join(project_dir, "project.godot"), "w") as f:
        f.write(project_file_content)

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

    # Use a valid Godot node type for the root scene
    write_scene_file(project_dir, "Node4D", "Node")
    write_scene_file(project_dir, "Node4D/Node2D", "Node2D")
    write_scene_file(project_dir, "Node4D/Node2D/Control", "Control")
    write_scene_file(project_dir, "Node4D/Node3D", "Node3D")

    # Run Godot CLI to import assets
    subprocess.run([godot_executable, "--editor", "--path", project_dir])
    print("Godot project initialized via CLI.")

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
                assets_path = os.path.join(search_dir, 'Modules', 'Model', 'GameFiles', 'Models', 'tmp')
                project_path = os.path.join(search_dir, 'Modules', 'Godot')
            else:
                # fallback, just use a default or None
                assets_path = None
            break
        search_dir = os.path.dirname(search_dir)

    #tmp path
    assets_path = "A:\Dev\Games\TheSimpsonsGame\Modules\Model_Assets\GameFiles\Main\PS3_GAME\Blender_TMP_OUTPUT"

    if project_path is None or assets_path is None:
        print("Could not locate project.ini or determine assets_path.")
    else:
        create_godot_project(
            project_name="Game",
            project_path=project_path,
            assets_path=assets_path,
            godot_executable="A:\\Godot_v4.4.1-stable_mono_win64\\Godot_v4.4.1-stable_mono_win64_console.exe"
        )
