# User Guide | Keeper Security / Snowflake 

## Overview

This user guide covers the post-rotation script for the Keeper Security / Snowflake integration. Details on how to use the post-rotation script are available at the [_Keeper Security online documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts) and will not be repeated here.

## Pre-requisites

In order to use the post-rotation script, you will need the following prerequisites:

**1. snowflake.connector Library:** Ensure that the snowflake connector library is installed in your python environment.

### Snowflake connector installation

The Snowflake Connector for Python provides an interface for developing Python applications that can connect to Snowflake and perform all standard operations. You should have snowflake connector library installed in your python environment to successfully run the post-rotation script. To install snowflake connector, activate a Python virtual environment in your keeper-gateway environment and run the following command:

    pip install snowflake-connector-python

## Steps to create Keeper security records and Snowflake user

### 1. Store Snowflake Admin Credentials

Store the Snowflake admin credentials in a Keeper Security record of type `Login` named as `Snowflake Authentication Record`. You will need this Keeper Security record name in order to run the post-rotation script.

### 2. Add custom field to Snowflake Authentication Record

- Add a custom field named `snowflake_account_name` to the Snowflake Authentication Record and set its value to account name of your snowflake account

    <img src="imgs/snowflakeAuthRecord.png" width="350" alt="Snowflake Authentication Record">

### 3. Create a Snowflake User

- Login to your Snowflake account.
- From the left hand side menu, go to `Admin`->`User & Roles`.

    <img src="imgs/user&roles.png" width="350" alt="user&roles">
- Click on `Add User` button present at the top right.
- Add user details and uncheck the `Force user to change password on first time login`. Then click on `Create User`.

    <img src="imgs/addUser.png" width="350" alt="addUser">

### 4. Create a New Rotation Record of type PAM User

- Create a New Rotation Record of type PAM User. Keep the title same as
the user name of the snowflake user we created previously.


### 5. Add details to the PAM User record

- Add the user name of the snowflake user in the `Login` field.
- Keep the `Password` field empty.

    <img src="imgs/addPAMuser.png" width="350" alt="PAM User Record">
- Click on Password Rotation Settings. Keep `Rotation` as `On-Demand`, select your `PAM Configuration`, and click on `Update`

    <img src="imgs/postRotationSettings.png" width="350" alt="postRotationSettings">
- In the PAM Scripts section, click on Add PAM Script. Attach the post rotation script here, choose `Snowflake Authentication Record` in `Rotation Credential`, enter the script command. Now click on Add.

    <img src="imgs/addPAMscript.png" width="350" alt="addPAMscript">
- Now add a custom field of type `Text`. Add the label as `NOOP` and keep the vale as `True`.

    <img src="imgs/addCustomField.png" width="350" alt="addCustomField">
- Save the PAM User record.

### 6. Rotate the Snowflake User Credentials.

- Open the PAM User Record created in the previous step and click on `Rotate Now`. When this record has its secrets rotated, the post-rotation script will run and update the password for given snowflake user.

    <img src="imgs/rotateNow.png" width="350" alt="rotateNow">

#### NOTE: If you want to use a virtual environment, add a shebang line at the top of the script as documented here [_Python Environment Setup_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts/use-case-examples/rotate-credential-via-rest-api#step-5-python-environment-setup)

## Using the script

Once you have your pre-requisites ready, make sure you cover the following:

1. Ensure that the post-rotation script references the Keeper Security record containing your Snowflake admin credentials.

Once this is done, attach the post-rotation script to a Keeper Security PAM user record using the Keeper Security [_documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts). When this record has its secrets rotated, the post-rotation script will run and update the password for given snowflake user.
