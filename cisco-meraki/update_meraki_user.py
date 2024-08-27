'''
Password rotation script for Cisco meraki user accounts.

This script is designed to rotate the password for a given Cisco Meraki User.
It facilitates the automated updating of user password in your Cisco meraki environment.

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

def fetch_meraki_user_by_email(api_key, network_id, email):
    """
    Fetches User details by email.
    
    Args:
    - api_key (str): The Meraki API key.
    - network_id (str): The network ID to search within.
    - email (str): The email of the user to fetch.
    
    Returns:
    - User details if found, otherwise None.
    """
    if not network_id:
        print("Invalid network ID.")
        return None

    # URL to fetch Meraki dashboard users
    users_url = f"https://api.meraki.com/api/v1/networks/{network_id}/merakiAuthUsers"
    headers = {
        'X-Cisco-Meraki-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        # Make GET request to fetch users
        response = requests.get(users_url, headers=headers)
        response.raise_for_status()
        # Parse response JSON
        users = response.json()

        if users:
            for user in users:
                if user['email'] == email:
                    print("\nUser found for the email-", email)
                    return user
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Meraki dashboard users: {e}")
        return None

def update_meraki_user_password(api_key, network_id, user_id, new_password):
    """
    Updates the password for a Meraki dashboard user.
    
    Args:
    - api_key (str): The Meraki API key.
    - network_id (str): The network ID the user belongs to.
    - user_id (str): The ID of the user to update.
    - new_password (str): The new password to set.
    
    Returns:
    - bool: True if successful, otherwise False.
    """
    if not network_id:
        print("Invalid network ID.")
        return False

    # URL to update a specific user's password
    user_url = f"https://api.meraki.com/api/v1/networks/{network_id}/merakiAuthUsers/{user_id}"
    headers = {
        'X-Cisco-Meraki-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {'password': new_password}

    # Make PUT request to update user's password
    response = requests.put(user_url, headers=headers, json=payload)
    
    return response

def rotate(meraki_network_id, meraki_api_key, meraki_user_email, new_password):
    """
    Rotate the password for a given Cisco user.
    Args:
    - meraki_network_id (str): Network ID of the network where the user is located.
    - meraki_api_key (str): API access key for authorization.
    - meraki_user_email (str): Email of the user whose password needs to be rotated.
    - new_password (str): The new password to be set for the Cisco user.
    Returns:
    - None
    """
    
    # Calls the function fetch_meraki_user_by_email to fetch the user details using user email.
    user = fetch_meraki_user_by_email(meraki_api_key, meraki_network_id, meraki_user_email)

    # If the user does not exist, print the message and exit the program
    if not user:
        print(f"No user found with the email: {meraki_user_email}")
        exit(1)
    
    try:
        meraki_user_id = user['id']

        # Updating password for the given user using ID
        response = update_meraki_user_password(meraki_api_key, meraki_network_id, meraki_user_id, new_password)
        if response.status_code == 200:
            print(f"Password updated successfully for user with email {meraki_user_email}")
        else:
            print(f"Failed to update password. Status code: {response.status_code}, Error: {response.text}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while updating the password for the given user email: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def main():
    """
    Main function to rotate the password for a Cisco meraki user.

    Reads and decodes input parameters from stdin, including the authentication record details
    and the new password. Then, updates the password of the specified Cisco meraki user.
    """
    record_title = 'Cisco Authentication Record' #This should be same as the title of the record containing meraki api key and network ID details. 
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
    
    # Network ID of the network where the user is located
    meraki_network_id = api_access_token_record.get('network_id')
    
    # API Key for Cisco meraki api authentication
    meraki_api_key = api_access_token_record.get('password')

    # Email of the Cisco meraki user whose password needs to be rotated
    meraki_user_email = params.get('user')

    # New password to set for the Cisco meraki user
    new_password = params.get('newPassword')
    
    # Check if all required fields are present
    if not all([meraki_network_id, meraki_api_key, meraki_user_email]):
        print("# Error: One or more required fields are missing in the access token record.")
        exit(1)

    # Rotate the password for the specified Cisco meraki user
    rotate(meraki_network_id, meraki_api_key, meraki_user_email, new_password)

if __name__ == "__main__":
    main()
