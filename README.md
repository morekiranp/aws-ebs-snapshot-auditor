# aws-ebs-snapshot-auditor
Detect and clean up unused EBS snapshots for AWS cost optimization using Python.

# 🧹 AWS Lambda – EBS Snapshot Cleanup Script

## 📖 Overview
This AWS Lambda function automatically identifies and deletes **unused Amazon EBS snapshots** in your AWS account to help reduce storage costs.

The cleanup logic ensures that:
- Snapshots not attached to any volume are deleted.
- Snapshots whose associated volumes no longer exist are deleted.
- Snapshots from volumes that are detached (not attached to any running EC2 instance) are deleted.

This script can be run manually, on a schedule (via CloudWatch Events / EventBridge), or as part of a cost-optimization pipeline.

---

## ⚙️ How It Works

1. The Lambda function connects to the AWS EC2 service using the **boto3** client.
2. It retrieves:
   - All EBS snapshots owned by the account (`describe_snapshots`).
   - All running EC2 instances (`describe_instances` with `instance-state-name=running` filter).
3. It iterates through all snapshots and determines deletion based on:
   - No associated volume → **Delete snapshot**.
   - Associated volume missing → **Delete snapshot**.
   - Associated volume detached (not attached to a running instance) → **Delete snapshot**.
---

## 🧩 Requirements

- Python 3.9+ runtime (compatible with AWS Lambda)
- AWS `boto3` library (pre-installed in AWS Lambda Python runtime)
- AWS IAM role with sufficient EC2 permissions

---

## 🔐 Required IAM Permissions

Attach the following policy to your Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSnapshots",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DeleteSnapshot"
      ],
      "Resource": "*"
    }
  ]
}

