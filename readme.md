# EnderSync Core
EnderSynx Core is the backend infrastructure for synchronizing Minecraft worlds between devices using AWS.

The project is designed around a simple principle: **the device should not need to know how the cloud infrastructure works**. It only needs to upload, download, and identify the latest version of a world.

The initial MVP focuses on reliable world storage and synchronization using Amazon S3, while establishing a foundation that can later support version history, authentication, multiple devices, conflict resolution, and automated synchronization.

## Features

*  Cloud storage for Minecraft worlds
*  World synchronization between devices
*  Compressed world uploads
*  Metadata associated with every world
*  AWS IAM-based access control
*  Structured S3 object organization
*  Designed to evolve toward versioning and multi-device synchronization

##  Architecture

The current MVP uses Amazon S3 as the central storage layer.

```text
                     ┌─────────────────────┐
                     │       Device        │
                     │                     │
                     │  CloudSynx Client   │
                     └──────────┬──────────┘
                                │
                                │ Upload / Download
                                ▼
                     ┌─────────────────────┐
                     │     Amazon S3       │
                     │                     │
                     │  worlds/            │
                     │  └── <world>/       │
                     │      ├── latest.zip │
                     │      └── metadata.json
                     └─────────────────────┘
```

Infrastructure is provisioned using **AWS CloudFormation**, allowing the environment to be recreated without manually configuring resources through the AWS Console.

## 📁 S3 Structure

Worlds are organized using prefixes inside the S3 bucket:

```text
s3://<bucket>/
└── worlds/
    └── <world-id>/
        ├── latest.zip
        └── metadata.json
```

For example:

```text
worlds/
└── survival-world/
    ├── latest.zip
    └── metadata.json
```

### `latest.zip`

Contains the compressed Minecraft world directory.

The world is compressed before being uploaded to reduce transfer size and simplify storage.

### `metadata.json`

Contains information describing the uploaded world.

Example:

```json
{
    "world_id": "survival-world",
    "minecraft_version": "1.21.1",
    "modpack": "Chocolate Edition",
    "uploaded_at": "2026-09-26T23:00:00Z",
    "version": 1
}
```

The metadata is intentionally kept separate from the world archive so that clients can retrieve information about a world without downloading the entire world.

## 🔐 Security

CloudSynx does not store AWS credentials inside the application repository.

Access to AWS resources is controlled through IAM permissions.


##  Infrastructure as Code

CloudSynx uses **AWS CloudFormation** to define its infrastructure.

This allows the project to move from:

```text
Manual AWS Console configuration
```

to:

```text
CloudFormation template
        ↓
AWS Stack
        ↓
Reproducible infrastructure
```

The infrastructure definitions are located in:

```text
infrastructure/
```

CloudFormation is responsible for resources such as:

* S3 bucket
* IAM policies
* IAM roles
* Bucket configuration
* Lifecycle configuration
* Other AWS resources required by the project

AWS-specific configuration and deployment instructions are documented separately in `docs/aws/`.

## 📂 Repository Structure

```text
cloudsynx-core/
│
├── infrastructure/
│   └── cloudformation/
│       └── ...
│
├── src/
│   └── ...
│
├── scripts/
│   └── ...
│
├── docs/
│   ├── architecture/
│   │   └── ...
│   │
│   ├── aws/
│   │   ├── setup.md
│   │   ├── iam.md
│   │   └── s3.md
│   │
│   └── development/
│       └── ...
│
├── tests/
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The repository separates **application code**, **infrastructure**, and **documentation** so that the AWS environment can be understood and reproduced independently from the client implementation.

<!--

##  Getting Started

### Prerequisites

* Python 3.x
* AWS account
* AWS CLI
* Git
* An AWS identity with the required permissions

Verify the AWS CLI installation:

```bash
aws --version
```

Verify your AWS identity:

```bash
aws sts get-caller-identity
```

### 1. Clone the repository

```bash
git clone <repository-url>
cd cloudsynx-core
```

### 2. Create the virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS

Configure the AWS CLI using an appropriate credential provider:

```bash
aws configure
```

Or use another supported AWS authentication method.

### 5. Deploy the infrastructure

CloudSynx infrastructure can be deployed through CloudFormation.

Example:

```bash
aws cloudformation deploy \
    --template-file infrastructure/cloudformation/main.yaml \
    --stack-name cloudsynx-core \
    --capabilities CAPABILITY_NAMED_IAM
```

The exact deployment parameters are documented in:

```text
docs/aws/setup.md
```

## 🔄 MVP1 Workflow

The first version of CloudSynx focuses on a straightforward synchronization flow.

### Upload

```text
Minecraft World
      │
      ▼
Compress world
      │
      ▼
Create metadata.json
      │
      ▼
Upload to S3
      │
      ├── latest.zip
      └── metadata.json
```

### Download

```text
S3
 │
 ├── metadata.json
 │
 └── latest.zip
        │
        ▼
    Download
        │
        ▼
    Extract world
        │
        ▼
Minecraft
```

The client is responsible for preparing the world and metadata, while S3 acts as the durable cloud storage layer.

## 🧩 Design Goals

CloudSynx Core is being developed with the following principles:

### Reproducibility

Infrastructure should be possible to recreate without manually clicking through the AWS Console.

### Minimal permissions

AWS identities should receive only the permissions required for their specific operation.

### Clear separation of responsibilities

The client should handle world preparation and synchronization logic, while AWS provides the underlying infrastructure and storage.

### Extensibility

The MVP should provide a foundation for future capabilities without prematurely introducing unnecessary infrastructure.

## 🛣️ Roadmap

### MVP1

* [x] S3-based world storage
* [x] World archive format
* [x] World metadata
* [x] Basic upload/download flow
* [ ] CloudFormation infrastructure
* [ ] IAM permission model
* [ ] Client implementation
* [ ] End-to-end synchronization test

### MVP2

* [ ] World version history
* [ ] Device identification
* [ ] Synchronization state
* [ ] Safer update workflow
* [ ] Conflict detection

### Future

* [ ] Multiple worlds per account
* [ ] Multi-device synchronization
* [ ] Automatic backups
* [ ] World restoration
* [ ] Authentication and authorization layer
* [ ] Event-driven synchronization
* [ ] Web/mobile management interface

## 📚 Documentation

Detailed documentation is organized under `docs/`.

```text
docs/
├── architecture/
├── aws/
└── development/
```

The documentation covers:

* System architecture
* AWS resource configuration
* IAM permissions
* S3 structure
* CloudFormation deployment
* Development setup
* Synchronization workflow
* Design decisions

-->

##  Project Status

CloudSynx Core is currently under active development.

The current implementation represents the **MVPq stage**, so APIs, infrastructure, and storage conventions may change as synchronization requirements evolve.

##  License

This project is currently not licensed for redistribution.

See the repository for the current project terms.
