__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

import os
import json
from utils import helper


def save_report(result_dict: dict, file_name: str, scanning_id: str, path: str = "scanned_reports",
                save_file_extension: str = "json"):
    """
        Save a report as a JSON file.

        Args:
            result_dict (dict): The dictionary containing the report data to be saved.
            file_name (str): The name of the output JSON file (excluding the extension).
            scanning_id (str): A unique identifier for the scanning process.
            path (str, optional): The directory path where the report should be saved (default is "scanned_reports").
            save_file_extension (str, optional): The file extension for the saved report (default is "json").

        Returns:
            tuple: A tuple containing two elements:
                - result_json (str): The JSON representation of the result_dict.
                - save_path (str): The full path to the saved JSON file.
    """

    # create directory to store reports for scanned file
    helper.make_directory(path=path)

    sub_dir = os.path.join(path, scanning_id)
    # create directory to store reports for scanned file
    helper.make_directory(path=sub_dir)

    # Serializing json
    result_json = json.dumps(result_dict, indent=7)

    save_path = "{}.{}".format(os.path.join(sub_dir, file_name), save_file_extension)
    # Writing to json file
    with open(save_path, "w") as outfile:
        outfile.write(result_json)

    return result_json, save_path


def create_aggregator_report(result_dict: dict, scanned_files: list,
                             failed_scan_files: list,
                             repo_type: str,
                             repo_url: str = None,
                             bucket_name: str = None,
                             agg_scan_tf_models: bool = False):
    """
        This function will summarize and consolidated the detailed scanned result a quick overview format
        like how many model and notebook files were found for scanning and how-many file scanned by
        watchtower by aishield and calculates how many Critical , High , Medium and Low vulnerabilities
        found from the Model Inspector scanning result and Notebook Inspector scanning result, and return the
        overall summary report as json format.

        Args:
            result_dict (dict): The dictionary containing the report data to analysed for summarization.
            scanned_files (list): list of files found for scanning
            failed_scan_files (list): list of file failed to scan
            repo_type (str): repository type either GitHub or s3
            repo_url (str, optional): if repository type is GitHub, pass the repository url for scanning started.
            bucket_name (str, optional): if repository type is s3, pass the s3 bucket name for scanning started..

        Returns:
            tuple: A tuple containing two elements:
                - result_json (str): The JSON representation of the result_dict.
                - save_path (str): The full path to the saved JSON file.
    """

    aggregator_result_dict = dict()  # Initialize an empty dictionary for aggregator scanning results
    detailed_result_dict = dict()  # Initialize an empty dictionary for detailed scanning results
    try:
        aggregator_result_dict['Repository Type'] = repo_type
        if repo_type.lower() == "github" or repo_type.lower() == "huggingface":
            aggregator_result_dict["Repository URL"] = repo_url

        elif repo_type.lower() == "s3":
            aggregator_result_dict["Bucket Name"] = bucket_name
        count = 0
        for file in scanned_files:
            if file.endswith(".h5"):
                count = count + 1

        number_of_model_files = sum(
            1 for file in scanned_files if file.endswith(".h5") or file.endswith(".pb") or file.endswith(".keras")
            or file.endswith(".pkl") or file.endswith(".pt") or file.endswith(".pth") or file.endswith(
                ".safetensors") or file.endswith(".bin"))

        number_of_notebooks = sum(1 for file in scanned_files if file.endswith(".ipynb") or file.endswith('.py'))
        number_of_requirement_file = sum(1 for file in scanned_files if file.endswith("requirements.txt"))

        aggregator_result_dict["Total Number of Model Found"] = number_of_model_files
        aggregator_result_dict[
            "Total Number of Notebooks & Requirement files Found"] = number_of_notebooks + number_of_requirement_file

        number_of_model_files_failed = sum(
            1 for file in failed_scan_files if file.endswith(".h5") or file.endswith(".pb") or file.endswith(".keras")
            or file.endswith(".pkl") or file.endswith(".pt") or file.endswith(".pth") or file.endswith(
                ".safetensors") or file.endswith(".bin"))

        number_of_notebooks_failed = sum(
            1 for file in failed_scan_files if file.endswith(".ipynb") or file.endswith(".py"))
        number_of_requirement_file_failed = sum(1 for file in failed_scan_files if file.endswith(".requirements.txt"))

        # when the flag is NOT set, (.h5,.pb and .keras) models are NOT scanned
        if not agg_scan_tf_models:
            number_of_unscanned_tf_files = sum(
                1 for file in scanned_files if file.endswith(".h5") or file.endswith(".pb") or file.endswith(".keras"))

            # calculate number of model scanned
        if agg_scan_tf_models:
            aggregator_result_dict[
                "Total Number of Model Scanned"] = number_of_model_files - number_of_model_files_failed
        else:
            aggregator_result_dict[
                "Total Number of Model Scanned"] = number_of_model_files - number_of_model_files_failed - number_of_unscanned_tf_files
        # calculate number of notebooks failed to scan
        aggregator_result_dict["Total Number of Notebooks & Requirement files Scanned"] = (
                                                                                                  number_of_notebooks + number_of_requirement_file) - (
                                                                                                  number_of_notebooks_failed + number_of_requirement_file_failed)
        # calling the parser to parse the detailed scanned result
        # to calculate the Number of Model and notebook Vulnerability vs severity Map
        aggregator_result_dict["Total Notebook & Requirement files Vulnerabilities Found"], aggregator_result_dict[
            "Total Model Vulnerabilities Found"], detailed_result_dict = result_parser(result_dict)

    except Exception as e:
        # Handle other exceptions
        print("Failed Create Summary of the Report due to {}".format(str(e)))

    return aggregator_result_dict, detailed_result_dict


def model_inspector_result_parser(output: list):
    """
            Description: This function will take the output log generated by model safety check tool(unsafe-check-h5
                         or unsafe-check-pb or unsafe-check-pkl) and
                         identifies how many vulnerabilities found and its severity and return
                         the number of vulnerabilities found according to the severity type.

            input_parameter :
                    output : list, Mandatory
                            DESCRIPTION. output logs in list format.
            Returns
            -------
                vulnerability_severity_map : dict
                          DESCRIPTION. dictionary map of High vulnerabilities found and its severity .

    """
    vulnerability_severity_map = dict()  # Initialize an empty dictionary for vulnerability vs severity map
    try:
        # If output is not empty, attempt to parse
        if len(output['output_log']) != 0:
            if output['tool'] == 'picklescan':
                for pickle_vul in output['output_log']:
                    severity = pickle_vul['severity']
                    if severity in vulnerability_severity_map:
                        vulnerability_severity_map[severity] = int(vulnerability_severity_map[severity]) + 1
                    else:
                        vulnerability_severity_map[severity] = 1
            else:
                for out in output['output_log']:
                    # get the severity from the output
                    severity = out.split("-")[0].split(":")[1].replace(" ", "")
                    if (len(severity) > 0):
                        if severity in vulnerability_severity_map:
                            vulnerability_severity_map[severity] = int(vulnerability_severity_map[severity]) + 1
                        else:
                            vulnerability_severity_map[severity] = 1

    except Exception as e:
        print("Failed to parse model inspector tool output {}".format(e))

    return vulnerability_severity_map


def result_parser(result_dict: str):
    """
            This function will calculate the Number of Vulnerabilities found vs its severity respective to
            the Model Inspector Scanning result and Notebook Inspector result Scanning, and return two dictionary
            containing the both information.

            It will check if it is a Model Inspector output or notebook Inspector output , once it identifies
            its respective parser to get the severity information, as used different tools so for different tool
            the output will be different , so according to that respective parser function will take place in to
            consideration.

            Args:
                result_dict (str): The string format dictionary containing the report
                                    data to analysed for summarization.

            Returns:
                tuple: A tuple containing two elements:
                    - notebook_vul_sev_result (dict): returns the severity vs number of vulnerabilities map for notebook
                                                      inspector result.
                    - model_vul_sev_result (dict): returns the severity vs number of vulnerabilities  map for model
                                                      inspector result.
        """

    # Initialize a dictionary for notebook inspector scanning with initializing Count of Vulnerabilities found for
    # each severity as zero
    notebook_vul_sev_result = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    # Initialize a dictionary for model inspector scanning with initializing Count of Vulnerabilities found for
    # each severity as zero
    model_vul_sev_result = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    """TODO : Currently Only identifying the High , Medium and Low
              Vulnerabilities . Categorizing Critical Vulnerability feature
              will be coming soon."""

    if len(result_dict) != 0:
        result_dict = eval(result_dict)
        for key, value in result_dict.items():
            scanning_reports = value['scanning_reports']
            if key.endswith(".ipynb") or key.endswith(".py") or key.endswith(".txt"):
                for tool_output in scanning_reports:
                    tool_wise_vulnerability_severity_map = dict()
                    if tool_output['tool'] == "Detect-Secret":
                        tool_wise_vulnerability_severity_map, output_log = detect_secret_output_parser(
                            tool_output['output_log'])
                        tool_output['output_log'] = output_log

                    elif tool_output['tool'] == "Whisper":
                        tool_wise_vulnerability_severity_map, output_log = whisper_output_parser(
                            tool_output['output_log'])
                        tool_output['output_log'] = output_log

                    elif tool_output['tool'] == "Presidio-Analyzer":
                        # As output is in string format no need for eval 
                        tool_wise_vulnerability_severity_map, output_log = presidio_analyzer_output_parser(
                            tool_output['output_log'])
                        tool_output['output_log'] = output_log

                    elif tool_output['tool'] == "Safety":
                        tool_wise_vulnerability_severity_map, output_log = safety_output_parser(
                            tool_output['output_log'])
                        tool_output['output_log'] = output_log

                    # Create an aggregator result of Severity vs number of Vulnerabilities found
                    for k, v in tool_wise_vulnerability_severity_map.items():
                        if k in notebook_vul_sev_result:
                            notebook_vul_sev_result[k] += v
                        else:
                            notebook_vul_sev_result[k] = v

                result_dict[key] = scanning_reports

                pass

            else:
                for tool_output in scanning_reports:
                    if len(tool_output) != 0:
                        tool_wise_vulnerability_severity_map = model_inspector_result_parser(tool_output)
                    # Iterate through the keys of both dictionaries
                    # Create an aggregator result of Severity vs number of Vulnerabilities found
                    for k, v in tool_wise_vulnerability_severity_map.items():
                        if k in model_vul_sev_result:
                            model_vul_sev_result[k] += v
                        else:
                            model_vul_sev_result[k] = v

    return notebook_vul_sev_result, model_vul_sev_result, result_dict


def detect_secret_output_parser(output: str):
    """
            Description: This function will take the output log generated by detect secret tool and
                         identifies how many vulnerabilities found and its severity and return
                         the number of vulnerabilities found according to the severity type.

            input_parameter :
                    output : str, Mandatory
                            DESCRIPTION. output logs in list format.
            Returns
            -------
                vulnerability_severity_map : int
                          DESCRIPTION. dictionary map of High vulnerabilities found and its severity .

    """
    """ As Detect Secret scanning identifies API Key , Secret Key , High entropy string , PII related 
        information . So Vulnerability Severity might be low, medium and high according to the 
        type we will be detecting. The type to severity map is mentioned in the below , according to 
        that map will be mark the severity found from the output log"""

    detect_secret_severity_map = {
        "Artifactory Credentials": "High",
        "AWS Access Key": "High",
        "Azure Storage Account access key": "High",
        "Basic Auth Credentials": "High",
        "Cloudant Credentials": "High",
        "Discord Bot Token": "High",
        "GitHub Token": "High",
        "High Entropy String": "High",
        "Base64 High Entropy String": "High",
        "Hex High Entropy String": "High",
        "IBM Cloud IAM Key": "High",
        "IBM COS HMAC Credentials": "High",
        "JSON Web Token": "High",
        "Secret Keyword": "High",
        "Mailchimp Access Key": "High",
        "NPM tokens": "High",
        "Private Key": "High",
        "SendGrid API Key": "High",
        "Slack Token": "High",
        "Softlayer Credentials": "High",
        "Square OAuth Secret": "High",
        "Stripe Access Key": "High",
        "Twilio API Key": "High"
    }

    vulnerability_severity_map = dict()  # Initialize an empty dictionary for scanning results
    try:
        output = eval(output)
        # If output is not empty, attempt to parse
        if len(output) != 0:
            for key, value in output['results'].items():
                for out in value:
                    if out['type'] in detect_secret_severity_map:
                        severity = detect_secret_severity_map[out['type']]
                        if severity in vulnerability_severity_map:
                            vulnerability_severity_map[severity] = int(vulnerability_severity_map[severity]) + 1
                        else:
                            vulnerability_severity_map[severity] = 1

                        out["vulnerability_severity"] = severity
                    else:
                        out["vulnerability_severity"] = "UNKNOWN"
    except Exception as e:
        print("Failed to parse detect_secret_output {}".format(e))
    return vulnerability_severity_map, output


def whisper_output_parser(output: str):
    """
        Description: This function will take the output log generated by whisper tool and
                     identifies how many vulnerabilities found and its severity and return
                     the number of vulnerabilities found according to the severity type.

        input_parameter :
                output : str, Mandatory
                        DESCRIPTION. output logs in list format.
        Returns
        -------
            vulnerability_severity_map : int
                      DESCRIPTION. dictionary map of High vulnerabilities found and its severity .

    """
    """ As Whisper scanning always identifies the API Keys and secret key related Vulnerabilities
        So , any Exposure of API keys and secrets can lead to unauthorized access to sensitive systems
         and data, leading to potential data breaches and other security incidents.
         So all whisper relates vulnerabilities found consider as High"""

    vulnerability_severity_map = dict()  # Initialize an empty dictionary for scanning results
    try:
        # If output is not empty, attempt to parse
        output = eval(output)
        if len(output) != 0:
            for out in output:
                whisper_sev_key = out['severity'].lower()
                if whisper_sev_key == "info" or whisper_sev_key == "minor" or whisper_sev_key == "low":
                    vul_sev_key = "Low"
                elif whisper_sev_key == "major" or whisper_sev_key == "medium":
                    vul_sev_key = "Medium"
                elif whisper_sev_key == "blocker" or whisper_sev_key == "critical" or whisper_sev_key == "high":
                    vul_sev_key = "High"
                out['vulnerability_severity'] = vul_sev_key
                if vul_sev_key in vulnerability_severity_map:
                    vulnerability_severity_map[vul_sev_key] = int(vulnerability_severity_map[vul_sev_key]) + 1
                else:
                    vulnerability_severity_map[vul_sev_key] = 1

    except Exception as e:
        print("Failed to parse whisper_output {}".format(e))

    return vulnerability_severity_map, output


def safety_output_parser(output: str):
    """
            Description: This function will take the output log generated by whisper tool and
                         identifies how many vulnerabilities found and its severity and return
                         the number of vulnerabilities found according to the severity type.

            input_parameter :
                    output : str, Mandatory
                            DESCRIPTION. output logs in list format.
            Returns
            -------
                vulnerability_severity_map :
                          DESCRIPTION. dictionary map of High vulnerabilities found and its severity .

    """
    """ As Safety scanning always identifies the Use of vulnerable libraries can lead to various
     security vulnerabilities, including unauthorized data access, data corruption, and other
      critical issues. So all Safety relates vulnerabilities found consider as High"""

    vulnerability_severity_map = dict()  # Initialize an empty dictionary for scanning results
    vulnerability_severity = ""
    try:
        if isinstance(output, str):
            output_log = eval(output) if len(output) >= 2 else {}

        if 'scanned_packages' in output.keys():
            for key, value in output_log["scanned_packages"].items():
                version = "" if value['version'] is None else value['version']
                if key in output["affected_packages"].keys():
                    insecure_versions = output["affected_packages"][key]["insecure_versions"]

                    if version in insecure_versions:
                        # update to higher vulnerability score when lower found
                        if vulnerability_severity in ["", "Medium"]:
                            vulnerability_severity = "High"
                        output['scanned_packages'][key]['package_vulnerability_severity'] = "High"

                    else:
                        if vulnerability_severity not in ['High', 'Medium']:
                            vulnerability_severity = 'Medium'
                        output['scanned_packages'][key]['package_vulnerability_severity'] = "Medium"

                else:
                    print("Affected package not detected.")

            vulnerability_severity_map["High"] = len(output["affected_packages"])
            output['scanned_packages']['vulnerability_severity'] = vulnerability_severity

    except Exception as e:
        print("Failed to parse safety_output {}".format(e))

    return vulnerability_severity_map, output


def presidio_analyzer_output_parser(output: str):
    """
            Description: This function will take the output log generated by presidio_analyzer tool and
                         identifies how many vulnerabilities found and its severity and return
                         the number of vulnerabilities found according to the severity type.

            input_parameter :
                    output : str, Mandatory
                            DESCRIPTION. output logs in list format.
            Returns
            -------
                vulnerability_severity_map : dict
                          DESCRIPTION.  dictionary map of High vulnerabilities found and its severity .

    """
    """ As Presidio Analyzer Scanning always identifies detection of SSN along with other PIIs 
        increases the risk of identity theft and other serious privacy violations. So SSN related
        vulnerabilities found consider as High or else will consider as Medium"""

    vulnerability_severity_map = dict()  # Initialize an empty dictionary for scanning results

    # Harding the type value here , if type we found as SSN will mark as high severity
    high_severity_string = ["SSN", "ssn"]
    final_output = []
    try:
        # If output is not empty, attempt to parse
        if len(output) != 0:
            output_list = output.split("\n")
            for out in output_list:
                if out.split(",")[0] in high_severity_string:
                    out = out + ", vulnerability_severity: High"
                    if "High" in vulnerability_severity_map:
                        vulnerability_severity_map["High"] = int(vulnerability_severity_map["High"]) + 1
                    else:
                        vulnerability_severity_map["High"] = 1

                else:
                    out = out + ", vulnerability_severity: Medium"
                    if "Medium" in vulnerability_severity_map:
                        vulnerability_severity_map["Medium"] = int(vulnerability_severity_map["Medium"]) + 1
                    else:
                        vulnerability_severity_map["Medium"] = 1
                final_output.append(out)
    except Exception as e:

        print("Failed to parse presidio_analyzer_output {}".format(e))

    return vulnerability_severity_map, "\n".join(final_output)
