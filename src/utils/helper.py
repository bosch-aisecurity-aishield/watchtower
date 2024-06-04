__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

import os
import shutil
from utils import github_util, aws_s3_util, zip_util


def fetch_scanning_files(repo_type: str, scanning_id: str, repo_url: str = None, github_clone_dir: str = None,
                         aws_access_key_id: str = None, aws_secret_access_key: str = None, region: str = None,
                         bucket_name: str = None, s3_download_dir: str = None,path: str = None, branch_name: str = 'main',depth: int=1,base_path: str=None):
    """
        Fetches files to be scanned based on the repository type and scanning ID.

        Parameters:
        - repo_type (str): The type of repository ('github' or 's3').
        - scanning_id (str): The unique identifier for the scanning process.
        - repo_url (str, optional): The URL of the GitHub repository (only required for 'github' repo_type).
        - github_clone_dir (str, optional): The local directory for cloning GitHub repository (only for 'github').
        - aws_access_key_id (str, optional): AWS Access Key ID (only required for 's3' repo_type).
        - aws_secret_access_key (str, optional): AWS Secret Access Key (only required for 's3' repo_type).
        - region (str, optional): AWS region (only required for 's3' repo_type).
        - bucket_name (str, optional): AWS S3 bucket name (only required for 's3' repo_type).
        - s3_download_dir (str, optional): Local directory for saving files from S3 (only for 's3').
        - path (str,optional): Path of the file/folder (only required for 'file' or 'folder' repo_type) 
        - branch_name (str,optional): Name of branch of repository (only required to inspect a specific branch of repository other than master/main branch)
        Returns:
        - to_be_scanned_files (List[str]): A list of file paths to be scanned.
        - save_dir (str): The directory where the fetched files are saved.

        This function fetches files to be scanned based on the repository type and scanning ID. For 'github'
        repositories, it clones the GitHub repository, searches for specific file
        types (.h5, .pb, .pkl, .ipynb, requirements.txt),and returns their paths. For 's3' repositories,
        it downloads specific file types from an AWS S3 bucket and returns their paths.


        Note:
        - When using 'gitHub' or 'huggingface' repo_type, ensure the 'github_clone_dir' is provided as the local directory for cloning.
        - When using 's3' repo_type, ensure AWS credentials ('aws_access_key_id', 'aws_secret_access_key') are provided.
        - When using 'file' repo_type, ensure file path is provided.
        """

    to_be_scanned_files = list()
    save_dir = None
    extensions = [".h5", ".pkl", ".pb", ".ipynb","requirements.txt"]
    if (repo_type.lower() == 'github' and (depth >=1 )) or repo_type.lower() == 'huggingface':
        github_clone_dir = github_clone_dir + '_{}'.format(scanning_id)

        save_dir = github_clone_dir
        
        if repo_type.lower() == 'github':
            repo_url = repo_url
        elif repo_type.lower() == 'huggingface':
            HUGGINGFACE_DOMAIN = r"https://huggingface.co/"
            if not repo_url.startswith(HUGGINGFACE_DOMAIN):
                repo_url = HUGGINGFACE_DOMAIN + repo_url
            else:
                url_path = repo_url[len(HUGGINGFACE_DOMAIN):].split("/")
                # Ensure only user name and repository name are included
                if len(url_path) > 2:
                    repo_url = HUGGINGFACE_DOMAIN + "/".join(url_path[:2])

        github_util.clone_github_repo(repo_url, save_dir,branch_name,depth)
    
        # get all h5 files
        # h5_files = search_files(base_path,github_clone_dir, '.h5')
        # # get all .pb files
        # pb_files = search_files(base_path,github_clone_dir, '.pb')
        # # get all .pkl files
        # pkl_files = search_files(base_path,github_clone_dir, '.pkl')
        # # get all ipynb files
        # ipynb_files = search_files(base_path,github_clone_dir, '.ipynb')
        # #get requirements files
        ##requirement_files = search_files(base_path,github_clone_dir, 'requirements.txt')
        #get files from zip files
        
        all_files = search_files(base_path,github_clone_dir, extensions)
        
        #to_be_scanned_files = h5_files + ipynb_files + pb_files + pkl_files
       
        to_be_scanned_files = all_files
        
        

    if repo_type.lower() == 's3':

        s3_download_dir = s3_download_dir + '_{}'.format(scanning_id)

        save_dir = s3_download_dir

        # Ensure local directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # create s3 object to interact with s3 buckets
        s3_object = aws_s3_util.AIShieldWatchtowerS3(aws_access_key_id, aws_secret_access_key,
                                                     region, bucket_name, save_dir)

        # Specify the list of file_extensions
        file_extensions = [".h5", ".pkl", ".ipynb"]

        # Fetch the files specified in the file extensions from S3 saved locally
        to_be_scanned_files = s3_object.download_files(file_extensions)
        
    if repo_type.lower() == 'file':
        if path:
            if path.endswith((".h5", ".pkl", ".pb", ".ipynb","requirements.txt")):
                to_be_scanned_files.append(path)
            elif path.endswith(".zip"):
                to_be_scanned_files = zip_util.list_files(path,extensions)

    if repo_type.lower() == 'folder':
        tar_dir = path  # Assuming file_path is the path to the folder
        folder_base_path = os.path.dirname(tar_dir)
        
        all_files = search_files(folder_base_path,tar_dir, extensions)
        # h5_files = search_files(folder_base_path,tar_dir, '.h5')
        # pb_files = search_files(folder_base_path,tar_dir, '.pb')
        # pkl_files = search_files(folder_base_path,tar_dir, '.pkl')
        # ipynb_files = search_files(folder_base_path,tar_dir, '.ipynb')
        # requirement_files = search_files(folder_base_path,tar_dir, 'requirements.txt')

        # to_be_scanned_files = h5_files + ipynb_files + pb_files + pkl_files +requirement_files
        to_be_scanned_files  = all_files

    return to_be_scanned_files, save_dir


def search_files(base_path:str, target_dir: str, file_extensions):
    """
    Finds all the files ending with a given extension in the specified directory and its sub-folders.

    Parameters:
    - target_dir (str): Directory to begin the search.
    - file_extension (str): File extension to search for (e.g. '.h5', '.ipynb').

    Returns:
    - List of paths to files with the specified extension.
    """
    if not target_dir:
        raise Exception("Target directory is empty")

    # Normalize the target directory and check if it is within the base_path
    full_target_dir = os.path.normpath(os.path.join(base_path, target_dir))
    if not os.path.abspath(full_target_dir).startswith(os.path.abspath(base_path)):
        raise Exception("Target directory is outside the base path")
    # List to hold the paths of all files matching the given extension
    matching_files = []
    # for root, dirs, files in os.walk(target_dir):
    #     # Check each file in the current directory
    #     for file in files:
    #         # If the file ends with the specified extension, add its full path to our list
    #         if file.endswith(file_extensions):
    #             matching_files.append(os.path.join(root, file))
    matching_files=zip_util.list_files(target_dir, file_extensions)
    
    return matching_files



def make_directory(path):
    """
    create directory

    Parameters
    ----------
    path : full path of directory

    Returns
    -------
    None.

    """
    if os.path.isdir(path):
        print("{} already exist".format(path))

    if not os.path.isdir(path):
        os.mkdir(path=path)
        print("{} created successfully".format(path))


def delete_directory(base_path :str,directory):
    """
    delete directory

    Parameters
    ----------
    directory : list containing the directory to delete along with all the files

    Returns
    -------
    None.

    """
    
    for d in directory:

        full_path = os.path.normpath(os.path.join(base_path, d))
        if not os.path.abspath(full_path).startswith(os.path.abspath(base_path)):
            print("Path '{}' is outside the base folder '{}' and cannot be deleted.".format(full_path, base_path))
            return

        try:
            if os.path.isdir(d):
                try:
                    shutil.rmtree(path=d)
                    print("{} Removed Successfully".format(d))
                except OSError:
                    os.remove(path=d)
                    print("{} Removed Successfully".format(d))
            else:
                os.remove(d)
                print("{} Removed Successfully".format(d))

        except Exception as e:
            print("{} Failed to remove due to {}".format(d, str(e)))


def check_file_at_given_dir(path: str, file_name: str = 'requirements.txt'):
    """
    Check file existence at given path

    Parameters
    ----------
    path : str, path to look for the file
        DESCRIPTION.
    file_name : str, full file name with extension
        DESCRIPTION. The default is 'requirements.txt'.

    Returns
    -------
    file_path : TYPE
        DESCRIPTION.

    """
    file_path = None
    if file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
    return file_path

