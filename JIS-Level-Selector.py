import os
import shutil
import yaml

def find_name_in_yaml(file_path):
    """Finds the first instance of "name: " in the file and returns the string after that."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if "name: " in line:
                    return line.split("name: ")[1].strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def get_working_directory():
    """Determine and return the working directory based on the presence of main.yaml."""
    possible_directories = [
        os.getcwd(),
        r"C:\Program Files (x86)\Steam\steamapps\common\Jelly Is Sticky\asset\level",
        r"C:\Program Files\Steam\steamapps\common\Jelly Is Sticky\asset\level"
    ]
    
    for directory in possible_directories:
        if os.path.exists(os.path.join(directory, 'main.yaml')):
            return directory

    return None

def list_yaml_files_with_names(working_dir):
    """List all YAML files with their associated level names."""
    all_files = sorted([f for f in os.listdir(working_dir) if f.endswith('.yaml') and f != 'worlds.yaml'])
   
    yaml_files = [('custom.yaml', find_name_in_yaml(os.path.join(working_dir, 'custom.yaml')))] \
                + [(f, find_name_in_yaml(os.path.join(working_dir, f))) for f in all_files if f != 'custom.yaml']

    print("\nLevels available:")
    print("(Note: Some included levels by the game developers aren't in a playable state)\n")
    # Determine the width required for the index based on the number of yaml files
    idx_width = len(str(len(yaml_files)))

    # Determine the width required for the file names
    max_len = max(len(f) for f in yaml_files)

    for idx, (filename, levelname) in enumerate(yaml_files, 1):
        print(f"{idx:>{idx_width}}. {filename:{max_len}} : {levelname}")

    return yaml_files

def queue_level(working_dir, yaml_files):
    """Queue a level based on user's choice."""
    backup_dir = os.path.join(working_dir, 'JISLS-backup')
    previous_filename_path = os.path.join(working_dir, 'JISLS-previous-filename.txt')

    # Create backup folder if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Create the previous filename record if it doesn't exist
    if not os.path.exists(previous_filename_path):
        with open(previous_filename_path, 'w') as file:
            file.write('')

    while True:
        choice = input("\nChoose a number from the list above: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(yaml_files):
            print("The input was not valid, please try again.")
            continue
        
        if choice == "1":
            print("That level is already queued. Choose another.")
            continue

        selected_file = yaml_files[int(choice) - 1][0]
        levelname_for_custom = find_name_in_yaml(os.path.join(working_dir, 'custom.yaml'))

        # Renaming custom.yaml to its previous name
        with open(previous_filename_path, 'r') as file:
            prev_filename = file.read().strip()
        
        if prev_filename:
            os.rename(os.path.join(working_dir, 'custom.yaml'), os.path.join(working_dir, prev_filename))
        else:
            os.rename(os.path.join(working_dir, 'custom.yaml'), os.path.join(working_dir, f"{levelname_for_custom}.yaml"))

        # Backup selected file
        shutil.copy(os.path.join(working_dir, selected_file), backup_dir)

        # Update the previous filename record
        with open(previous_filename_path, 'w') as file:
            file.write(selected_file)

        # Rename selected file to custom.yaml
        os.rename(os.path.join(working_dir, selected_file), os.path.join(working_dir, 'custom.yaml'))

        print(f"\n~~~ Successfully queued {yaml_files[int(choice) - 1][1]}. ~~~")
        return  # This will exit the function without displaying the list again

def open_directory_in_explorer(working_dir):
    """Open the directory in Windows Explorer."""
    os.startfile(working_dir)

def display_menu_and_get_choice():
    """Display the menu options and return the user's choice."""
    print("\nChoose an action from the following by inputting its number:")
    print("1. Queue a level for playing")
    print("2. Queue a blank level for editing")
    print("3. Open level directory in Explorer")
    print("4. Exit")

    return input("\nEnter your choice: ")

def main():
    """Main function to control the script flow."""
    print("Jelly is Sticky Level Selector by treehann & GPT-4, version 1.0")

    working_dir = get_working_directory()
    if not working_dir:
        print("Cannot find Jelly is Sticky level directory.")
        return

    if working_dir == os.getcwd():
        print("Script was run from the Jelly is Sticky levels folder.")
    else:
        print("Located Jelly is Sticky level directory. Script was run from elsewhere.")
    
    while True:
        yaml_files = list_yaml_files_with_names(working_dir)
        user_choice = display_menu_and_get_choice()

        if user_choice == "1":
            queue_level(working_dir, yaml_files)
        elif user_choice == "2":
            continue
        elif user_choice == "3":
            open_directory_in_explorer(working_dir)
        elif user_choice == "4":
            print("Exiting...")
            break
        else:
            print("The input was not valid, please try again.")

if __name__ == "__main__":
    main()
