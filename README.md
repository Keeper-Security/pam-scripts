**Keeper Secrets Manager** ("KSM") provides your DevOps, IT Security and software development teams with a fully cloud-based, Zero-Knowledge platform for managing all of your infrastructure secrets such as API keys, Database passwords, access keys, certificates and any type of confidential data.

**Keeper Privileged Access Manager** ("KeeperPAM") is a zero-knowledge platform which protects against unauthorized access and security breaches.

This repo contains sample "Post-rotation scripts" for performing custom privilege automation functions. PAM Scripts are user-defined software programs that can be attached to any PAM resource records in the Keeper vault. Depending on the PAM record the script is attached to, the script will execute either on the Keeper Gateway, or the remote host where password rotation occurred. Scripts can also be executed without performing a rotation.

Password Rotation documentation can be found here:
[Password Rotation with Keeper](https://docs.keeper.io/en/secrets-manager/secrets-manager/password-rotation)

Usage of Keeper PAM Scripts can be found here:
[PAM Scripts Documentation](https://docs.keeper.io/en/secrets-manager/secrets-manager/password-rotation/post-rotation-scripts)

For more information about Keeper's products:
- [Enterprise Password Manager](https://www.keepersecurity.com/enterprise.html)
- [Secrets Manager](https://www.keepersecurity.com/secrets-manager.html)
- [Connection Manager](https://www.keepersecurity.com/connection-manager.html)
- [Privilege Access Manager](https://www.keepersecurity.com/privileged-access-management/)

If you need assistance with PAM Scripts, please open a Github issue on this repo or email us at commander@keepersecurity.com.
