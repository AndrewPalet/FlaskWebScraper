import os, uuid

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import date

"""
def createBlobLog creates blob container in azure storage and uploads a log file to the container

:param str container_name: name of the container
:param str log_filepath: filepath to logfile
:param str log_filename: name of the logfile

"""
def createBlobLog(container_name, log_filepath, log_filename):
    try:
        # Quick start code goes here
        # Retrieve the connection string for use with the application. The storage
        # connection string is stored in an environment variable on the machine
        # running the application called AZURE_STORAGE_CONNECTION_STRING. If the environment variable is
        # created after the application is launched in a console or with Visual Studio,
        # the shell or application needs to be closed and reloaded to take the
        # environment variable into account.
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        connect_str = ""

        # Create the BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container = ContainerClient.from_connection_string(connect_str, container_name)

        # Create the container, if it doesn't exist create it
        try:
            container_properties = container.get_container_properties()
            print("Container: " + container_name +  " exists")
        except Exception as e:
            container_client = blob_service_client.create_container(container_name)
            print(e)
            print("Container: " + container_name + " did not exist so we have created it.")

        # Create a blob client using the log file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=log_filename)

        print("\nUploading to Azure Storage as blob:\n\t" + log_filename)

        # Upload the created file
        with open(log_filepath, "rb") as data:
            blob_client.upload_blob(data, overwrite = True)

    except Exception as ex:
        print('Exception:')
        print(ex)

