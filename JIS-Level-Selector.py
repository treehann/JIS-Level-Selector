import yaml
import os

def find_name_in_yaml2(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        # Check if 'levels' key exists and it's a sequence
        if 'levels' in data and isinstance(data['levels'], list):
            for level in data['levels']:
                if 'name' in level:
                    return level['name']
    return None
    
def find_name_in_yaml(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if "name: " in line:
                return line.split("name: ", 1)[1].strip()
    return None


def check_directory_for_worlds_yaml(directory):
    return os.path.exists(os.path.join(directory, "worlds.yaml"))

def main():
    try:
        print("Jelly is Sticky Level Selector by treehann & GPT-4, version 1.0")

        script_dir = os.path.dirname(os.path.realpath(__file__))
        steam_dirs = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Jelly Is Sticky\asset\level",
            r"C:\Program Files\Steam\steamapps\common\Jelly Is Sticky\asset\level"
        ]

        # Check current directory for worlds.yaml
        if check_directory_for_worlds_yaml(script_dir):
            working_dir = script_dir
            print("Script was run from the Jelly is Sticky levels folder.")
        else:
            # Search for worlds.yaml in the specified Steam directories
            for dir in steam_dirs:
                if check_directory_for_worlds_yaml(dir):
                    working_dir = dir
                    print("Located Jelly is Sticky level directory. Script was run from elsewhere.")
                    break
            else:
                print("Cannot find Jelly is Sticky level directory.")
                input("Press any key to exit...")
                return

        # Get all yaml files in the working directory, prioritizing 'custom.yaml'
        yaml_files = sorted([f for f in os.listdir(working_dir) if f.endswith('.yaml') and f != 'custom.yaml'])
        if 'custom.yaml' in os.listdir(working_dir):
            yaml_files.insert(0, 'custom.yaml')

        # Determine the width required for the index based on the number of yaml files
        idx_width = len(str(len(yaml_files)))

        # Determine the width required for the file names
        max_len = max(len(f) for f in yaml_files)

        # Display all yaml files with their corresponding 'name' key in the 'levels' sequence
        print("\nFiles in the directory:")
        for idx, yaml_file in enumerate(yaml_files, 1):
            full_path = os.path.join(working_dir, yaml_file)
            level_name = find_name_in_yaml(full_path)
            
            # If the file has no 'levels' sequence with a 'name' key, skip it
            if not level_name:
                continue

            print(f"{idx:>{idx_width}}. {yaml_file:{max_len}} : {level_name}")

        print("\nChoose an action from the following by inputting its number:")
        print("1. Queue a level for playing")
        print("2. Queue a blank level for editing")
        print("3. Exit")

        while True:
            user_choice = input("Your choice: ")

            if user_choice == "1" or user_choice == "2":
                print("\nChoose an action from the following by inputting its number:")
                print("1. Queue a level for playing")
                print("2. Queue a blank level for editing")
                print("3. Exit")
            elif user_choice == "3":
                break  # Exit the loop and end the script
            else:
                print("The input was not valid, please try again.")

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press any key to exit...")

if __name__ == "__main__":
    main()
