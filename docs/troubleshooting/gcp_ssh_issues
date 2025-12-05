# GCP VM Access - Lost or Broken Access

## Context
Analyst had a working pipeline on a VM but can no longer access it.

## Problem
Historical:
- Davis had a working segmentation pipeline on VM X.
- Lost SSH access; multiple people spent hours trying.

## Diagnosis

Common causes:
- VM recreated with different disk / metadata.
- Service account or IAM roles changed.
- OS Login enabled/disabled midstream.
- Firewall rules updated.
- External IP changed and local SSH config stale.

## Fix (Recovery Playbook)

1. **Identify the VM correctly**
   - Project:
   - Zone:
   - Instance name:
   - Disk name(s):

2. **Check instance configuration**
   - Confirm:
     - External IP still present.
     - Network tags still include SSH-allowed tags.

3. **Snapshot disk ASAP**
   - If access may require destructive steps, snapshot the boot + data disks.

4. **Try OS Login SSH**

```bash
gcloud compute ssh <INSTANCE_NAME> --zone=<ZONE> --project=<PROJECT_ID>
```
