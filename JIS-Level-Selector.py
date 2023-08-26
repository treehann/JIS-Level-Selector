import os
import shutil
import string
import subprocess

# This file was assembled at the macro level by an AI so it's probably messy, continue with caution.
# I was too lazy but also didn't have enough time to actually make this thing from end to end,
# however a lot of manual effort was put in to assemble, refactor, and debug it.       -treehann

# *****************************************************************************************
# Constants
EXCLUDED_FILES = ["main.yaml","worlds.yaml"]
DEV_LEVELS = ["bonus.yaml","bonus_2.yaml","demo.yaml","meta.yaml","new_meta.yaml","recycle.yaml","test.yaml"]
DEFAULT_LEVEL_CONTENT = """levels:
  - name: Default-Level
    music: Vestibulum.mp3
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
DEFAULT_SAVE_CONTENT = """# Jelly save file

solved_levels:
"""
LEVEL_BACKUP_FOLDER_NAME = "JISLS-backup"
PFF_NAME = "JISLS-previous-filename.txt"

# *****************************************************************************************
# Function group: Miscellaneous / Helper -- not including filesystem functions

def print_intro():
    print("+-------------------------------------------------------------------------+")
    print("|    Jelly is Sticky Level Selector v1.21 by treehann, aided by GPT-4     |")
    print("|    Exit this program before running Jelly is Sticky to avoid errors.    |")
    print("|  Report bugs to: treehann.prod@gmail.com / discord.com/invite/yNEJvzZ   |")
    print("+-------------------------------------------------------------------------+\n")

def rename_to_valid_filename(levelname):
    """Convert a levelname to a valid filename. (String conversions only, no I/O)"""
    valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c if c in valid_chars else '-' for c in levelname)
    return filename

# *****************************************************************************************
# Function group: Filesystem Operations -- anything using os, or open/write/close of files
def get_ld():
    """Locate and return the Level Directory."""
    paths_to_check_LD = [
        ".",
        "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Jelly Is Sticky\\asset\\level",
        "C:\\Program Files\\Steam\\steamapps\\common\\Jelly Is Sticky\\asset\\level"
    ]

    for path in paths_to_check_LD:
        if os.path.isfile(os.path.join(path, "worlds.yaml")):
            if path == ".":
                print("Program was run from the level directory containing worlds.yaml.")
            else:
                print("Found the level directory containing worlds.yaml. Program was run from elsewhere.")
            return path
    user_path = input("Could not auto-locate level directory. Please input path manually: ")
    if os.path.isfile(os.path.join(user_path, "worlds.yaml")):
        print("Successfully input level directory path containing worlds.yaml.")
        return user_path
    return None
    
def get_gd(ld):
    # Navigate two directories up
    gd = os.path.join(ld, "..", "..")
    gd = os.path.abspath(gd)  # Convert to absolute path
    
    # Check if the jelly.exe exists in that directory
    if os.path.exists(os.path.join(gd, "jelly.exe")):
        print("Found the game directory containing jelly.exe.")
    else:
        print("Cannot find game directory containing jelly.exe.")
    
    return gd

def get_udd():
    """Locate and return the User Data Directory."""
    
    # Get the current logged in username
    current_user = os.getlogin()

    # Construct the default path
    default_path = f"C:\\Users\\{current_user}\\AppData\\Roaming\\Lunarch Studios\\Jelly Is Sticky"

    # Construct the full path to the config.yaml file within the default path
    config_path = os.path.join(default_path, "config.yaml")

    # Check if the config.yaml file exists at the default path
    if os.path.exists(config_path):
        print("Found the AppData directory containing config.yaml.")
        return default_path

    # If not found, prompt the user for the path
    manual_input_path = input("Could not auto-locate AppData directory containing config.yaml. Please input path manually: ")
    if os.path.isfile(os.path.join(manual_input_path, "config.yaml")):
        print("Successfully input AppData directory containing config.yaml.")
        return manual_input_path

    # If still not found, print a message
    print("Could not locate AppData directory containing config.yaml.")
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

def create_shortcut(target, path, name):
    """Creates a shortcut using Windows Scripting Host."""

    shortcut_path = os.path.join(path, f"{name}.lnk")

    # Check if the shortcut already exists
    if os.path.exists(shortcut_path):
        return False

    # VBScript to create the shortcut
    vbscript = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{target}"
    oLink.Save
    """

    # Execute the VBScript
    with open("temp_create_shortcut.vbs", "w") as f:
        f.write(vbscript)

    subprocess.run(["cscript", "temp_create_shortcut.vbs"], shell=True, check=True, capture_output=True)

    # Clean up the temporary VBScript file
    os.remove("temp_create_shortcut.vbs")

    return True

def update_worlds_file(ld, num):
    """Sets the second num_levels key of worlds.yaml to num"""
    filename = f'{ld}/worlds.yaml'  # Incorporating the directory into the filename

    # 1. Read all lines from the file into a list
    with open(filename, 'r') as file:
        lines = file.readlines()

    # 2. Identify the line containing num_levels for WORLD_Custom
    # We'll find the line after the one containing "name: WORLD_Custom"
    for index, line in enumerate(lines):
        if "name: WORLD_Custom" in line:
            target_index = index + 3  # The num_levels line is 3 lines after the name line
            break

    target_line = lines[target_index]

    # 3. Replace the number at the end of the target line
    # Use regex to identify and replace the number at the end of the line
    import re
    updated_line = re.sub(r'(\d+)$', str(num), target_line)
    lines[target_index] = updated_line

    # 4. Write the updated lines back to the file
    with open(filename, 'w') as file:
        file.writelines(lines)

def check_exist_key_files(ld, udd):
    """ If there is not custom.yaml in the level directory or save_custom.yaml in the AppData directory, creates them"""
    cy_warning = False
    scy_warning = False
    
    cy_path = os.path.join(ld, "custom.yaml")
    if not os.path.exists(cy_path):
        print("WARNING: Did not find custom.yaml in level directory, which is unusual. Just queued a new blank level.")
        with open(os.path.join(ld, "custom.yaml"), 'w') as f:
            f.write(DEFAULT_LEVEL_CONTENT)
        cy_warning = True
        
        # new level = clear worlds file and PFF (previous filename file)
        update_worlds_file(ld, 1)
        pff_file_path = os.path.join(ld, PFF_NAME)
        if os.path.exists(pff_file_path):
            open(pff_file_path, 'w').close()
    
    scy_path = os.path.join(udd, "save_custom.yaml")
    if not os.path.exists(scy_path):
        print("WARNING: Did not find save_custom.yaml in AppData directory, which is unusual. Just created a new empty one.")
        with open(os.path.join(udd, "save_custom.yaml"), 'w') as f:
            f.write(DEFAULT_SAVE_CONTENT)
        scy_warning = True
    
    if(not cy_warning and not scy_warning):
        print("Found custom.yaml & save_custom.yaml in their expected directories (1st & 3rd above).")
    elif((cy_warning and not scy_warning) or (scy_warning and not cy_warning)): 
        print("WARNING: You may have a level file (custom.yaml) and save file (save_custom.yaml) mismatch now")
        print("because one had to be recreated and the other did not. If you are concerned about losing save data")
        print("for either the current custom level or the previously-loaded one (there is no danger to the main game),")
        print("please consult this program's developer, the Discord, or the Steam community.")

# *****************************************************************************************
# Function group: User Actions
def show_level_list(ld):
    """Display the list of levels."""
    print("\nLevels available:")
    yll = fetch_yll(ld)

    # Calculate dynamic column widths
    index_width = len(str(len(yll) - 1)) 
    filename_width = max(len(lf) for lf in yll)
    levelname_width = max(len(read_levelname_from_file(os.path.join(ld, lf))) for lf in yll)

    for idx, lf in enumerate(yll):
        levelname = read_levelname_from_file(os.path.join(ld, lf))
        
        # Determine the label for the fourth column
        if idx == 0:
            status_label = "QUEUED"
        elif lf in DEV_LEVELS:
            status_label = "DEV"
        else:
            status_label = "USER"

        print(f"{idx:{index_width}}. {lf:{filename_width}} {levelname:{levelname_width}} {status_label}")



def queue_level_for_playing(ld, udd):
    """Replace custom.yaml with user's selected level."""
    show_level_list(ld)
    yll = fetch_yll(ld)
    while True:
        try:
            choice = int(input("\nInput the number of a level from the list above to queue it,\nor a negative number to cancel. ---> Input: "))
            if choice < 0:
                # break completely out
                return True
            elif 0 <= choice < len(yll):
                if yll[choice] == "custom.yaml":
                    print("That level is already queued. Please make another choice.")
                    continue
                break
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")

    # Create backup folder and PFF
    backup_path = os.path.join(ld, LEVEL_BACKUP_FOLDER_NAME)
    if not os.path.exists(backup_path):
        os.mkdir(backup_path)
    if not os.path.exists(os.path.join(ld, PFF_NAME)):
        with open(os.path.join(ld, PFF_NAME), 'w') as f:
            f.write('')
    backup_path_2 = os.path.join(udd, LEVEL_BACKUP_FOLDER_NAME)
    if not os.path.exists(backup_path_2):
        os.mkdir(backup_path_2)

    # Renaming existing custom.yaml (and save_custom.yaml)
    clevelname = read_levelname_from_file(os.path.join(ld, "custom.yaml"))
    new_filename="invalid_filename.yaml"
    with open(os.path.join(ld, PFF_NAME), 'r') as f:
        previous_name = f.read()
    if previous_name and not clevelname == "Default-level":
        new_filename = rename_to_windows_duplicate_format(ld, previous_name)
        os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_filename))
        
        # Make corresponding save name with new filename. Need to delete the old ond first if it exists.
        new_savename = f"save_{new_filename}"
        new_save_dest = os.path.join(udd, new_savename)
        if os.path.exists(new_save_dest):
            os.remove(new_save_dest)
        os.rename(os.path.join(udd, "save_custom.yaml"), os.path.join(udd, new_savename))
    else:
        filename = rename_to_valid_filename(clevelname) + ".yaml"
        new_filename = rename_to_windows_duplicate_format(ld, filename)
        os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_filename))
        
        # Make corresponding save name with new filename. Need to delete the old ond first if it exists.
        new_savename = f"save_{new_filename}"
        new_save_dest = os.path.join(udd, new_savename)
        if os.path.exists(new_save_dest):
            os.remove(new_save_dest)
        os.rename(os.path.join(udd, "save_custom.yaml"), os.path.join(udd, new_savename))
        
    # Delete custom.yaml_backup if it exists
    unneeded_backup_filename = os.path.join(ld, 'custom.yaml_backup')
    if os.path.exists(unneeded_backup_filename):
        os.remove(unneeded_backup_filename)
    unneeded_backup_filename2 = os.path.join(udd, 'save_custom.yaml_backup')
    if os.path.exists(unneeded_backup_filename2):
        os.remove(unneeded_backup_filename2)
    
    # Make a backup of the chosen level's yaml file
    shutil.copy(os.path.join(ld, yll[choice]), backup_path)
    
    # Create the new custom.yaml (by renaming list item) and updating the PFF.     
    with open(os.path.join(ld, PFF_NAME), 'w') as f:
        f.write(yll[choice])
    os.rename(os.path.join(ld, yll[choice]), os.path.join(ld, "custom.yaml"))
    
    # Create the new save_custom.yaml from an existing save file matching the chosen level's filename, if such a thing exists
    matching_save_filename = f"save_{yll[choice]}"
    if os.path.isfile(os.path.join(udd, matching_save_filename)):
        # back it up
        shutil.copy(os.path.join(udd, matching_save_filename), backup_path_2)
        
        # rename it to save_custom.yaml
        os.rename(os.path.join(udd, matching_save_filename), os.path.join(udd, 'save_custom.yaml'))
        
        print(f"\nFound and loaded the save data for this level.")
    else:
        # otherwise create a fresh one
        with open(os.path.join(udd, "save_custom.yaml"), 'w') as f:
            f.write(DEFAULT_SAVE_CONTENT)
        
        print(f"\nNo save data found for this level. New blank save file created.")
    
    print(f"~~~ Successfully queued {read_levelname_from_file(os.path.join(ld, 'custom.yaml'))} ~~~")
    print("Remember to exit this program before opening Jelly is Sticky.")
        
    # Set worlds count correctly
    c_filename = "custom.yaml"
    c_file_path = f"{ld}/{c_filename}"
    with open(c_file_path, 'r') as c_file:
        c_content = c_file.read()
        w_count = c_content.count("name:")  
    update_worlds_file(ld, w_count)

def queue_blank_level(ld, udd):
    """Create a blank level in custom.yaml."""
    
    # rename custom.yaml
    levelname = read_levelname_from_file(os.path.join(ld, "custom.yaml"))
    new_name = rename_to_windows_duplicate_format(ld, f"{rename_to_valid_filename(levelname)}.yaml")
    os.rename(os.path.join(ld, "custom.yaml"), os.path.join(ld, new_name))

    # write a new custom.yaml
    with open(os.path.join(ld, "custom.yaml"), 'w') as f:
        f.write(DEFAULT_LEVEL_CONTENT)
    
    # update worlds count
    update_worlds_file(ld, 1)
    
    # rename save_custom.yaml. Need to delete the old ond first if it exists.
    new_save_name = f"save_{new_name}"
    new_save_dest = os.path.join(udd, new_save_name)
    if os.path.exists(new_save_dest):
        os.remove(new_save_dest)
    os.rename(os.path.join(udd, "save_custom.yaml"), os.path.join(udd, new_save_name))
    
    # write a new save_custom.yaml
    with open(os.path.join(udd, "save_custom.yaml"), 'w') as f:
        f.write(DEFAULT_SAVE_CONTENT)
    
    print("Wrote new blank save data.")
    print("~~~ Successfully queued blank level. ~~~")
    print("Remember to exit this program before opening Jelly is Sticky.")
    
    # Clear the PFF, to prevent the fresh level being renamed something unintended when it is moved out of the queue
    pff_file_path = os.path.join(ld, PFF_NAME)
    if os.path.exists(pff_file_path):
        open(pff_file_path, 'w').close()


def open_level_directory(ld):
    """Open the Level Directory in Windows Explorer."""
    os.system(f'explorer {os.path.abspath(ld)}')

def create_shortcuts(ld):
    wd = os.getcwd()
    
    #normalize paths to make them comparable
    normalized_wd = os.path.normpath(os.path.abspath(wd))
    normalized_ld = os.path.normpath(os.path.abspath(ld))

    if normalized_wd == normalized_ld:
        print("The current directory from which JISLS was run is already the level directory. Canceling.")
        returnaps

    shortcuts_created = 0

    # Puts a shortcut to the LD in the WD named “level directory - Shortcut”
    if create_shortcut(ld, wd, "level directory - Shortcut"):
        shortcuts_created += 1

    # Puts a shortcut to the WD in the LD named “JIS-Level-Selector directory - Shortcut”
    if create_shortcut(wd, ld, "JIS-Level-Selector directory - Shortcut"):
        shortcuts_created += 1

    # Puts a shortcut to itself (the Python program) in the LD named “JIS-Level-Selector.py - Shortcut”
    current_script_path = os.path.abspath(__file__)
    if create_shortcut(current_script_path, ld, "JIS-Level-Selector.py - Shortcut"):
        shortcuts_created += 1

    extra_note = ""
    the_s = "s"
    if(shortcuts_created == 0):
        extra_note = ". All were already present."
    if(shortcuts_created == 1):
        the_s = ""
    print(f"Created {shortcuts_created} shortcut{the_s}{extra_note}")

def launch_jis(gd):
        # If jelly.exe isn't running, launch it from the given directory (gd)
    jelly_path = os.path.join(gd, 'jelly.exe')
    if os.path.exists(jelly_path):
        subprocess.Popen(jelly_path, cwd=gd)  # setting cwd ensures the game runs in its directory
    else:
        print(f"Cannot find {jelly_path}. Ensure it exists in the specified directory.")

# *****************************************************************************************
# Function Group: Main
def main():
    """Main loop."""
    print_intro()
    
    # get important directories
    ld = get_ld()
    if not ld:
        print("Cannot find Jelly is Sticky level directory containing worlds.yaml.")
        input("Press any key...")
        return
    
    gd = get_gd(ld)
    udd = get_udd()
    
    # show warning if custom.yaml or save_custom.yaml are not found in those directories, and create those files
    check_exist_key_files(ld, udd)

    while True:
        tluoI = 1
        print("\n"+str(tluoI)+" - Show level list")
        tluoI += 1
        print(str(tluoI)+" - QUEUE EXISTING level for playing or editing")
        tluoI += 1
        print(str(tluoI)+" - QUEUE BLANK level for new level creation")
        tluoI += 1
        print(str(tluoI)+" - Open level directory in Windows Explorer")
        tluoI += 1
        print(str(tluoI)+" - Create shortcuts between current directory and level directory")
        tluoI += 1
        print(str(tluoI)+" - Exit program")
        tluoI += 1
        print(str(tluoI)+" - Exit program and run Jelly Is Sticky")
        try:
            choice = int(input("\nInput a number to choose from the options above: "))
            if choice == 1:
                show_level_list(ld)
            elif choice == 2:
                queue_level_for_playing(ld, udd)
            elif choice == 3:
                queue_blank_level(ld, udd)
            elif choice == 4:
                open_level_directory(ld)
            elif choice == 5:
                create_shortcuts(ld)
            elif choice == 6:
                break
            elif choice == 7:
                launch_jis(gd)
                break
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")

if __name__ == '__main__':
    main()
