import os
import shutil
import subprocess
import json

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

def create_godot_project(project_name: str, project_path: str, assets_path: str, script_path: str, json_path: str, asset_extension: str, godot_executable: str="godot") -> None:
    """Creates a Godot project with the given name and assets."""
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
        f.write(project_file_content.strip())

    # Copy assets recursively, filtering by extension and maintaining structure
    if os.path.exists(assets_path):
        print(f"Copying assets with extension '{asset_extension}' from {assets_path} to {assets_dir}...")
        copied_count = 0
        for root, dirs, files in os.walk(assets_path):
            for filename in files:
                if filename.lower().endswith(asset_extension.lower()):
                    source_file_path = os.path.join(root, filename)
                    # Calculate relative path to maintain structure
                    relative_path = os.path.relpath(source_file_path, assets_path)
                    destination_file_path = os.path.join(assets_dir, relative_path)

                    # Ensure destination directory exists
                    destination_dir = os.path.dirname(destination_file_path)
                    os.makedirs(destination_dir, exist_ok=True)

                    # Copy the file
                    shutil.copy2(source_file_path, destination_file_path)
                    copied_count += 1
        if copied_count > 0:
            print(f"Assets copied: {copied_count} file(s).")
        else:
            print(f"No assets found with extension '{asset_extension}' in {assets_path}.")
    else:
        print(f"Assets path does not exist: {assets_path}")

    # Copy scene_config.json into the project
    if os.path.exists(json_path):
        shutil.copy2(json_path, os.path.join(project_dir, "scene_config.json"))
        print("scene_config.json copied into the project.")
    else:
        print(f"JSON config path does not exist: {json_path}")

    # Copy the EditorScript into the project directory
    editor_script_dest_path = os.path.join(project_dir, os.path.basename(script_path))
    if os.path.exists(script_path):
        shutil.copy2(script_path, editor_script_dest_path)
        print(f"{os.path.basename(script_path)} copied into the project.")
    else:
        print(f"Editor script path does not exist: {script_path}")
        return # Exit if the script doesn't exist

    # Construct the res:// path for the script
    script_res_path = os.path.basename(script_path)

    # Run the GDScript
    subprocess.run([
        godot_executable,
        #"--headless",
        "--editor",
        "--path", project_dir,
        "--build-solutions",
        "--script", script_res_path # Use the res:// path inside the project
    ])

    print("Godot editor script execution attempted.") # Changed message for clarity

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
    assets_path = ".\\Modules\\Model\\GameFiles\\test"

    json_path = os.path.join(current_dir, 'scene_config.json')

    if project_path is None or assets_path is None or json_path is None:
        print("Could not locate project.ini or determine assets_path or json_path.")
    else:
        create_godot_project(
            project_name="Game",
            project_path=project_path,
            assets_path=assets_path,
            script_path=os.path.join(current_dir, "EditorScript.gd"),
            json_path=json_path,
            asset_extension=".blend", # Specify the desired asset extension here
            godot_executable="A:\\Godot_v4.4.1-stable_mono_win64\\Godot_v4.4.1-stable_mono_win64_console.exe"
        )
