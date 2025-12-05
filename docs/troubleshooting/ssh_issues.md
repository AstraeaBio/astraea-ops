# SSH - Common Issues and Fixes

## Context
- System: GCP VMs (analysis / segmentation machines)

---

## Problem
`ssh -i ~/.ssh/davis-image-segmentation-vm user@IP`  
returns:

> Permission denied (publickey)

or:

> Connection timed out

---

## Common Causes

1. **Incorrect SSH key permissions**: SSH keys must have restricted permissions
2. **Missing or incorrect SSH config**: Configuration file may be misconfigured
3. **Firewall blocking port 22**: Network restrictions preventing connections
4. **Expired or revoked keys**: SSH keys may no longer be valid

## Diagnosis

Typical root causes:

- Wrong private key specified in `-i` or key not present on local machine.
- Key not added to `ssh-agent`.
- VM was rebuilt and does not have the same `authorized_keys`.
- OS Login / IAM misconfigured (GCP user not allowed).
- Firewall rule or network tag blocking SSH.
- VM not actually running.

---

## Fix (Checklist)

### 1. Confirm VM is running
1. In GCP console, check VM status = `Running`.
2. If `Terminated`, start it and retry.

### 2. Confirm correct private key exists

```bash
ls -l ~/.ssh/davis-image-segmentation-vm
```

### 3 (Unix): Fix SSH Key Permissions

Ensure your SSH key files have the correct permissions:

```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 700 ~/.ssh
```

### 4: Verify SSH Config

Check your SSH configuration file:

```bash
cat ~/.ssh/config
```

### 5: Add key to ssh-agent
```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/davis-image-segmentation-vm
ssh-add -l  # confirm it's listed
```

Ensure host entries are properly formatted:

```
Host myserver
    HostName server.example.com
    User username
    IdentityFile ~/.ssh/id_rsa
```

### 6: Test SSH Connection Verbosely

Use verbose mode to diagnose issues:

```bash
ssh -vvv user@host
```

### 7: if using OS Login
Make sure OS Login is enabled and your user has roles/compute.osLogin:
```
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud compute os-login ssh-keys add --key-file=~/.ssh/davis-image-segmentation-vm.pub
```
Then:
```
gcloud compute ssh <INSTANCE_NAME> --zone=<ZONE> --project=<PROJECT_ID> \
  --ssh-key-file=~/.ssh/davis-image-segmentation-vm
```

### 8: If still failing - use serial console for recovery

1. Enable serial port access in VM settings.
2. Use GCP console serial console to log in as root/user.
3. Check /home/<user>/.ssh/authorized_keys and ensure the correct public key is present.
4. Fix permissions
```
chmod 700 /home/<user>/.ssh
chmod 600 /home/<user>/.ssh/authorized_keys
chown -R <user>:<user> /home/<user>/.ssh
```
5. Retry ssh

### Verification

- ssh user@IP connects without errors.
- You can ls expected project directories.
- Document which method worked (direct key vs OS Login).

## Prevention

- Standardize on OS Login for all analysts.
- Each VM must have:
- Documented project
  - Owner
  - Access method
- Any time a VM is rebuilt, update this doc if there’s a new trap
- If OS Login broken – attach disk to a rescue VM
  - Stop instance.
  - Detach disk.
  - Attach disk to a known-good VM as secondary.
  - Mount and copy critical data (e.g. /home, /opt, conda envs, notebooks).
- Rebuild clean VM
  - Use Terraform/template if you have one.
  - Reattach recovered data as needed.
  - Document the new access method and put a link here.

## Verification

- Analyst confirms they can:
  - SSH into VM
  - Run their segmentation pipeline
  - Access prior data

## Prevention / Notes
- No “snowflake” VMs:
- All must be reproducible from an image or Terraform.
- For each VM:
  - Keep a short VM_MANIFEST.md in this repo with:
    - Purpose
    - Owner
    - Creation method
    - Access method (OS Login / key)

- Regularly rotate SSH keys
- Use SSH agent for key management
- Keep SSH client and server software updated

## Related Resources

- [GCP VM Access](gcp_vm_access.md)

## Last Updated

2025-12-05
