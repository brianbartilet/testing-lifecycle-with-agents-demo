import shutil
import os
import time

PYTHON_VERSION = "python3.12"


def copy_directory(source_dir, target_dir):
    """
    Copies a directory from a source to a target location.

    Args:
        source_dir (str): The path of the source directory to be copied.
        target_dir (str): The path of the target directory where the source directory will be copied.

    Prints a success message if the directory is copied successfully, otherwise prints an error message.
    """
    try:
        # Check if the target directory already exists
        if os.path.exists(target_dir):
            # If it exists, remove it to avoid errors
            shutil.rmtree(target_dir)
        # Copy the source directory to the target directory
        shutil.copytree(source_dir, target_dir)
        print(f"Directory {source_dir} copied to {target_dir} successfully.")
    except Exception as e:
        print(f"Error copying directory: {e}")


if __name__ == "__main__":

    version = PYTHON_VERSION if os.getenv("ENV").lower() == "test" else ""
    source_base = os.path.join(os.getcwd(), "venv", "lib", f"{version}", "site-packages", "core")
    # Specify the source and target directories
    source_directory_demo = os.path.join(source_base, "demo")
    target_directory_demo = os.path.join(os.getcwd(), "demo")

    source_directory_docs = os.path.join(source_base, "docs")
    target_directory_docs = os.path.join(os.getcwd(), "docs")

    # Call the function to copy the directory
    copy_directory(source_directory_demo, target_directory_demo)
    copy_directory(source_directory_docs, target_directory_docs)

    # Move pytest.ini to root directory
    time.sleep(1)
    source_file_ini = os.path.join(os.getcwd(), "demo", "pytest.ini")  # Use the correct file extension
    destination_file_ini = os.path.join(os.getcwd())

    shutil.copy(source_file_ini, destination_file_ini)
    print(f"File {source_file_ini} moved to {destination_file_ini} successfully.")

    # Move the config.yml to root directory
    time.sleep(1)
    source_file = os.path.join(os.getcwd(), "demo", "sample_config.yaml")  # Use the correct file extension
    destination_file = os.path.join(os.getcwd())
    destination_file_check = os.path.join(os.getcwd(), "sample_config.yaml")

    # Check if the file exists in the source
    if os.path.exists(source_file):
        # Check if the file already exists in the destination
        if os.path.exists(destination_file_check):
            os.remove(source_file)
            print(f"File {destination_file} already exists. Removed template configuration.")
        else:
            shutil.move(source_file, destination_file)
            print(f"File {source_file} moved to {destination_file} successfully.")
    else:
        print(f"File {source_file} does not exist.")

