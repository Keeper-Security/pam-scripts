#!/usr/local/bin/pam_rotation_venv_python3

'''
Password rotation script for Tenable Credential Records.

This script is designed to rotate the password for a given Tenable Authentication Record using the PyTenable's TenableIO package.
It facilitates the automated updating of credentials in your Tenable environment.

NOTE: If spaces are present in the path to the python interpreter, the script will fail to execute.
    This is a known limitation of the shebang line in Linux and you will need to create a symlink
    to the python interpreter in a path that does not contain spaces.
    For example: sudo ln -s "/usr/local/bin/my python3.7" /usr/local/bin/pam_rotation_venv_python3
'''
import asyncio
import json
import sys
import base64

'''
Optionally display installed packages for debugging. Uncomment if needed.
import pkg_resources
print("# \n# Installed packages for debugging:")
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
for m in installed_packages_list:
    print(f"  {m}")
'''

# Import the TenableIO package
try:
    from tenable.io import TenableIO
except ImportError:
    print("# Error: The 'TenableIO' package could not be imported. Run 'pip install pytenable' to install it.")
    exit(1)

def rotate(tenable_access_key, tenable_secret_key, tenable_credential_name, new_password):
    """
    Connects with Tenable using the TenableIO package.
    Rotate the password for a given Tenable Credential Name.

    Args:
    - tenable_access_key (str): The access key for connecting to Tenable.
    - tenable_secret_key (str): The secret key for connecting to Tenable.
    - tenable_credential_name (str): The name of the Tenable Credential Record whose password needs to be rotated.
    - new_password (str): The new password to be set for the Tenable Credential Record.

    Returns:
    - None
    """

    # Connect with tenable using TenableIO package
    tio = TenableIO(tenable_access_key, tenable_secret_key)
    
    # Retrieve a list of credentials matching the specified Tenable Credential Name and store them in the variable 'credential'.
    credential = list(tio.credentials.list(('name', 'eq', tenable_credential_name)))
    
    # If more than one or no credentials found with the given Credential Name, exit the program and print an error for debugging
    if len(credential)!=1:
        print("# ERROR: There should be exactly one credential with the given Tenable Credential Name.")
        exit(1)
    
    # Extract the UUID of the credential from the list
    credentials_uuid = credential[0]['uuid']
    
    # Updating the password of the Tenable Crdential using its UUID
    tio.credentials.edit(credentials_uuid,password=new_password)
    
    print(f"Password successfully rotated for the given Tenable Credential Name - {tenable_credential_name}")

def main():
    """
    Main function to rotate the password for a given Tenable Authentication Record.

    Reads and decodes input parameters from stdin, including the authentication record details
    and the new password. Then, updates the password of the specified Tenable Credential Record.

    Args:
    - None

    Returns:
    - None
    """
    
    record_title = 'Tenable Authentication Record' #This should be same as the title of the record containing access key and secret key.
    api_access_token_record = None
    params = None
    
    # Read and decode input parameters from stdin
    for base64_params in sys.stdin:
        params = json.loads(base64.b64decode(base64_params).decode())
        '''
        # Optionally print available params for debugging. Uncomment if needed.
        # print(f"# \n# Available params for the script:")
        # for key, value in params.items():
        #     print(f"#     {key}={value}")
        '''

        records = json.loads(base64.b64decode(params.get('records')).decode()) # Decode and load records that are passed into the record as JSON strings in the PAM Script section as "Rotation Credential" records

        # Find the Record that contains the access token by its Title
        api_access_token_record = next((record for record in records if record['title'].lower() == record_title.lower()), None)
        break

    if api_access_token_record is None:
        print(f"# Error: No Record with the access token found. Title: {record_title}")
        exit(1)

    # Extract Details from the record
    tenable_access_key = api_access_token_record.get('tenable_access_key')
    tenable_secret_key = api_access_token_record.get('tenable_secret_key')
    
    # Credential name for the record whose password needs to be rotated.
    tenable_credential_name = params.get('user')

    # Extract new rotated password to be updated using pyTenable.
    new_password = params.get('newPassword')
 
    if not all([tenable_access_key, tenable_secret_key, tenable_credential_name]):
        print("# Error: One or more required fields are missing in the access token record.")
        exit(1)
    
    # Rotate the password for a given Tenable Credential Name.
    rotate(tenable_access_key, tenable_secret_key, tenable_credential_name, new_password)

if __name__ == "__main__":
    main()
