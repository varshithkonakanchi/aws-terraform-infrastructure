\## Project Overview



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



\# Author



\*\*Varshith Sai Konakanchi\*\*



DevOps | Cloud | Cybersecurity

