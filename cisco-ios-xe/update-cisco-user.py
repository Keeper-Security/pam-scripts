'''
Password rotation script for Cisco user accounts.

This script is designed to rotate the password for a given Cisco user.
It facilitates the automated updating of user password in your Cisco environment.

NOTE: If spaces are present in the path to the python interpreter, the script will fail to execute.
    This is a known limitation of the shebang line in Linux and you will need to create a symlink
    to the python interpreter in a path that does not contain spaces.
    For example: sudo ln -s "/usr/local/bin/my python3.7" /usr/local/bin/pam_rotation_venv_python3
'''

import sys
import base64
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
'''
Optionally display installed packages for debugging. Uncomment if needed.
import pkg_resources
print("# \n# Installed packages for debugging:")
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
for m in installed_packages_list:
    print(f"  {m}")
'''

# Import the requests package
try:
    import requests
except ImportError:
    print("# Error: The 'requests' package is not installed. Run 'pip install requests' to install it.")
    exit(1)

def get_username_details(cisco_url, cisco_admin_username, cisco_admin_password, cisco_user_name):
    """
    Verify the Cisco user.
    Args:
    - cisco_url (str): The host endpoint of the Cisco account to connect to.
    - cisco_admin_username (str): The username of the Cisco admin account.
    - cisco_admin_password (str): The password of the Cisco admin account.
    - cisco_user_name (str): The name of the Cisco user whose password needs to be rotated.
    Returns:
    - True if username found.
    """
    
    # Constructs the request URL for the username API endpoint
    request_url = f"{cisco_url}username/"
    
    # Sets the headers for the RESTCONF request, specifying that we expect and send YANG data in JSON format
    headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
    }
    try:
        # Sends a GET request to the Cisco router to fetch user details
        response = requests.get(request_url, headers=headers, auth=(cisco_admin_username,cisco_admin_password), verify=False)
        response.raise_for_status()
        data = response.json()
        # Extracts the list of usernames from the response data
        usernames = data["Cisco-IOS-XE-native:username"]
        # Iterates through the list of usernames to find the specified user
        for user in usernames:
            if user["name"]==cisco_user_name:
                # Returns True if the specified username is found
                return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching username details from Cisco router: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return False

def rotate(cisco_url, cisco_admin_username, cisco_admin_password, cisco_user_name, new_password):
    """
    Rotate the password for a given Cisco user.
    Args:
    - cisco_url (str): The host endpoint of the Cisco account to connect to.
    - cisco_admin_username (str): The username of the Cisco admin account.
    - cisco_admin_password (str): The password of the Cisco admin account.
    - cisco_user_name (str): The name of the Cisco user whose password needs to be rotated.
    - new_password (str): The new password to be set for the Cisco user.
    Returns:
    - None
    """
    
    # Calls the function get_username_details to check if the specified user exists on the Cisco router
    user = get_username_details(cisco_url, cisco_admin_username, cisco_admin_password, cisco_user_name)

    # If the user does not exist, print an error message and exit the program
    if not user:
        print(f"No user found with the username: {cisco_user_name}")
        exit(1)
    
    # Sets the headers for the RESTCONF request, specifying that we expect and send YANG data in JSON format
    headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
    }

    # Creates the data payload for the PATCH request to update the user's password
    data = {
    "Cisco-IOS-XE-native:native": {
        "username": [
                {
                "name": cisco_user_name,
                "password": {
                    "password": new_password
                    }
                }
            ]
        }
    }
    
    try:
        # Sends a PATCH request to the Cisco router to update the user's password
        response = requests.patch(cisco_url, headers=headers, auth=(cisco_admin_username,cisco_admin_password), data=json.dumps(data), verify=False)
        response.raise_for_status()
        print(f"Password updated successfully for user {cisco_user_name}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while updating the password for the given user: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def main():
    """
    Main function to rotate the password for a Cisco device user.

    Reads and decodes input parameters from stdin, including the authentication record details
    and the new password. Then, updates the password of the specified Cisco device user.
    """
    record_title = 'Cisco Authentication Record' #This should be same as the title of the record containing username, password and host endpoint details. 
    api_access_token_record = None
    params = None
    
    # Read and decode input parameters from stdin
    for base64_params in sys.stdin:
        params = json.loads(base64.b64decode(base64_params).decode())

        # Decode and load records passed in as JSON strings from the PAM Script section as "Rotation Credential" records
        records = json.loads(base64.b64decode(params.get('records')).decode())
        # Find the record that matches the specified title
        api_access_token_record = next((record for record in records if record['title'].lower() == record_title.lower()), None)
        break

    if api_access_token_record is None:
        print(f"# Error: No Record with the access token found. Title: {record_title}")
        exit(1)
    
    # Extract Details from the record
    # HostName endpoint of the Cisco device endpoint.
    cisco_router_endpoint = api_access_token_record.get('host_endpoint') 
    # Admin username for the Cisco device
    cisco_admin_username = api_access_token_record.get('login')
    # Admin password for the Cisco device
    cisco_admin_password = api_access_token_record.get('password')

    # Username of the Cisco device user whose password needs to be rotated
    cisco_user_name = params.get('user')
    # New password to set for the Cisco device user
    new_password = params.get('newPassword')
    
    # Check if all required fields are present
    if not all([cisco_router_endpoint, cisco_admin_username, cisco_admin_password, cisco_user_name]):
        print("# Error: One or more required fields are missing in the access token record.")
        exit(1)
    
    # Construct the Cisco API URL
    cisco_url = f"https://{cisco_router_endpoint}/restconf/data/Cisco-IOS-XE-native:native/"

    # Rotate the password for the specified Cisco device user
    rotate(cisco_url, cisco_admin_username, cisco_admin_password, cisco_user_name, new_password)

if __name__ == "__main__":
    main()
