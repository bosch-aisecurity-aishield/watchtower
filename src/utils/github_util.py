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


def clone_github_repo(repo_url, target_dir):
    """
    Clone a GitHub repository.

    Parameters:
    - repo_url (str): The URL of the GitHub repository.
    - target_dir (str): The directory to clone the repository into.

    Returns:
    - None
    """
    try:
        if not os.path.exists(target_dir):
            git.Repo.clone_from(repo_url, target_dir)
        else:
            print("Directory already exists. Assuming the repository is already cloned.")
    except Exception as e:
        print("Error cloning git repo {}".format(str(e)))


def delete_github_repo(repo_path):
    
    """
    Delete a GitHub cloned repository.

    Parameters:
    - repo_path (str): Path of the cloned repo
    
    Returns:
    - None
    """
    try:
        for root, dirs, files in os.walk(repo_path):  
            for dir in dirs:
                os.chmod(path.join(root, dir), stat.S_IRWXU)
            for file in files:
                os.chmod(path.join(root, file), stat.S_IRWXU)
        shutil.rmtree(repo_path)
        print("Locally cloned repository has been successfully removed")
    
    except Exception as e:
        print("{} Failed to remove due to {}".format(repo_path, str(e)))
    