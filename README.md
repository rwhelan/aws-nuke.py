# aws-nuke

## Overview
aws-nuke is a tool for destroying ALL the resources in an AWS Account... Except for a small list of IAM resources.

As the AWS API does not offer a global `delete_all()` method, each service in AWS has to be handled individually.  aws-nuke makes adding services destroyers straightforward by abusing Pythons import system.

## Adding Support For New Services

New services (nukers) are added by creating files in the `/nukes` directory.  Any class that subclasses the `BaseNuker` class will get loaded and its methods called when `list`ing or `nuke`ing from the command line

## Nukers Interface

Every Nuker should have 2 public methods: `list_resources()` and `nuke_resources()` as well as a couple attributes.

### `list_resources()`

This method gets called via the command line option `list` and it should return a Python list of all the resources for that service.  When running the `list` operation, the returned Python list is displayed on the screen for the user to validate all the found resources.

Ideally, the members in the list returned from this method should be in a format that can be consumed by the `nuke_resources()` method.  Doing so would ensure what the user sees on the screen will match what gets destroyed when running a `nuke` operation.

### `nuke_resources()`

This method should destroy ALL the resources for the service.

### Attributes

* `self.name`
  - A `str` that is unique among all the nukers.  It is used for dependency resolution.

* `self.dependencies`
  - A `list` of `str`s that are to be executed before this nuker.  This is helpful to ensure dependent services are cleaned up prior to this.  If any of the dependent nukers are not found or have `enabled = False`, this nuker won't be imported.

* `enabled`
  - A bool used to disable a nuker. (And any nukers that have this one marked as dependent)

* `global_service`
  - A bool used to mark a service as global or spanning regions. Route53, S3, IAM etc.  If marked as global, it will only be imported when the tool is ran with the `global` command line switch