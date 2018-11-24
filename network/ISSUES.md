# Known Issues

## Error when running `ecs-cluster` for the first time

### Message

`error while evaluating conditional ((ec2_lc_existing | length) > 0): 'ec2_lc_existing' is undefined`

```
TASK [ecs-cluster : Local | Of AMI matching Launch Configs select one that also matches instance type] ************************************************************************
fatal: [localhost]: FAILED! => {"msg": "The conditional check '(ec2_lc_existing | length) > 0' failed. The error was: error while evaluating conditional ((ec2_lc_existing | length) > 0): 'ec2_lc_existing' is undefined\n\nThe error appears to have been in '/Users/ebridges/Documents/elektron-working/elektron/network/roles/ecs-cluster/tasks/main.yml': line 59, column 5, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\n  - name: \"Local | Of AMI matching Launch Configs select one that also matches instance type\"\n    ^ here\n"}
```

### Cause

The variable `ec2_lc_existing` is left undefined if there are no pre-registered AMIs, as would happen on first run of these scripts.

### Workaround

Add this right after the above task, at line 59 or so:

```
  - name: "Local | Initialize variable to null if no AMI IDs match."
    set_fact:
      ec2_lc_existing: {}
    when: (ec2_lc_list.launch_configurations | length) == 0
```


## IAM Error When Running `ecs-cluster` role

### Message

`TypeError: '<' not supported between instances of 'dict' and 'dict'`

```
TASK [ecs-cluster : AWS | IAM | Create IAM role needed for cluster EC2 instances access to AWS EC2 services] ******************************************************************
task path: /Users/ebridges/Documents/elektron-working/elektron/network/roles/ecs-cluster/tasks/main.yml:18
An exception occurred during task execution. To see the full traceback, use -vvv. The error was: TypeError: '<' not supported between instances of 'dict' and 'dict'
fatal: [localhost]: FAILED! => {"changed": false, "module_stderr": "Traceback (most recent call last):\n  File \"/Users/ebridges/.ansible/tmp/ansible-tmp-1542996970.597159-27420721105465/AnsiballZ_iam_role.py\", line 113, in <module>\n    _ansiballz_main()\n  File \"/Users/ebridges/.ansible/tmp/ansible-tmp-1542996970.597159-27420721105465/AnsiballZ_iam_role.py\", line 105, in _ansiballz_main\n    invoke_module(zipped_mod, temp_path, ANSIBALLZ_PARAMS)\n  File \"/Users/ebridges/.ansible/tmp/ansible-tmp-1542996970.597159-27420721105465/AnsiballZ_iam_role.py\", line 48, in invoke_module\n    imp.load_module('__main__', mod, module, MOD_DESC)\n  File \"/Users/ebridges/.virtualenvs/network-IZyr3MhR/lib/python3.6/imp.py\", line 235, in load_module\n    return load_source(name, filename, file)\n  File \"/Users/ebridges/.virtualenvs/network-IZyr3MhR/lib/python3.6/imp.py\", line 170, in load_source\n    module = _exec(spec, sys.modules[name])\n  File \"<frozen importlib._bootstrap>\", line 618, in _exec\n  File \"<frozen importlib._bootstrap_external>\", line 678, in exec_module\n  File \"<frozen importlib._bootstrap>\", line 219, in _call_with_frames_removed\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/__main__.py\", line 516, in <module>\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/__main__.py\", line 510, in main\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/__main__.py\", line 267, in create_or_update_role\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/__main__.py\", line 176, in compare_assume_role_policy_doc\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/ansible_iam_role_payload.zip/ansible/module_utils/ec2.py\", line 647, in sort_json_policy_dict\n  File \"/var/folders/dp/9r2sg2kj0771py71lvbf3bb00000gn/T/ansible_iam_role_payload_qnfog3j7/ansible_iam_role_payload.zip/ansible/module_utils/ec2.py\", line 639, in value_is_list\nTypeError: '<' not supported between instances of 'dict' and 'dict'\n", "module_stdout": "", "msg": "MODULE FAILURE\nSee stdout/stderr for the exact error", "rc": 1}
```

### Cause

When setting up the service in the `svc` role, an additional policy is appended to the role defined in `ecs_instance_iam_role`, and an additional entity needs to be added to the trust relationships. The task in `ecs-cluster` role does not support merging multiple policies on the role.

### Workaround

Manually add the following to the `elektronService-ecsInstanceRole` role:

* Attach the `AmazonEC2ContainerServiceRole` policy under the "Permissions" tab.
* Edit the Trust Relationships to add an additional statement.  The whole policy should look like this:
  ```
  {
    "Version": "2008-10-17",
    "Statement": [
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      },
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  ```