__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

from tqdm import tqdm
from utils import helper, github_util, report_util
import os
from modules import notebook_inspector, model_inspector


def orchestrator(repo_type: str = 'github', repo_url: str = None, github_clone_dir: str = "repo_dir",
                 aws_access_key_id: str = None, aws_secret_access_key: str = None, region: str = None,
                 bucket_name: str = None, s3_download_dir: str = 's3_downloads', scanning_id: str = None,
                 path: str=None, branch_name: str='main', depth: int=1, pass_scan_tf_models:  bool = False):
    """
    This Function will work as an orchestrator to clone the given repo provided and fetch what are the files to be
    scanned by watchtower powered by AIShield , and trigger model inspector or notebook inspector according to the
    file extension . and once scanning will be done , it will trigger to save the detailed report , consolidated
    report / summary of the scanning of the file , and watchtower provided vulnerability severity mapped detailed
    report , clean up local downloaded directories after scanning and report generation being done.


    Parameters
    ----------
    repo_type : str, optional
        DESCRIPTION. The default is 'gitHub'.
    repo_url : str, optional
        DESCRIPTION. The default is None.
    github_clone_dir : str, optional
        DESCRIPTION. The default is "repo_dir".
    aws_access_key_id: str, optional
        DESCRIPTION. The default is None.
    aws_secret_access_key: str, optional
        DESCRIPTION. The default is None.
    region: str, optional
        DESCRIPTION. The default is None.
    bucket_name: str, optional
        DESCRIPTION. The default is None.
    s3_download_dir: str, optional
        DESCRIPTION. The default is "s3_downloads".
    scanning_id: str
        DESCRIPTION. scanning id
    path: str, optional
        DESCRIPTION. The default is None.
    branch_name: str, optional
        DESCRIPTION. The default is "main"
    depth: int, optional
        DESCRIPTION. The default value is 1.


    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    report_path : str
        DESCRIPTION. the aggregator / summary of the report path
    scanning_status : boolean
        DESCRIPTION. The default is True, if scanning failed due
                    to any reason else status will be False

    """
    save_dir = None
    report_path = None
    scanning_status = True
    failed_scan_files = list()
    scanned_report_dictionary = {}
    base_path = str(os.getcwd())

    try:
        print("Scanning Started ...")
        to_be_scanned_files, save_dir = helper.fetch_scanning_files(repo_type=repo_type, repo_url=repo_url,
                                                                    github_clone_dir=github_clone_dir,
                                                                    aws_access_key_id=aws_access_key_id,
                                                                    aws_secret_access_key=aws_secret_access_key,
                                                                    s3_download_dir=s3_download_dir,
                                                                    region=region,
                                                                    bucket_name=bucket_name,
                                                                    scanning_id=scanning_id,
                                                                    path=path,
                                                                    branch_name=branch_name,
                                                                    depth=depth,
                                                                    base_path = base_path)
        #print("notebook scanning", to_be_scanned_files)

        # iterate to get response from each files
        for file in tqdm(to_be_scanned_files):

            print("\nScanning - {}.".format(file))

            """TODO : Right now only supported .pkl / .h5 / .pb format model scanning, 
            further release onnx, pt extension model scanning feature will be coming """

            
            if file.endswith('.h5') or file.endswith(".keras") or file.endswith('.pb'):
                if (pass_scan_tf_models):
                    dictionary, status = model_inspector.scan(model_path_input=file)
                else:
                    tool_dict = {"tool": "unsafe-check-h5-keras-pb", 
                                 "output_log": "Scanning for this file format is not enabled: Enable using the argument 'scan_tf_models'"}
                    dictionary, status = tool_dict, True
        
            elif file.endswith(".pkl") or file.endswith('.safetensors') or file.endswith('.pt') or file.endswith('.pth') or file.endswith('.bin'):
                dictionary, status = model_inspector.scan(model_path_input=file)

            elif file.endswith('.py') or file.endswith('.ipynb'):
                dictionary, status = notebook_inspector.scan(file_name=file, requirement_file="")

            elif file.endswith('requirements.txt'):
                dictionary, status = notebook_inspector.scan(file_name="", requirement_file=file)

            if not status:
                failed_scan_files.append(file)
                print("Scanning failed. Continuing scanning for the next file")

            else:
                scanned_report_dictionary['{}'.format(file)] = dictionary
                print("Scanning completed. Continuing scanning for the next file")

        # Saving the Detailed scanned report
        detailed_result_json, _ = report_util.save_report(result_dict=scanned_report_dictionary,
                                                          file_name="detailed_reports_{}".format(scanning_id),
                                                          scanning_id=scanning_id)

        consolidated_aggregator_result, vul_sev_detail_result = report_util.create_aggregator_report(
            result_dict=detailed_result_json, scanned_files=to_be_scanned_files,
            failed_scan_files=failed_scan_files,
            repo_type=repo_type, repo_url=repo_url,
            bucket_name=bucket_name,
            agg_scan_tf_models=pass_scan_tf_models)

        # pretty printed json format
        # Saving the summary of the scanned report
        consolidated_aggregator_result_json, report_path = report_util.save_report(
            result_dict=consolidated_aggregator_result, file_name="summary_reports_{}".format(scanning_id),
            scanning_id=scanning_id)

        # Saving the Detailed scanned report
        _, _ = report_util.save_report(result_dict=vul_sev_detail_result,
                                       file_name="severity_mapped_detailed_reports_{}".format(scanning_id),
                                       scanning_id=scanning_id)

        print(consolidated_aggregator_result_json)
        print("Scanning Completed")
    except Exception as e:
        scanning_status = False
        print("Scanning Failed due to {}".format(str(e)))
        
    if save_dir != None:
        # Clean up the local cloned directory either scanning failed or Completed
        if repo_type.lower() == "github":
            github_util.delete_github_repo(repo_dir=save_dir)
        elif repo_type.lower() not in ["file", "folder"]:
            helper.delete_directory(base_path,[save_dir])

    return report_path, scanning_status


