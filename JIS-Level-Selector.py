import yaml
import os

def find_name_in_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        # Check if 'levels' key exists and it's a sequence
        if 'levels' in data and isinstance(data['levels'], list):
            for level in data['levels']:
                if 'name' in level:
                    print(level['name'])
                    return  # Assuming you want to print the first 'name' found and then exit
            print("'name' key not found inside any item in 'levels'.")
        else:
            print("'levels' sequence not found or not a list in yaml data.")

def check_directory_for_worlds_yaml(directory):
    return os.path.exists(os.path.join(directory, "worlds.yaml"))

def main():
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
            return

    # At this point, working_dir is set to where worlds.yaml was found
    # If further operations need to use the 'custom.yaml' in this directory, use os.path.join(working_dir, 'custom.yaml')

    input("Press any key to exit...")

if __name__ == "__main__":
    main()
