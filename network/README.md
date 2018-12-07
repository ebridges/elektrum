### Installing & Configuring Elektron Network

These scripts configure a VPC network and a database instance on AWS for use by the Elektron app.

#### Usage

* Place the Ansible vault passphrase in a file named `vault-password.txt` in this directory. Password should be by itself on one line.
* Execute `run.sh` to run the playbook in order to configure the network components.
