__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

import os
import git  # !pip install GitPython
import stat
import shutil
from os import path

"""try:
  import git
except:
  !pip install GitPython
  import git
"""


def clone_github_repo(repo_url, target_dir, branch_name, depth):
    """
    Clone a GitHub repository.

    Parameters:
    - repo_url (str): The URL of the GitHub repository.
    - target_dir (str): The directory to clone the repository into.
    - branch_name (str): The name of the branch of Github repository.
    - depth (int): Upto which commit want to clone the repository

    Returns:
    - None
    """
    try:
        if not os.path.exists(target_dir):
            git.Repo.clone_from(repo_url, target_dir,branch=branch_name,depth=depth)
        else:
            print("Directory already exists. Assuming the repository is already cloned.")
    except Exception as e:
        print("Error cloning git repo {}".format(str(e)))


def delete_github_repo(repo_dir):
    
    """
    Delete a GitHub cloned repository.

    Parameters:
    - repo_path (str): Path of the cloned repo
    
    Returns:
    - None
    """
    try:
        # if not repo_dir:
        #     if not os.path.exists(repo_dir):
        #         print("Invalid repo directory or directory does not exist. No need to remove.")
        #         return

        # Make sure repo_dir is an absolute path
        repo_dir = os.path.abspath(repo_dir)

        # Ensure that repo_dir is within an expected directory
        expected_root = os.path.abspath(os.getcwd())
        if not repo_dir.startswith(expected_root):
            print("Invalid repo directory. No need to remove.")
            return

        # Change permissions of files and directories recursively
        # for root, dirs, files in os.walk(repo_dir):
        #     for dir in dirs:
        #         os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        #     for file in files:
        #         os.chmod(os.path.join(root, file), stat.S_IRWXU)

        shutil.rmtree(repo_dir, ignore_errors=True)
        os.rmdir(repo_dir)
        print("Locally cloned repository has been successfully removed")
          
    except Exception as e:
        print("{} Failed to remove due to {}, it is recommended to delete the directory manually".format(repo_dir, str(e)))
