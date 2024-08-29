#!/usr/local/bin/pam_rotation_venv_python3

'''
Password rotation script for Snowflake user accounts.

This script is designed to rotate the password for a given Snowflake user using the snowflake connector package.
It facilitates the automated updating of user password in your Snowflake environment.

NOTE: If spaces are present in the path to the python interpreter, the script will fail to execute.
    This is a known limitation of the shebang line in Linux and you will need to create a symlink
    to the python interpreter in a path that does not contain spaces.
    For example: sudo ln -s "/usr/local/bin/my python3.7" /usr/local/bin/pam_rotation_venv_python3
'''
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

# Import the snowflake connector package
try:
    import snowflake.connector
except ImportError:
    print("# Error: The 'snowflake connector' package could not be imported. Run 'pip install snowflake-connector-python' to install it.")
    exit(1)

def rotate(snowflake_account_name, snowflake_admin_user, snowflake_admin_pass, snowflake_user_name, new_password):
    """
    Connects with Snowflake using the snowflake.connector module.
    Rotate the password for a given Snowflake user.

    Args:
    - snowflake_account_name (str): The name of the Snowflake account to connect to.
    - snowflake_admin_user (str): The username of the Snowflake admin account.
    - snowflake_admin_pass (str): The password of the Snowflake admin account.
    - snowflake_user_name (str): The name of the Snowflake user whose password needs to be rotated.
    - new_password (str): The new password to be set for the Snowflake user.

    Returns:
    - None
    """

    # Connect with snowflake account using snowflake.connector module
    try:
        conn = snowflake.connector.connect(
        user=snowflake_admin_user,
        password=snowflake_admin_pass,
        account=snowflake_account_name
        )
    except Exception as E:
        print(f"Unable to connect to snowflake account. Error: {E}")
        exit(1)
    
    # Create a cursor object
    cur = conn.cursor()
    
    # Change new user's password
    try:
        change_pass_query = f"ALTER USER {snowflake_user_name} SET PASSWORD = '{new_password}'"
        cur.execute(change_pass_query)
    except Exception as E:
        print(f"Unable to update the password. Error: {E}")
        exit(1)

    # Close the cursor and connection
    cur.close()
    conn.close()

    print(f"Password successfully rotated for the given Snowflake User - {snowflake_user_name}")

def main():
    """
    Main function to rotate the password for a given Snowflake User.

    Reads and decodes input parameters from stdin, including the authentication record details
    and the new password. Then, updates the password of the specified Snowflake user.

    Args:
    - None

    Returns:
    - None
    """
    record_title = 'Snowflake Authentication Record' #This should be same as the title of the record containing admin credentials.
    admin_credential_record = None
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

        # Find the Record that contains the admin account details by its Title
        admin_credential_record = next((record for record in records if record['title'].lower() == record_title.lower()), None)
        break

    if admin_credential_record is None:
        print(f"# Error: No Record with the access token found. Title: {record_title}")
        exit(1)

    # Extract Details from the record
    snowflake_account_name = admin_credential_record.get('snowflake_account_name')
    snowflake_admin_user = admin_credential_record.get('login')
    snowflake_admin_pass = admin_credential_record.get('password')
    
    # Username for the user whose password needs to be rotated.
    snowflake_user_name = params.get('user')

    # Extract new rotated password..
    new_password = params.get('newPassword')
    
    if not all([snowflake_account_name, snowflake_admin_user, snowflake_admin_pass]):
        print("# Error: One or more required fields are missing in the authentication record.")
        exit(1)
   
    # Rotate the password for a given Snowflake user.
    rotate(snowflake_account_name, snowflake_admin_user, snowflake_admin_pass, snowflake_user_name, new_password)

if __name__ == "__main__":
    main()
