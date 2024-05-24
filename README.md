![Django CI](https://github.com/ebridges/elektrum/workflows/elektrum-ci/badge.svg?branch=master)

# Elektrum

## About

The `elektrum` application is a multi-tier system for hosting images and other media designed to be efficient and scalable.  Generally the steps involved in installing it are as follows:

1. Setup Project
1. Establish basic system prerequisites and configure parameters in a global settings file.
1. Configure permissions, a network, storage, security, and distribution mechanisms on AWS.
1. Generate a configuration file that can be used by the application.
1. Deploy the application.

## Platform Information

* Python 3.12
* Django 4.0
* lgw 1.2.*
* PostgreSQL 11
* Ansible 9

## Installation & Deployment

### To Install & Run

* see `INSTALL.md`

### Network Documentation

* see `network/README.md`
* see `network/roles/vpc/README.md`
