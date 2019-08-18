#  Mock EC2 Metadata

##  Intended Use

This is a simple Flask based service running in a Docker container that imitates the AWS EC2 Metadata service.  It is useful for local development images outside of AWS that require the ability to assume an IAM role or permissions.  It is currently used for developing and testing custom AMIs locally in Vagrant, where the software stack is required to interact with AWS services and needs an IAM role to do so.


##  IAM Configuration

The Mock EC2 Metadata service will use an [AWS Credential Profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) on your Docker host, and use those credentials to assume a role.  This means that you are able to assume the same IAM role that is configured as the Instance Profile in AWS, making for meaningful testing.

The default AWS Credential location (`~/.aws/`) is bind mounted into the Docker container to be available in the running container.

The source IAM profile as configured in `~/.aws/credentials` and the ARN of the IAM role to be assumed are configured in the yaml configuration file.  (Details in the Installation section)


##  Installation

This application can be run in at least three different manners:

1. As a Docker container on your host machine.
2. As a Docker container inside your Vagrant image.
3. As a native python application inside a virtualenv in your Vagrant image.

The instructions here are for the first method:  It has the least interaction with your Vagrant image of the three methods.

Install it as follows:

1. Clone this repo to your Docker host.
2. The configuration is managed in `conf/config.yaml`.  Copy `conf/sample-config.yaml` to `conf/config.yaml` and edit according to your requirements.  (`conf/config.yaml` is excluded from the git repo)
3. Make the helper shell scripts executable.
  ```
  chmod +x *.sh
  ```
4.  Build the docker image with:
  ```
  ./build-docker.sh
  ```


##  Usage

Run the docker image with:
  ```
  ./run-docker.sh <environment>
  ```
The `run-docker.sh` script takes an argument of either `dev` or `prd`:

- `dev`
  - Will run the docker container interactively.
  - Flask will run in debug mode, printing all output to STDOUT, useful for troubleshooting.
  - This repo will be bind mounted into the container at `/app` for easy editing.
- `prd`
  - Will run the docker container detached.
  - Access logs will be output to the container's STDOUT, and available with the `docker logs` command.

The container has port TCP/5000 published to 0.0.0.0:5000 on the Docker host.

It can be tested with `curl http://localhost:5000/status` from the Docker host.


##  Networking

The networking aspect is configured as follows:

- The mock-ec2-metadata service is listens on 0.0.0.0:5000 on the Docker host.
- The Vagrant/VirtualBox image can reach this via its default gateway, also on port TCP/5000.  (This assumes the default Vagrant networking configuration.  NAT mode for VirtualBox)
- An IPTables NAT rule is added to redirect requests made to 169.254.169.254 on TCP/80 to the default gateway, port TCP/5000
- This NAT rule is configured in a simple shell script, `nat.sh`, which is configured in the provided example Vagrantfile as a provisioning script, to be run every time the Vagrant image is booted up, or the provisioners run.


##  Credential caching

The temporary credentials returned by `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>` are cached in Flask for one hour.


##  Metadata service timeout

Should you find your app or sdk is timing out before obtaining temporary credentials from the mock ec2 metadata service, you can increase the default timeout of 1 sec.

```
export AWS_METADATA_SERVICE_TIMEOUT=5
export AWS_METADATA_SERVICE_NUM_ATTEMPTS=2
```

##  Endpoints

The following metadata endpoints are configured:

- http://169.254.169.254/latest/meta-data/hostname
- http://169.254.169.254/latest/meta-data/instance-id
- http://169.254.169.254/latest/meta-data/instance-type
- http://169.254.169.254/latest/meta-data/local-ipv4
- http://169.254.169.254/latest/meta-data/placement/availability-zone
- http://169.254.169.254/latest/meta-data/iam/security-credentials
- http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
- http://169.254.169.254/latest/dynamic/instance-identity/document
