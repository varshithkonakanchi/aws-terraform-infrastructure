\## Part 1 Infrastructure Provisioning



This project demonstrates the design and automated provisioning of a secure, multi-tier AWS infrastructure using \*\*Terraform (Infrastructure as Code)\*\*.



The objective was to build an environment where:



\- Internet traffic enters through an Application Load Balancer.

\- Application servers run on private EC2 instances.

\- The database is isolated from the public internet.

\- Security Groups control communication between infrastructure layers.

\- Terraform state is centrally stored in Amazon S3.

\- Infrastructure can be consistently created, modified, and destroyed using Terraform.



The project demonstrates practical knowledge of \*\*AWS networking, Terraform, Infrastructure as Code, security, load balancing, Linux, and cloud infrastructure management\*\*.



\---



\# Architecture



```text

&#x20;                             Internet

&#x20;                                 |

&#x20;                                 |

&#x20;                                 v

&#x20;                        Internet Gateway

&#x20;                                 |

&#x20;                                 |

&#x20;                    +------------+------------+

&#x20;                    |                         |

&#x20;                    |     Public Subnets      |

&#x20;                    |                         |

&#x20;                    |  Application Load       |

&#x20;                    |      Balancer           | 

&#x20;                    +------------+------------+

&#x20;                                 |

&#x20;                          HTTP Port 80

&#x20;                                 |

&#x20;                   +-------------+-------------+

&#x20;                   |                           |

&#x20;                   v                           v

&#x20;             EC2 Instance 1              EC2 Instance 2

&#x20;             Private Subnet              Private Subnet

&#x20;                   |                           |

&#x20;                   +-------------+-------------+

&#x20;                                 |

&#x20;                         PostgreSQL 5432

&#x20;                                 |

&#x20;                                 v

&#x20;                        Amazon RDS PostgreSQL

&#x20;                         Private DB Subnets





Private EC2 Instances

&#x20;       |

&#x20;       v

&#x20;  NAT Gateway

&#x20;       |

&#x20;       v

Internet Gateway

&#x20;       |

&#x20;       v

Internet

```



The infrastructure is distributed across \*\*two Availability Zones\*\* to provide better availability for the application layer.



\---



\# AWS Services Used



| AWS Service | Purpose |

|---|---|

| Amazon VPC | Provides isolated networking for the environment |

| Public Subnets| Private Subnets| DB Subnets | Provide isolated networking for RDS |

| Internet Gateway | Provides internet connectivity to public resources |

| NAT Gateway | Provides outbound internet access to private EC2 instances |

| Amazon EC2 | Hosts the Nginx application |

| Application Load Balancer | Distributes incoming HTTP requests |

| Amazon RDS | Provides managed PostgreSQL database |

| Security Groups | Control network communication between infrastructure layers |

| Amazon S3 | Stores Terraform remote state |



\---



\# Network Design



The VPC uses the following CIDR:



```

10.0.0.0/16

```



Subnet allocation:



| Network | CIDR | Purpose |

|---|---|---|

| Public Subnet 1 | `10.0.1.0/24` | ALB / NAT Gateway |

| Public Subnet 2 | `10.0.2.0/24` | ALB |

| Private App Subnet 1 | `10.0.11.0/24` | EC2 Application Server |

| Private App Subnet 2 | `10.0.12.0/24` | EC2 Application Server |

| Private DB Subnet 1 | `10.0.21.0/24` | RDS |

| Private DB Subnet 2 | `10.0.22.0/24` | RDS |



The public and application subnets are distributed across two Availability Zones.



\---



\# Request Flow



Application traffic follows this path:



```text

User

&#x20;|

&#x20;| HTTP : 80

&#x20;v

Application Load Balancer

&#x20;|

&#x20;| HTTP : 80

&#x20;v

EC2 Application Servers

&#x20;|

&#x20;| PostgreSQL : 5432

&#x20;v

Amazon RDS PostgreSQL

```



The user does not directly communicate with either the EC2 instances or the database.



The Application Load Balancer acts as the public entry point.



\---



\# Security Design



Security was implemented using separate Security Groups for each infrastructure layer.



\## ALB Security Group



Allows incoming:



```text

TCP 80

Source: 0.0.0.0/0

```



This allows users to access the application through the public Application Load Balancer.



\---



\## Application Security Group



Allows:



```text

TCP 80

Source: ALB Security Group

```



The EC2 instances therefore do not accept application traffic directly from the internet.



Only traffic originating from the Application Load Balancer is permitted.



\---



\## Database Security Group



Allows:



```text

TCP 5432

Source: Application Security Group

```



The PostgreSQL database can only be reached by resources associated with the application Security Group.



RDS is configured as:



```text

Publicly Accessible: False

```



This prevents direct database access from the internet.



\---



\# Private EC2 Internet Access



The EC2 application instances are deployed inside private subnets.



They do not require public IP addresses for normal application access.



A \*\*NAT Gateway\*\* provides outbound internet connectivity so the instances can perform operations such as:



```text

Package installation

Operating system updates

External repository access

```



The traffic path is:



```text

Private EC2

&#x20;   |

&#x20;   v

NAT Gateway

&#x20;   |

&#x20;   v

Internet Gateway

&#x20;   |

&#x20;   v

Internet

```



The internet cannot initiate connections through the NAT Gateway back to the private EC2 instances.



\---



\# Application Layer



Two EC2 instances are provisioned using Terraform.



During instance initialization, Terraform provides a `user-data.sh` bootstrap script.



The script:



1\. Updates the operating system packages.

2\. Installs Nginx.

3\. Enables the Nginx service.

4\. Starts Nginx.

5\. Retrieves the EC2 instance ID using EC2 Instance Metadata Service.

6\. Generates a simple HTML page.



The application displays:



```text

Application deployed successfully

Provisioned using Terraform

Instance ID: <instance-id>

```



Displaying the instance ID makes it possible to demonstrate that requests can reach different backend instances through the Application Load Balancer.



\---



\# Load Balancing



An AWS \*\*Application Load Balancer (ALB)\*\* provides the public entry point for the application.



The ALB spans both public subnets.



Two EC2 instances are registered with an ALB Target Group.



```text

&#x20;                   ALB

&#x20;                    |

&#x20;            +-------+-------+

&#x20;            |               |

&#x20;            v               v

&#x20;         EC2-1            EC2-2

```



The Target Group performs HTTP health checks against:



```text

/

```



Only healthy instances receive application traffic.



\---



\# Database Layer



The database layer uses \*\*Amazon RDS for PostgreSQL\*\*.



Configuration includes:



```text

Engine             : PostgreSQL

Instance Class     : db.t3.micro

Storage            : 20 GB GP3

Storage Encryption : Enabled

Public Access      : Disabled

Backup Retention   : 7 Days

Port               : 5432

```



The RDS instance is associated with a DB subnet group containing the two private database subnets.



Database access is restricted to the application Security Group.



\---



\# Terraform Remote State



Instead of relying only on local Terraform state, this project uses an \*\*Amazon S3 remote backend\*\*.



```text

Terraform

&#x20;   |

&#x20;   v

Amazon S3

&#x20;   |

&#x20;   v

terraform.tfstate

```



The S3 backend provides centralized state storage.



S3 versioning is enabled to maintain previous versions of the Terraform state.



Terraform S3 state locking is also enabled to help prevent concurrent Terraform operations from modifying the state simultaneously.



Sensitive Terraform state files are excluded from Git.



\---



\# Project Structure



```text

aws\_terraform\_project/

│

├── .gitignore

├── .terraform.lock.hcl

├── backend.tf

├── main.tf

├── outputs.tf

├── README.md

├── terraform.tfvars.example

├── user-data.sh

├── variables.tf

└── versions.tf

```



\## File Responsibilities



\### `main.tf`



Contains the main AWS infrastructure resources:



\- VPC

\- Subnets

\- Internet Gateway

\- NAT Gateway

\- Route Tables

\- Security Groups

\- EC2 Instances

\- Application Load Balancer

\- Target Group

\- ALB Listener

\- RDS PostgreSQL



\### `variables.tf`



Defines configurable Terraform input variables including:



\- AWS Region

\- AWS Profile

\- Project Name

\- Environment

\- VPC CIDR

\- Subnet CIDRs

\- EC2 Instance Type

\- RDS Instance Class

\- Database Configuration



\### `outputs.tf`



Returns important information after deployment:



\- VPC ID

\- Public Subnet IDs

\- Private Subnet IDs

\- Database Subnet IDs

\- EC2 Instance IDs

\- ALB DNS Name

\- RDS Endpoint

\- RDS Port



\### `backend.tf`



Configures the Amazon S3 remote Terraform backend.



\### `versions.tf`



Defines:



\- Required Terraform version

\- AWS provider version

\- AWS provider configuration

\- Default resource tags



\### `user-data.sh`



Bootstraps the EC2 application servers and configures Nginx.



\### `terraform.tfvars.example`



Provides an example configuration without exposing actual credentials or passwords.



\---



\# Prerequisites



Before deploying the project, the following are required:



\- AWS Account

\- AWS CLI

\- Terraform

\- Git

\- Configured AWS CLI profile



Verify:



```bash

aws --version

terraform --version

git --version

```



AWS authentication can be verified using:



```bash

aws sts get-caller-identity --profile <profile-name>

```



\---



\# Deployment



\## 1. Clone Repository



```bash

git clone <repository-url>

cd aws-terraform-infrastructure

```



\## 2. Configure Variables



Copy:



```text

terraform.tfvars.example

```



to:



```text

terraform.tfvars

```



Configure the required values locally.



`terraform.tfvars` is intentionally excluded from Git.



\---



\## 3. Initialize Terraform



```bash

terraform init

```



This initializes the AWS provider and S3 backend.



\---



\## 4. Format Terraform



```bash

terraform fmt

```



\---



\## 5. Validate Configuration



```bash

terraform validate

```



Expected result:



```text

Success! The configuration is valid.

```



\---



\## 6. Review Deployment Plan



```bash

terraform plan -out=tfplan

```



Terraform displays the infrastructure resources that will be created.



\---



\## 7. Deploy Infrastructure



```bash

terraform apply tfplan

```



Terraform automatically provisions the AWS environment.



\---



\# Testing



After deployment, retrieve the outputs:



```bash

terraform output

```



Retrieve the ALB DNS name:



```bash

terraform output -raw load\_balancer\_dns

```



The application can then be accessed using:



```text

http://<ALB-DNS-NAME>

```



PowerShell can also be used to verify the endpoint:



```powershell

$ALB = terraform output -raw load\_balancer\_dns

Invoke-WebRequest "http://$ALB" -UseBasicParsing

```



A successful request returns:



```text

StatusCode : 200

```



The browser displays:



```text

Application deployed successfully

Provisioned using Terraform

Instance ID: <EC2-instance-id>

```



\---



\# Infrastructure Validation



Terraform-managed resources can be verified using:



```bash

terraform state list

```



The ALB target health can also be verified using AWS CLI:



```bash

aws elbv2 describe-target-health \\

&#x20; --target-group-arn <TARGET-GROUP-ARN>

```



Both application instances should report:



```text

healthy

```



\---



\# Destroying the Environment



The environment contains AWS resources that can incur charges, particularly:



\- NAT Gateway

\- Application Load Balancer

\- EC2

\- RDS



When the environment is no longer required:



```bash

terraform destroy

```



Review the Terraform destruction plan before confirming.



\---



\# Security Considerations



This implementation includes several security controls:



\- EC2 instances deployed in private subnets

\- RDS deployed in private database subnets

\- RDS public access disabled

\- Security Group-to-Security Group access controls

\- Database traffic restricted to port 5432

\- Application traffic restricted through the ALB

\- RDS storage encryption enabled

\- Remote Terraform state stored in S3

\- S3 state versioning enabled

\- Terraform state locking enabled

\- Sensitive variable files excluded from Git

\- Terraform state files excluded from Git

\- AWS credentials excluded from the repository



For a production environment, additional improvements could include:



\- HTTPS using AWS Certificate Manager

\- AWS WAF in front of the ALB

\- AWS Secrets Manager for database credentials

\- Multi-AZ RDS

\- Auto Scaling Groups

\- VPC Flow Logs

\- CloudWatch monitoring and alarms

\- AWS Systems Manager for private instance administration

\- Multiple NAT Gateways for Availability Zone-level resilience



\---



\# Key Design Decisions



\### Why are EC2 instances private?



Application servers do not need to be directly exposed to the internet because all user traffic enters through the Application Load Balancer.



\### Why use a NAT Gateway?



Private EC2 instances require outbound internet connectivity for package installation and operating system updates while remaining inaccessible directly from the internet.



\### Why use separate database subnets?



Separating the database tier provides additional network isolation and keeps RDS away from public-facing resources.



\### Why use Security Group references?



Referencing Security Groups instead of allowing broad CIDR ranges provides tighter control between the ALB, application, and database layers.



\### Why use remote Terraform state?



Remote state provides centralized state management and makes the infrastructure easier to manage consistently compared with relying only on a local state file.



\---



\# Possible Production Improvements



The current environment is designed as a demonstration project.



For a production deployment, I would extend the architecture with:



```text

Route 53

&#x20;   |

&#x20;   v

AWS WAF

&#x20;   |

&#x20;   v

HTTPS ALB + ACM Certificate

&#x20;   |

&#x20;   v

Auto Scaling Group

&#x20;   |

&#x20;   v

Private EC2 Instances

&#x20;   |

&#x20;   v

Multi-AZ RDS PostgreSQL

```



Monitoring could also be implemented using CloudWatch metrics, logs, dashboards, and alarms.



Database credentials should be moved from Terraform variables to AWS Secrets Manager or RDS-managed master credentials.



\---



\# Skills Demonstrated



This project demonstrates practical experience with:



\- Infrastructure as Code

\- Terraform

\- AWS Networking

\- VPC Architecture

\- Public and Private Subnets

\- Route Tables

\- Internet and NAT Gateways

\- Amazon EC2

\- Application Load Balancers

\- Amazon RDS PostgreSQL

\- AWS Security Groups

\- Linux / Nginx

\- Terraform Remote State

\- Amazon S3

\- AWS CLI

\- Git / GitHub

\- Cloud Security Fundamentals



\---



Part 2 - Deployment Automation (CI/CD)

GitHub Actions • Docker • AWS EC2 • Security Scanning • Manual Approval • Slack Alerts

Project: AWS Terraform Infrastructure / DevOps Assignment

This document explains the completed CI/CD implementation for Part 2 of the DevOps technical assignment. The solution automates pull-request validation, Docker image creation and publishing, vulnerability scanning, staging deployment, manual production approval, production deployment, health checks, and Slack failure notifications.

CI/CD platform

GitHub Actions

Container registry

Docker Hub

Deployment target

AWS EC2

Application

Python Flask

Security scans

pip-audit and Trivy

Notifications

Slack Incoming Webhook


CI/CD Implementation Documentation

8Byte.ai DevOps Technical Assignment | Part 2 - Deployment Automation

1. Overview

The CI/CD solution is implemented using GitHub Actions. It validates changes before merge, builds and publishes container images after merge to main, performs security scanning, automatically deploys the application to staging, pauses for manual approval before production, and sends Slack alerts when failures occur.

Run tests automatically when a pull request targets the main branch.

Run both unit and integration tests with Pytest.

Scan Python dependencies for known vulnerabilities using pip-audit.

Build a Docker image and push it to Docker Hub after a merge/push to main.

Tag images with both latest and the exact Git commit SHA for traceability.

Scan container images with Trivy before deployment.

Deploy the commit-specific image automatically to an AWS EC2 staging container.

Run a health check after staging deployment.

Require a manual reviewer approval before production deployment.

Deploy the same commit-specific image to production after approval.

Send Slack notifications when tests, security scans, builds, or deployments fail.

2. CI/CD Architecture

Developer / Feature Branch
        |
        v
Pull Request to main
        |
        v
PR Tests + pip-audit
        |
        v
Unit + Integration Tests
        |
        v
Merge to main
        |
        v
Docker Build + Push to Docker Hub
        |
        v
Trivy Container Scan
        |
        v
Automatic Staging Deployment (AWS EC2 :5000)
        |
        v
Staging Health Check
        |
        v
Manual Production Approval (GitHub Environment)
        |
        v
Production Deployment (AWS EC2 :5001)
        |
        v
Production Health Check

Any failed stage -> Slack #ci-cd-alerts notification

Cost-conscious demo design: staging and production are logically separated as different Docker containers and ports on the same temporary EC2 host. For a real production environment, staging and production should normally be isolated on separate infrastructure.

3. GitHub Actions Workflows

The workflow definitions are stored in the repository under:

.github/workflows/
├── pr-tests.yml
└── docker-build.yml

4. Pull Request Validation Workflow

Workflow file: .github/workflows/pr-tests.yml

The PR workflow runs whenever a pull request is opened or updated against the main branch. Its purpose is to prevent untested or vulnerable application changes from being merged.

Checkout the repository.

Set up Python 3.14 on the GitHub-hosted runner.

Install application dependencies from app/requirements.txt.

Run pip-audit against the Python dependency list.

Run unit and integration tests using pytest -v.

If a step fails, post a failure message to Slack.

4.1 Unit and Integration Tests

Application tests are stored under:

app/tests/
├── test_app.py
└── test_integration.py

The unit tests validate the home, health, and version endpoints. The integration test starts the Flask application as a real process and verifies the /health endpoint over HTTP. The validated test suite currently contains four tests.

test_home PASSED
test_health PASSED
test_version PASSED
test_running_application PASSED

4 passed

4.2 Dependency Vulnerability Scanning

Python dependencies are scanned with pip-audit. The scan checks packages in app/requirements.txt against known vulnerability data. A detected vulnerability can fail the PR job and prevent the change from being merged until it is reviewed or remediated.

pip-audit -r requirements.txt

5. Docker Build and Registry Publishing

Workflow file: .github/workflows/docker-build.yml

The main deployment workflow runs on pushes to the main branch, including pull-request merges. GitHub Actions authenticates to Docker Hub through repository secrets, builds the application image, and publishes it to the Docker registry.

Docker Hub repository:

cybercreeper/8byte-devops-app

Each successful build publishes two tags:

latest - convenient pointer to the newest successful build.

<git-commit-sha> - immutable deployment reference tied to the exact source commit.

Traceability benefit: staging and production deploy the commit-SHA tag instead of relying only on latest, so the deployed container can be mapped directly to a Git commit.

6. Container Vulnerability Scanning

After the Docker image is built and pushed, Trivy scans the commit-specific image. The workflow scans operating-system packages and application libraries and is configured to fail when a CRITICAL vulnerability is detected.

Scanner: Trivy (Aqua Security).

Target: cybercreeper/8byte-devops-app:<git-commit-sha>.

Scope: OS packages and application libraries.

Severity gate: CRITICAL.

Unfixed issues are ignored in the current demo configuration.

A failed scan prevents the dependent staging deployment job from running.

7. Automated Staging Deployment

The staging job depends on the successful build-and-push job. GitHub Actions reconstructs a temporary ED25519 SSH key from a Base64-encoded repository secret, connects to the staging EC2 host with native SSH, and deploys the exact commit-specific Docker image.

GitHub Actions
      |
      v
Decode temporary ED25519 key
      |
      v
SSH to AWS EC2
      |
      v
Pull commit-SHA Docker image
      |
      v
Stop/remove previous staging container
      |
      v
Start 8byte-staging-app on host port 5000
      |
      v
GET /health

Staging container name: 8byte-staging-app

Staging host port: 5000

Restart policy: unless-stopped

7.1 Staging Health Check

After deployment, the workflow validates the application locally on the EC2 host:

curl --fail --retry 5 --retry-delay 2 http://localhost:5000/health

Expected response:

{"status":"healthy"}

8. Manual Production Approval

Production deployment is protected by a GitHub Environment named production. Required reviewers are enabled for this environment. The deploy-production job references that environment, so GitHub pauses the workflow after staging until a reviewer explicitly approves the deployment.

Build + Security Scan   [PASS]
          |
          v
Staging Deployment      [PASS]
          |
          v
Staging Health Check    [PASS]
          |
          v
Production Environment  [WAITING FOR REVIEW]
          |
          v
Manual Approve and Deploy
          |
          v
Production Deployment

Key control: production cannot proceed automatically unless the configured reviewer approves the pending deployment.

9. Production Deployment

After approval, GitHub Actions deploys the same commit-specific image to a separate production Docker container. The demo uses a different container name and host port to keep staging and production logically separated while using one temporary EC2 instance.

Production container name: 8byte-production-app

Production host port: 5001

9.1 Production Health Check

The production deployment is validated after the container starts:

curl --fail --retry 5 --retry-delay 2 http://localhost:5001/health

Expected response:

{"status":"healthy"}

10. Slack Failure Notifications

A Slack Incoming Webhook is integrated with both CI workflows. Notifications are posted to the #ci-cd-alerts channel only when a failure occurs.

Slack workspace: 8Byte DevOps

Channel: #ci-cd-alerts

Alerts cover failures in:

PR validation and tests.

Python dependency vulnerability scanning.

Docker login/build/push.

Trivy image scanning.

Staging deployment and health check.

Production deployment and health check.

Notification steps use the GitHub Actions condition:

if: failure()

A temporary test branch intentionally executed exit 1 to verify the integration. The PR failed as expected and Slack received an alert containing the repository, branch, and GitHub Actions run link. The test PR was then closed and the temporary branch was deleted without being merged.

11. GitHub Secrets and Credential Handling

Sensitive values are stored as GitHub repository secrets instead of being written directly in workflow files or committed to Git.

Secret Name

Purpose

DOCKERHUB_USERNAME

Docker Hub account used by GitHub Actions.

DOCKERHUB_TOKEN

Docker Hub personal access token used to push images.

EC2_HOST

EC2 deployment target hostname or public IP.

EC2_USER

SSH username used for deployment.

EC2_SSH_KEY_B64

Base64-encoded ED25519 private deployment key.

SLACK_WEBHOOK_URL

Slack Incoming Webhook used for failure notifications.

Important: secret values, SSH private keys, access tokens, and webhook URLs are not included in repository documentation.

12. Failure Handling

1.  A failing PR test or dependency scan marks the PR check as failed.

2.  A failing Docker build or Trivy scan marks build-and-push as failed.

3.  Dependent deployment jobs do not proceed when an upstream job fails.

4.  A staging health-check failure marks the staging job as failed.

5.  Production remains protected behind the manual approval gate.

6.  Slack receives a failure notification with a direct link to the relevant GitHub Actions run.

7.  The failed run can be investigated from the GitHub Actions logs before a corrected change is retried.

13. Technology Summary

Component

Technology

CI/CD

GitHub Actions

Application

Python Flask

Testing

Pytest

Dependency scanning

pip-audit

Containerization

Docker

Registry

Docker Hub

Container scanning

Trivy

Staging deployment

AWS EC2 + Docker

Production deployment

AWS EC2 + Docker

Remote deployment

Native SSH with ED25519 key

Approval gate

GitHub Environments / Required reviewers

Failure notifications

Slack Incoming Webhook

14. Part 2 Completion Status

Requirement

Status

PR-triggered automated tests

Completed

Unit tests

Completed

Integration tests

Completed

Docker build on merge/push to main

Completed

Docker Hub image publishing

Completed

Dependency vulnerability scan

Completed

Container vulnerability scan

Completed

Automatic staging deployment

Completed

Staging health check

Completed

Manual production approval

Completed

Production deployment

Completed

Production health check

Completed

Slack failure notifications

Completed

15. Design Decisions and Production Improvements

The implementation prioritizes an end-to-end working deployment path for the technical assignment while keeping cloud cost low. The following improvements would be recommended before using the same pattern for a real production service:

Use separate AWS infrastructure for staging and production instead of two containers on one host.

Place the application behind an Application Load Balancer and terminate TLS/HTTPS at the load balancer.

Avoid leaving SSH open to the public internet; prefer AWS Systems Manager Session Manager or tightly controlled network access.

Use a fixed DNS name or deployment target instead of relying on a temporary public EC2 IP.

Use environment-specific GitHub secrets and least-privilege credentials.

Introduce image retention rules, rollback automation, and deployment version history.

Use pinned application dependency versions for stronger build reproducibility.

Add broader security-policy gates for HIGH findings after defining an accepted vulnerability policy.

Result: Part 2 demonstrates a complete CI/CD lifecycle from pull request validation through secure image publishing, staging deployment, controlled production release, health verification, and operational failure notification.



DevOps | Cloud | Cybersecurity

