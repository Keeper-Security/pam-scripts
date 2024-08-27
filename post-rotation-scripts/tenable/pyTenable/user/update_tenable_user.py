#!/usr/local/bin/pam_rotation_venv_python3

'''
Password rotation script for Tenable Users.

This script is designed to rotate the password for a given Tenable User using the PyTenable's TenableIO package.
It facilitates the automated updating of user password in your Tenable environment.

NOTE: If spaces are present in the path to the python interpreter, the script will fail to execute.
    This is a known limitation of the shebang line in Linux and you will need to create a symlink
    to the python interpreter in a path that does not contain spaces.
    For example: sudo ln -s "/usr/local/bin/my python3.7" /usr/local/bin/pam_rotation_venv_python3
'''
import asyncio
import json
import sys
import base64
from restfly.errors import UnauthorizedError
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

def fetch_user_id(tio, username):
    """
    Fetches the user ID from Tenable using the TenableIO package.

    Args:
    - tio (TenableIO): An instance of the TenableIO class for connecting to Tenable.
    - username (str): The username of the user whose ID needs to be fetched.

    Returns:
    - user_id(int) or None: The ID of the user if found, None otherwise.
    """
    try:
        for user in tio.users.list():
            if user["username"] == username:
                return user["id"]
        return None
    except UnauthorizedError as e:
        print(f"# Error: Access Key or Secret Key Invalid")
        exit(1)

def rotate(tenable_access_key, tenable_secret_key, tenable_user_name, old_password, new_password):
    """
    Connects with Tenable using the TenableIO package.
    Rotate the password for a given Tenable User.

    Args:
    - tenable_access_key (str): The access key for connecting to Tenable.
    - tenable_secret_key (str): The secret key for connecting to Tenable.
    - tenable_user_name (str): The username of the Tenable User whose password needs to be rotated.
    - old_password (str): The current password of the Tenable User.
    - new_password (str): The new password to be set for the Tenable User.

    Returns:
    - None
    """

    # Connect with tenable using TenableIO package
    tio = TenableIO(tenable_access_key, tenable_secret_key)
    
    # Fetch user id of the given Tenable User
    user_id = fetch_user_id(tio, tenable_user_name)

    if user_id is None:
        print(f"# Error: No user id fetched for the given username: {tenable_user_name}")
        exit(1)
    
    tio.users.change_password(user_id, old_password, new_password)
    
    print(f"Password successfully rotated for the given Tenable User - {tenable_user_name}")

def main():
    """
    Main function to rotate the password for a given Tenable Authentication Record.

    Reads and decodes input parameters from stdin, including the authentication record details
    and the new password. Then, updates the password of the specified Tenable User.

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
    
    # User name of the user whose password needs to be rotated.
    tenable_user_name = params.get('user')

    # Extract old password and new rotated password to be sent via TenableIO.
    old_password = params.get('oldPassword')
    new_password = params.get('newPassword')
    
    if not all([tenable_access_key, tenable_secret_key, tenable_user_name]):
        print("# Error: One or more required fields are missing in the access token record.")
        exit(1)
    
    # Rotate the password for a given Tenable User.
    rotate(tenable_access_key, tenable_secret_key, tenable_user_name, old_password, new_password)

if __name__ == "__main__":
    main()
