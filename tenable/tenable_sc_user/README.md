# User Guide | Keeper Security / Tenable 

## Overview

This user guide covers the post-rotation script for the Keeper Security / Tenable SC  integration. Details on how to use the post-rotation script are available at the [_Keeper Security online documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts) and will not be repeated here.

## Using the script

1. Ensure that the post-rotation script references the Keeper Security record containing your Tenable SC API credentials.

Once this is done, attach the post-rotation script to a Keeper Security PAM user record using the Keeper Security [_documentation_](https://docs.keeper.io/en/v/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts). When this record has its secrets rotated, the post-rotation script will run and update the secret in Tenable.

The given post-rotation script is not tested as we do not have a suitable testing environment.