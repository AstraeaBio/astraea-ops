# GCP VM Access

## Overview

Troubleshooting guide for accessing Google Cloud Platform virtual machines.

## Symptoms

- Unable to SSH into GCP VM
- IAP tunnel connection failures
- Permission denied errors when accessing VMs
- VMs not appearing in console or CLI

## Common Causes

1. **Insufficient IAM permissions**: Missing required roles for VM access
2. **Network/firewall rules blocking access**: VPC firewall rules may be too restrictive
3. **VM not running**: Instance may be stopped or terminated
4. **IAP not properly configured**: Identity-Aware Proxy may need configuration

## Solutions

### Solution 1: Verify IAM Permissions

Ensure you have the required roles:

- `roles/compute.osLogin` or `roles/compute.osAdminLogin`
- `roles/iap.tunnelResourceAccessor` (for IAP access)

Check permissions via CLI:

```bash
gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:user:YOUR_EMAIL"
```

### Solution 2: Use IAP Tunneling

Connect using Identity-Aware Proxy:

```bash
gcloud compute ssh INSTANCE_NAME --zone=ZONE --tunnel-through-iap
```

### Solution 3: Check VM Status

Verify the VM is running:

```bash
gcloud compute instances list --filter="name=INSTANCE_NAME"
gcloud compute instances describe INSTANCE_NAME --zone=ZONE
```

Start the VM if stopped:

```bash
gcloud compute instances start INSTANCE_NAME --zone=ZONE
```

## Prevention

- Use service accounts with minimal required permissions
- Document required IAM roles for team members
- Set up proper VPC firewall rules

## Related Resources

- [SSH Issues](ssh_issues.md)

## Last Updated

2025-12-05
