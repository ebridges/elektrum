### Run Server in Debug Mode ###

```
    {
      "name": "Elektron Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/project/manage.py",
      "console": "integratedTerminal",
      "args": [
        "runserver",
        "--noreload",
        "--nothreading"
      ],
      "django": true,
      "envFile": "etc/test.env",
      "cwd": "${workspaceFolder}/project"
    }
```

### Run a Single Unit Test ###

```
    {
      "name": "Elektron Debug: Test",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/project/manage.py",
      "console": "integratedTerminal",
      "args": [
        "test",
        "users.tests.test_authn_user_flows"
      ],
      "django": true,
      "envFile": "etc/test.env",
      "cwd": "${workspaceFolder}/project"
    },
```
