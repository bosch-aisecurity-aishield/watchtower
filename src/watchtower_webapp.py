__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
# Importing necessary modules
import datetime
from modules import workflow
from flask import Flask, render_template, request, flash

# Importing necessary modules
app = Flask(__name__)
app.secret_key = 'watchtower'


# Define a function to simulate processing and scanning
def trigger_workflow(repo_type, repo_url, s3_bucket_name, aws_secret_access_key, aws_access_key_id, region,
                     branch_name, depth, path):
    """
    Description: This function simulates the processing and scanning of a repository based on the provided parameters.

    Input Parameters:
        - repo_type (str): The type of the repository to be scanned (e.g., "github" or "s3").
        - repo_url (str): The URL of the repository (for "GitHub" repo_type) or the S3 bucket name (for "s3" repo_type).
        - s3_bucket_name (str): The S3 bucket name if the repo_type is "s3" (otherwise, set to None).
        - aws_access_key_id (str): aws access key id value in str
        - aws_secret_access_key (str): aws secret access key value in str
        - region (str): region where the bucket is present
        - branch_name (str): The branch_name of the GitHub repository to analyze. Defaults is "main" branch.
        - depth (int): Upto which commit want to clone github
        - path (str): The path of the file/folder to analyze.

    Returns:
        - report_path (str) : The path to the scanning report generated during the scanning process.
        - scanning_status (bool): The status of the scanning process, where True indicates success,
        and False indicates failure.

    """
    print('Triggering Orchestrator for Scanning Repo Type {}'.format(repo_type))

    # Generate a unique scanning ID based on the current timestamp
    scanning_id = str(int(datetime.datetime.now().timestamp()))
    
    # Call the watchtower.orchestrator function to perform the scanning
    report_path, scanning_status = workflow.orchestrator(repo_type=repo_type,
                                                         repo_url=repo_url,
                                                         bucket_name=s3_bucket_name,
                                                         aws_access_key_id=aws_access_key_id,
                                                         aws_secret_access_key=aws_secret_access_key,
                                                         region=region,
                                                         path=path,
                                                         branch_name=branch_name,
                                                         depth=depth,
                                                         scanning_id=scanning_id)
    return report_path, scanning_status


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
# Define a route for the root URL '/info'
@app.route('/info')
def info():
    return 'Welcome to Watchtower Powered by AIShield \n'


# Define a route for '/watchtower-aishield' that handles both GET and POST requests
@app.route('/watchtower-aishield', methods=['GET', 'POST'])
def index():
    """
    Description: This function handles both GET and POST requests for the '/watchtower-aishield' route. It processes the
    form data submitted by the user for repository scanning.

        POST Request Handling:
        - If the request method is POST, the function:
            - Determines the repository type based on user input (either "github" or "s3").
            - Retrieves the repository URL (for "GitHub" repo_type) or S3 bucket name (for "s3" repo_type)
            from the form data.
            - Validates the form inputs, checking for missing or incorrect values.
            - If there are errors, it displays error messages using the flash() function.
            - If there are no errors, it calls the simulate_processing function to initiate the scanning process.
            - If scanning is successful and a report is generated, it displays a success message.
            - If scanning fails, it displays a failure message.

        GET Request Handling:
        - If the request method is GET, the function renders the 'form.html' template.

        Returns:
        - If the request method is POST and processing is successful, the function may
        display success or failure messages via flash() and render the 'form.html' template.

    """
    if request.method == 'POST':
        repo_type = None

        # Determine the repository type based on user input
        if request.form.get('type') is not None:
            repo_type = request.form.get('type')
            
        # Get the repository URL and S3 bucket name from the form data
        repo_url = request.form.get('github_url')
        s3_bucket_name = request.form.get('s3_bucket_name')
        aws_access_key_id = request.form.get('aws_access_key_id')
        aws_secret_access_key = request.form.get('aws_secret_access_key')
        region = request.form.get('region')
        branch_name = request.form.get('branch')
        depth = request.form.get('depth')
        path = request.form.get('path')
        
        if (depth is None) or (not depth):
            depth=1
        
        if (branch_name is None) or (not branch_name):
            branch_name=None

        errors = []
        # Validate the form inputs
        if not repo_type:
            errors.append("Please select a repo_type.")

        if repo_type.lower() == "github" or repo_type.lower() == "huggingface":
            if not repo_url:
                errors.append("Repo URL is required.")

        elif repo_type.lower() == "s3":
            if not s3_bucket_name:
                errors.append("S3 BUCKET NAME is required.")
            if not aws_access_key_id:
                errors.append("AWS ACCESS KEY ID is required.")
            if not aws_secret_access_key:
                errors.append("AWS SECRET ACCESS KEY is required.")
            if not region:
                errors.append("REGION is required.")

        elif repo_type.lower() == "local":
            repo_type = request.form.get('file_type')
            if not path:
                errors.append("Path is required.")
                

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Call the simulate_processing function to start the scanning process
            report_path, scanning_status = trigger_workflow(repo_type, repo_url,
                                                            s3_bucket_name, aws_secret_access_key, aws_access_key_id,
                                                            region, branch_name, int(depth), path)
            if (report_path is not None) and scanning_status:
                flash("Job Submitted successfully! The report can be found at {}.".format(report_path), 'Success')
            else:
                flash("Job Failed", 'Failed')

    return render_template('form.html')


# Main driver function
if __name__ == '__main__':
    # Run the Flask application on host '0.0.0.0' and port 5015
    app.run(host='0.0.0.0', port=5015)
