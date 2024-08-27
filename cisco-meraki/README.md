# User Guide | Keeper Security / Cisco 

## Overview

This user guide covers the post-rotation script for the Keeper Security / Cisco Meraki integration. Details on how to use the post-rotation script are available at the [_Keeper Security online documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts) and will not be repeated here.

## Pre-requisites

In order to use the post-rotation script, you will need the following prerequisites:

**1. Requests Library:** Ensure that the requests library is installed in your Python environment. This library is necessary for making HTTP requests to Cisco Meraki Endpoint.

### Requests library installation   

The Requests library allows you to send HTTP requests easily. Activate a Python virtual environment in your Keeper Gateway environment and install the library using the following command:

    pip install requests


## Using the Script

Once you have your prerequisites ready, make sure you cover the following:

1. Ensure that the post-rotation script references the Keeper Security record containing your Cisco meraki credentials. By default the script references to record title 'Cisco Authentication Record'.
2. Attach the post-rotation script to a Keeper Security PAM user record using the Keeper Security documentation. When this record has its secrets rotated, the post-rotation script will execute and update the password for the specified Cisco meraki user.
3. While creating the Keeper Security record containing your Cisco meraki credentials, add the Meraki API key in password field, and make sure to add a custom text field called 'network_id' and add the Network ID of the Cisco Meraki account as the value.
4. The user whose password is getting rotated should not be an administrator and must be Authorized for Client VPN [While adding the user via user management portal, the authorized option should be selected as 'Yes'].

This guide provides essential information for integrating Keeper Security with Cisco devices, enabling automated password rotation and ensuring secure management of credentials.