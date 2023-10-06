__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

# importing necessary libraries
import datetime
import argparse
from modules import workflow

# Create an argument parser to handle command-line arguments
parser = argparse.ArgumentParser(
    description="AIShield.Watchtower: Automatically identify and analyze models and notebooks in a github repository "
                "or S3 bucket.")
parser.add_argument('--repo_type', type=str, help='Repo type github or s3')
parser.add_argument('--repo_url', type=str, help='The URL of the GitHub repository to analyze.')
parser.add_argument('--target_dir', type=str, default='repo_dir',
                    help='The directory to clone the repository into. Defaults to "repo_dir".')
parser.add_argument('--aws_access_key_id', type=str,
                    help='The name of the the aws secret access id S3 bucket to analyze.', default='None')
parser.add_argument('--aws_secret_access_key', type=str,
                    help='The name of the aws secret access key  bucket to analyze.', default='None')
parser.add_argument('--region', type=str, help='The S3 bucket region to analyze.', default='None')
parser.add_argument('--bucket_name', type=str, help='The name of the S3 bucket to analyze.')
parser.add_argument('--s3_downloads', type=str, default='s3_downloads',
                    help='The directory to download the model files from s3 bucket. Defaults to "s3_downloads".')

# Parse the command-line arguments
args = parser.parse_args()

# Check the repository type specified by the user
if args.repo_type.lower() == "github":

    # Generate a unique scanning ID based on the current timestamp
    scanning_id = str(int(datetime.datetime.now().timestamp()))

    # Call the watchtower.orchestrator function for GitHub repository analysis
    report_path, scanning_status = workflow.orchestrator(repo_type=args.repo_type,
                                                         repo_url=args.repo_url,
                                                         github_clone_dir=args.target_dir,
                                                         scanning_id=scanning_id)
    # Check if scanning was successful and print the report path
    if (report_path is not None) and scanning_status:
        print("Scanned report will be saved under : {}".format(report_path))
elif args.repo_type.lower() == "s3":
    # Generate a unique scanning ID based on the current timestamp
    scanning_id = str(int(datetime.datetime.now().timestamp()))
    # Call the watchtower.orchestrator function for S3 bucket analysis
    report_path, scanning_status = workflow.orchestrator(repo_type=args.repo_type,
                                                         aws_access_key_id=args.aws_access_key_id,
                                                         aws_secret_access_key=args.aws_secret_access_key,
                                                         region=args.region, bucket_name=args.bucket_name,
                                                         s3_download_dir=args.s3_downloads,
                                                         scanning_id=scanning_id)
    # Check if scanning was successful and print the report path
    if (report_path is not None) and scanning_status:
        print("Scanned report will be saved under : {}".format(report_path))
else:
    raise ValueError("Please specify repo type either a github or an s3.")
