### Installing & Configuring Elektron Network

These scripts configure a VPC network, a database instance, a load balancer, and an auto scaling container cluster on AWS for use by the Elektron app.

To run:

* Place the Ansible vault passphrase in a file named `vault-password.txt` in this directory. Password should be by itself on one line.
* Execute `setup.sh` to install the `ecs-cluster` Ansible Galaxy module.
* Execute `run.sh` to run the playbook in order to configure the network components.
