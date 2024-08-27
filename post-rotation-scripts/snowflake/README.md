# User Guide | Keeper Security / Snowflake 

## Overview

This user guide covers the post-rotation script for the Keeper Security / Snowflake integration. Details on how to use the post-rotation script are available at the [_Keeper Security online documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts) and will not be repeated here.

## Pre-requisites

In order to use the post-rotation script, you will need the following prerequisites:

**1. snowflake.connector Library:** Ensure that the snowflake connector library is installed in your python environment.

### Snowflake connector installation

The Snowflake Connector for Python provides an interface for developing Python applications that can connect to Snowflake and perform all standard operations. You should have snowflake connector library installed in your python environment to successfully run the post-rotation script. To install snowflake connector, activate a Python virtual environment in your keeper-gateway environment and run the following command:

    pip install snowflake-connector-python


#### NOTE: If you want to use a virtual environment, add a shebang line at the top of the script as documented here [_Python Environment Setup_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts/use-case-examples/rotate-credential-via-rest-api#step-5-python-environment-setup)

## Using the script

Once you have your pre-requisites ready, make sure you cover the following:

1. Ensure that the post-rotation script references the Keeper Security record containing your Snowflake admin credentials.

Once this is done, attach the post-rotation script to a Keeper Security PAM user record using the Keeper Security [_documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts). When this record has its secrets rotated, the post-rotation script will run and update the password for given snowflake user.
