import os
import shutil
import string

# Constants
EXCLUDED_FILES = ["bonus.yaml","bonus_2.yaml","demo.yaml","main.yaml","meta.yaml","new-meta.yaml","recycle.yaml","test.yaml","worlds.yaml"]
DEFAULT_LEVEL_CONTENT = """levels:
  - name: Default-Level
    blocks: |
      ######
      #....#
      #.R..#
      #....#
      #....#
      ######
    goals: |
      ######
      #....#
      #.@..#
      #..r.#
      #....#
      ######
    deco_default: 0"""
BACKUP_FOLDER_NAME = "JISLS-backup"
PFF_NAME = "JISLS-previous-filename.txt"

# Function group: Filesystem Operations
def get_ld():
    """Locate and return the Level Directory."""
    paths_to_check = [
        ".",
        "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Jelly Is Sticky\\asset\\level",
        "C:\\Program Files\\Steam\\steamapps\\common\\Jelly Is Sticky\\asset\\level"
    ]

    for path in paths_to_check:
        if os.path.isfile(os.path.join(path, "main.yaml")):
            if path == ".":
                print("Program was run from the Jelly is Sticky levels folder containing main.yaml.")
            else:
                print("Located Jelly is Sticky level directory containing main.yaml. Program was run from elsewhere.")
            return path
    user_path = input("Could not auto-locate level directory. Please input path manually: ")
    if os.path.isfile(os.path.join(user_path, "main.yaml")):
        return user_path
    return None

def fetch_yll(ld):
    """Return a list of level filenames excluding specified files and including custom.yaml at the beginning if it exists."""
    files = [f for f in os.listdir(ld) if f.endswith('.yaml') and f not in EXCLUDED_FILES]
    if 'custom.yaml' in files:
        files.remove('custom.yaml')
        files.insert(0, 'custom.yaml')
    return files

def read_levelname_from_file(filepath):
    """Return the levelname from a given file."""
    with open(filepath, 'r') as f:
        for line in f.readlines():
            if "name:" in line:
                return line.split("name:")[1].strip()
    return None

def rename_to_windows_duplicate_format(file_path, proposed_name):
    """Rename a file to a Windows-like format, such as (1), (2), etc. if conflicts occur."""
    counter = 1
    name, ext = os.path.splitext(proposed_name)
    new_name = proposed_name
    while os.path.exists(os.path.join(file_path, new_name)):
        new_name = f"{name} ({counter}){ext}"
        counter += 1
    return new_name

def rename_to_valid_filename(levelname):
    """Convert a levelname to a valid filename."""
    valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c if c in valid_chars else '-' for c in levelname)
    return filename

# Function group: User Actions
def show_level_list(ld):
    """Display the list of levels."""
    print("\nLevels available:")
    yll = fetch_yll(ld)

    # Find out the maximum width needed for the index
    max_width = len(str(len(yll)-1))
    
    for idx, lf in enumerate(yll):
        levelname = read_levelname_from_file(os.path.join(ld, lf))
        print(f"{idx:{max_width}}. {lf:20} {levelname}")


def queue_level_for_playing(ld):
    """Replace custom.yaml with user's selected level."""
    show_level_list(ld)
    print("Note: Levels from Jelly is Sticky’s original developers may not work.")
    yll = fetch_yll(ld)
    while True:
        try:
            choice = int(input("Input the number of a level from the list above: "))
            if 0 <= choice < len(yll):
                if yll[choice] == "custom.yaml":
                    print("That level is already queued. Please make another choice.")
                    continue
                break
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")

    # Creating backup folder and PFF
    backup_path = os.path.join(ld, BACKUP_FOLDER_NAME)
    if not os.path.exists(backup_path):
        os.mkdir(backup_path)
    if not os.path.exists(os.path.join(ld, PFF_NAME)):
        with open(os.path.join(ld, PFF_NAME), 'w') as f:
            f.write('')

    # Renaming existing custom.yaml
    clevelname = read_levelname_from_file(os.path.join(ld, "custom.yaml"))
    with open(os.path.join(ld, PFF_NAME), 'r') as f:
        previous_name = f.read()
    if previous_name and not clevelname == "Default-level":
        new_filename = rename_to_windows_duplicate_format(ld, previous_name)
        os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_filename))
    else:
        filename = rename_to_valid_filename(clevelname) + ".yaml"
        new_filename = rename_to_windows_duplicate_format(ld, filename)
        os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_filename))
        
    # Delete custom.yaml_backup if it exists
    unneeded_backup_filename = os.path.join(ld, 'custom.yaml_backup')
    if os.path.exists(unneeded_backup_filename):
        os.remove(unneeded_backup_filename)

    # Copying the new custom.yaml and updating the PFF
    shutil.copy(os.path.join(ld, yll[choice]), backup_path)
    with open(os.path.join(ld, PFF_NAME), 'w') as f:
        f.write(yll[choice])
    os.rename(os.path.join(ld, yll[choice]), os.path.join(ld, "custom.yaml"))
    print(f"\n~~~ Successfully queued {read_levelname_from_file(os.path.join(ld, 'custom.yaml'))} ~~~")
    print("Remember to exit this program before opening Jelly is Sticky.")

def queue_blank_level(ld):
    """Create a blank level in custom.yaml."""
    
    levelname = read_levelname_from_file(os.path.join(ld, "custom.yaml"))
    new_name = rename_to_windows_duplicate_format(ld, f"{rename_to_valid_filename(levelname)}.yaml")
    os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_name))

    with open(os.path.join(ld, "custom.yaml"), 'w') as f:
        f.write(DEFAULT_LEVEL_CONTENT)

    print("\n~~~ Successfully queued blank level. ~~~")
    print("Remember to exit this program before opening Jelly is Sticky.")
    
    # Clear the PFF, to prevent the fresh level being renamed something unintended when it is moved out of the queue
    pff_file_path = os.path.join(ld, PFF_NAME)
    if os.path.exists(pff_file_path):
        open(pff_file_path, 'w').close()


def open_level_directory(ld):
    """Open the Level Directory in Windows Explorer."""
    os.system(f'explorer {os.path.abspath(ld)}')

def main():
    """Main loop."""
    print("Jelly is Sticky Level Selector by treehann & GPT-4, version 1.1")
    print("Exit this program before running Jelly is Sticky to avoid errors.")
    ld = get_ld()
    if not ld:
        print("Cannot find Jelly is Sticky level directory containing main.yaml.")
        input("Press any key...")
        return

    while True:
        print("\n1 - Show level list")
        print("2 - Queue level for playing or editing")
        print("3 - Queue blank level for new level creation")
        print("4 - Open level directory in Windows Explorer")
        print("5 - Exit program")
        try:
            choice = int(input("\nInput a number to choose from the options above: "))
            if choice == 1:
                show_level_list(ld)
            elif choice == 2:
                queue_level_for_playing(ld)
            elif choice == 3:
                queue_blank_level(ld)
            elif choice == 4:
                open_level_directory(ld)
            elif choice == 5:
                break
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")

if __name__ == '__main__':
    main()
