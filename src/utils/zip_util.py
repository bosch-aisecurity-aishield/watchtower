import os
import shutil
import requests
from zipfile import ZipFile, BadZipFile

def list_files(base_path: str, target_path: str, extensions: list):
    # List to hold the paths of all files matching the given extension
    matching_files = []
    
    full_target_dir = os.path.normpath(os.path.join(base_path, target_path))
    if not os.path.abspath(full_target_dir).startswith(os.path.abspath(base_path)):
        raise Exception("Target directory is outside the base path")
      
    # Check if the given path is a directory or a file
    if os.path.isfile(target_path):
        # If it's a file and a ZIP file, handle it
        if target_path.endswith(".zip"):
            zip_extractor(base_path,target_path, delete_zip=True)
            matching_files_in_zipped = list_files(base_path,target_path=target_path[:-4], extensions=extensions)
            matching_files += matching_files_in_zipped
        elif any(target_path.endswith(ext) for ext in extensions):
            matching_files.append(os.path.relpath(target_path, os.path.dirname(target_path)))
    else:
        # If it's a directory, walk through each directory starting  
        full_target_dir = os.path.normpath(os.path.join(base_path, target_path))
        if not os.path.abspath(full_target_dir).startswith(os.path.abspath(base_path)):
            raise Exception("Target directory is outside the base path")
        
        for root, dirs, files in os.walk(target_path):
            # Check each file in the current directory
            for file in files:
                # if file is zip file, extract it
                if file.endswith(".zip"):
                    # full path of zip file
                    zip_full_path = os.path.join(root, file)
                    # extract and delete zip file
                    zip_extractor(base_path,zip_full_path, delete_zip=True)
                    matching_files_in_zipped = list_files(base_path,target_path=zip_full_path[:-4], extensions=extensions)
                    matching_files += matching_files_in_zipped
                elif any(file.endswith(ext) for ext in extensions):    
                    #matching_files.append(os.path.relpath(os.path.join(root, file), path))
                    matching_files.append(os.path.join(root,file))
                    
                    
    return matching_files


def remove_directories_with_hidden_files(base_path,root_path):
    """Recursively remove directories containing only files starting with a dot."""
    
    full_target_dir = os.path.normpath(os.path.join(base_path, root_path))
    if not os.path.abspath(full_target_dir).startswith(os.path.abspath(base_path)):
        raise Exception("Target directory is outside the base path")
    
    for root, dirs, files in os.walk(root_path, topdown=False):
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            dir_files = os.listdir(dir_path)

            # Check if all files in the directory start with a dot
            if all(file.startswith('.') for file in dir_files):
                shutil.rmtree(dir_path)
                #logger.info("{} : Directory {} removed successfully.".format(logger_name, dir_path))
            else:
                # Check and delete only files starting with a dot
                dot_files = [file for file in dir_files if file.startswith('.')]
                for dot_file in dot_files:
                    dot_file_path = os.path.join(dir_path, dot_file)
                    os.remove(dot_file_path)
                    #logger.info("{} : File {} removed successfully.".format(logger_name, dot_file_path))


def zip_extractor(base_path,file, extract_path=None, delete_zip=False):
    """ Extract the zip
        Args:
            extract_path: String where the output artifact is saved
            delete_zip : whether to delete the original zip file or not
            file : directory of the folder
        Returns:
            None
    """
    if extract_path is None:
        extract_path = os.path.splitext(file)[0]

    #logger.info("{} : Extracting : {}".format(logger_name, file))
    try:
        with ZipFile(file, 'r') as zf:
            # Filter out unwanted files and folders
            file_list = [f.filename for f in zf.infolist() if not f.filename.startswith('.')]
            # Extract the remaining files
            zf.extractall(extract_path, members=file_list)
        #logger.info("{} - {} Extracted successfully".format(logger_name, file))
        if delete_zip:  
            full_target_dir = os.path.normpath(os.path.join(base_path, file))
            if not os.path.abspath(full_target_dir).startswith(os.path.abspath(base_path)):
                raise Exception("Target directory is outside the base path") 
            os.remove(file)
           # logger.info("{} : {} removed successfully.".format(logger_name, file))
        # to remove hidden files e.g. when you zip from macbook, they will create all files starting with . file extension
        remove_directories_with_hidden_files(base_path,extract_path)
    except (BadZipFile, Exception) as e:
        print(f"Error extracting {file}: {e}")
        #logger.error("{} : Error extracting {}: {}".format(logger_name, file, e))
    









