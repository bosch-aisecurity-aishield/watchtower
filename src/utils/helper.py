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
from utils import github_util, aws_s3_util


def fetch_scanning_files(repo_type: str, scanning_id: str, repo_url: str = None, github_clone_dir: str = None,
                         aws_access_key_id: str = None, aws_secret_access_key: str = None, region: str = None,
                         bucket_name: str = None, s3_download_dir: str = None):
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

        Returns:
        - to_be_scanned_files (List[str]): A list of file paths to be scanned.
        - save_dir (str): The directory where the fetched files are saved.

        This function fetches files to be scanned based on the repository type and scanning ID. For 'github'
        repositories, it clones the GitHub repository, searches for specific file
        types (.h5, .pb, .pkl, .ipynb, requirements.txt),and returns their paths. For 's3' repositories,
        it downloads specific file types from an AWS S3 bucket and returns their paths.


        Note:
        - When using 'gitHub' repo_type, ensure the 'github_clone_dir' is provided as the local directory for cloning.
        - When using 's3' repo_type, ensure AWS credentials ('aws_access_key_id', 'aws_secret_access_key') are provided.
        """

    to_be_scanned_files = list()
    save_dir = None
    if repo_type.lower() == 'github':

        github_clone_dir = github_clone_dir + '_{}'.format(scanning_id)

        save_dir = github_clone_dir
        # Clone the gitHub repository in the local
        github_util.clone_github_repo(repo_url, save_dir)

        # get all h5 files
        h5_files = search_files(github_clone_dir, '.h5')

        # get all .pb files
        pb_files = search_files(github_clone_dir, '.pb')

        # get all .pkl files
        pkl_files = search_files(github_clone_dir, '.pkl')

        # get all ipynb files
        ipynb_files = search_files(github_clone_dir, '.ipynb')

        # get requirements files
        requirement_files = search_files(github_clone_dir, 'requirements.txt')

        to_be_scanned_files = h5_files + ipynb_files + pb_files + pkl_files + requirement_files

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

    return to_be_scanned_files, save_dir


def search_files(target_dir: str, file_extensions: str):
    """
    Finds all the files ending with a given extension in the specified directory and its sub-folders.

    Parameters:
    - target_dir (str): Directory to begin the search.
    - file_extension (str): File extension to search for (e.g. '.h5', '.ipynb').

    Returns:
    - List of paths to files with the specified extension.
    """

    # List to hold the paths of all files matching the given extension
    matching_files = []

    # Walk through each directory starting from the target_dir
    for root, dirs, files in os.walk(target_dir):
        # Check each file in the current directory
        for file in files:
            # If the file ends with the specified extension, add its full path to our list
            if file.endswith(file_extensions):
                matching_files.append(os.path.join(root, file))

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


def delete_directory(directory):
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

