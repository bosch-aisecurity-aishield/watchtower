__author__ = "AIShield"
__copyright__ = "Copyright @2023 Bosch Global Software Technologies Private Limited."
__credits__ = "AIShield"
__license__ = "Apache-2.0"
__version__ = "1.0"
__maintainer__ = "AIShield"
__email__ = "AIShield.Contact@bosch.com"
__status__ = "Beta"

import os
import boto3  # !pip install boto3
from utils import helper


class AIShieldWatchtowerS3:
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, region: str = None,
                 bucket_name: str = None, local_dir: str = './s3_downloads'):
        """

        Args:
            aws_access_key_id: the access key id will be needed for connection.
            aws_secret_access_key: the access secret key, will be needed for s3 connection
            region:the region of s3 bucket
            bucket_name: the bucket name
            local_dir: local directory path, to download files from s3 buckets
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region = region
        self.bucket_name = bucket_name
        self.s3_directory = local_dir

        # when user passing credential as parameter
        if (self.aws_access_key_id is not None) and (self.aws_secret_access_key is not None) and (
                self.region is not None):
            self.s3_client = boto3.client(service_name='s3', region_name=self.region,
                                          aws_access_key_id=self.aws_access_key_id,
                                          aws_secret_access_key=self.aws_secret_access_key)
            self.s3_resource = boto3.resource(service_name='s3', region_name=self.region,
                                              aws_access_key_id=self.aws_access_key_id,
                                              aws_secret_access_key=self.aws_secret_access_key)
        else:
            # when aws credential is configured separately (e.g. aws config - with cli)
            self.s3_client = boto3.client(service_name='s3')
            self.s3_resource = boto3.resource(service_name='s3')

        # create bucket client to download files
        self.bucket = self.s3_resource.Bucket(self.bucket_name)

    def list_files_from_s3(self, bucket_name: str = None, file_extension: str = None):
        """
        Finds all the files ending with a given extension in the specified S3 bucket.

        Parameters
        ----------
        bucket_name : str, optional
            DESCRIPTION. The S3 bucket name, which need to be scanned. The default is None.
        file_extension : str, optional
            DESCRIPTION. the extension of the file we have to look for. The default is None.

        Returns
        -------
        matching_files : TYPE
            DESCRIPTION. list containing all the matching files

        """

        # list to store file with given extension
        matching_files = []

        # Create a reusable Paginator
        paginator = self.s3_client.get_paginator('list_objects')

        # Create a PageIterator from the Paginator , add paginationConfig to increase max items
        page_iterator = paginator.paginate(
            Bucket=bucket_name)  # Prefix=prefix, PaginationConfig={'MaxItems': max_items}

        for page in page_iterator:
            for dictionary in page['Contents']:
                file_name = dictionary['Key']
                if file_extension is not None:
                    if file_name.endswith(file_extension):
                        matching_files.append(file_name)
                else:
                    matching_files.append(file_name)

        return matching_files

    def download_file(self, object_name: str):
        """
        download object from s3 bucket, create folder and save it
        Args:
            object_name:

        Returns:

        """
        file_path, file_name = os.path.split(object_name)
        # create folder structure and download
        full_path = self.s3_directory
        for path in file_path.split("/"):
            full_path = os.path.join(full_path, path)
            helper.make_directory(path=full_path)

        file_path = os.path.join(full_path, file_name)
        self.bucket.download_file(object_name, file_path)

        return file_path

    def download_files(self, file_extensions: list):
        """
        download files with given extensions
        Args:
            file_extensions: extensions of file to be downloaded

        Returns:

        """
        matching_files = []
        # iterate to download file with extension
        for file_extn in file_extensions:
            object_list = self.list_files_from_s3(self.bucket_name, file_extn)

            # iterate to download file one  by one
            for object_name in object_list:
                file_path = self.download_file(object_name)
                matching_files.append(file_path)

        return matching_files
