#!/usr/local/bin/pam_rotation_venv_python3

'''
Password rotation script for Tenable Credential Records.

This script is designed to rotate the password for a given Tenable Authentication Record using the Tenable API.
It facilitates the automated updating of credentials in your Tenable environment.

NOTE: If spaces are present in the path to the python interpreter, the script will fail to execute.
    This is a known limitation of the shebang line in Linux and you will need to create a symlink
    to the python interpreter in a path that does not contain spaces.
    For example: sudo ln -s "/usr/local/bin/my python3.7" /usr/local/bin/pam_rotation_venv_python3
'''

import asyncio
import sys
import base64
import json

'''
Optionally display installed packages for debugging. Uncomment if needed.
import pkg_resources
print("# \n# Installed packages for debugging:")
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
for m in installed_packages_list:
    print(f"  {m}")
'''

# Import the requests library
try:
    import requests
except ImportError:
    print("# Error: The 'requests' package is not installed. Run 'pip install requests' to install it.")
    exit(1)

def get_credential_uuid(service_url, service_access_token, tenable_credential_name):
    """
    Get the UUID of a Tenable Credential based on its name.

    Args:
    - service_url : URL to send API request to Tenable.
    - service_access_token : Authorization token for the API request [Combination of Access Key and Secret].
    - tenable_credential_name : Name of the credential for which the UUID is to be fetched.

    Returns:
    - JSON: The JSON response containing the UUID of the credential, or None if there was an error.
    """

    request_url = f"{service_url}?name:eq:\"{tenable_credential_name}\""

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-ApiKeys": service_access_token
    } # Headers for the request
    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        return response.json() # Return JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching UUID using credential name: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None # Return None if there was an error

def get_credential_details(service_url, service_access_token, uuid):
    """
    Get the details of a Tenable Credential based on its UUID.

    Args:
    - service_url : URL to send API request to Tenable.
    - service_access_token : Authorization token for the API request [Combination of Access Key and Secret].
    - uuid : UUID of the credential for which details are to be fetched.

    Returns:
    - JSON: The JSON response containing the details of the credential, with the 'type' property removed, or None if there was an error.
    """
     
    request_url = f"{service_url}/{uuid}"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-ApiKeys": service_access_token
    } # Headers for the request
    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        credentials = response.json()
        if 'type' in credentials:
            del credentials['type']
        return credentials # Return JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching credential details using UUID: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None # Return None if there was an error

def get_updated_settings(credentials, new_password):
    """
    Update the password field in a credential record.

    Args:
    - credentials : Dictionary containing the credential record.
    - new_password : The new password to be set in the credential record.

    Returns:
    - Dictionary: The updated credential record with the password field modified.
    """

    return {
        **credentials,
        "settings": {
            **credentials["settings"],
            "password": new_password
        }
    }

def update_credential_password(service_url, service_access_token, uuid, credentials):
    """
    Update the password of a credential record.

    Args:
    - service_url : URL to send API request to Tenable.
    - service_access_token : Authorization token for the API request.
    - uuid : UUID of the credential record to be updated.
    - credentials : Updated credential record containing the new password.

    Returns:
    - This function does not return any value.
    """

    request_url = f"{service_url}/{uuid}"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-ApiKeys": service_access_token
    } # Headers for the request
    try:
        put_response = requests.put(request_url, headers=headers, json=credentials)
        put_response.raise_for_status()
        print("Password updated successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during PUT request: {http_err}")
    except Exception as err:
        print(f"An error occurred during PUT request: {err}")

# Function to rotate password
def rotate(service_url, service_access_token, tenable_credential_name, new_password):
    """
    Rotate the password for a given Tenable Credential Name.

    Args:
    - service_url : Url to send API request to Tenable.
    - service_access_token : Authorization token for the API request.
    - tenable_credential_name : Credential name for the record whose password has to be rotated.
    - new_password : The new password to be set at ["settings"]["password"] field for the specific UUID.

    Returns:
    - This function does not return any value.
    """

    # Get credential UUID
    credentials_list = get_credential_uuid(service_url, service_access_token, tenable_credential_name)
    
    if credentials_list and 'credentials' in credentials_list and len(credentials_list['credentials']) > 0:
        uuid = credentials_list["credentials"][0].get("uuid")
        if not uuid:
            print("UUID not found in the credential.")
            return
        
        # Get credential details
        credentials = get_credential_details(service_url, service_access_token, uuid)
        
        if credentials and "settings" in credentials:
            # Update credentials password field with rotated password generated using Keeper
            updated_credentials = get_updated_settings(credentials,new_password)
            
            # Update credential password via PUT request
            update_credential_password(service_url, service_access_token, uuid, updated_credentials)
        
        else:
            print("Failed to fetch credentials or settings field missing.")
    
    else:
        print("No credentials obtained for given credential name or credentials list is empty.")

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
    service_url = api_access_token_record.get('url')
    tenable_access_key = api_access_token_record.get('tenable_access_key')
    tenable_secret_key = api_access_token_record.get('tenable_secret_key')
    service_access_token = f"accessKey={tenable_access_key};secretKey={tenable_secret_key}"
    
    # Credential name for the record whose password needs to be rotated.
    tenable_credential_name = params.get('user')

    # Extract new rotated password to be sent via PUT to Tenable API.
    new_password = params.get('newPassword')
 
    if not all([service_url, service_access_token, tenable_credential_name]):
        print("# Error: One or more required fields are missing in the access token record.")
        exit(1)
    
    # Rotate the password for a given Tenable Credential Name.
    rotate(service_url, service_access_token, tenable_credential_name, new_password)

if __name__ == "__main__":
    main()
