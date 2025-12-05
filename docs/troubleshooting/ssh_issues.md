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

### Solution 3 (Unix): Fix SSH Key Permissions

Ensure your SSH key files have the correct permissions:

```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 700 ~/.ssh
```

### Solution 4: Verify SSH Config

Check your SSH configuration file:

```bash
cat ~/.ssh/config
```

Ensure host entries are properly formatted:

```
Host myserver
    HostName server.example.com
    User username
    IdentityFile ~/.ssh/id_rsa
```

### Solution 5: Test SSH Connection Verbosely

Use verbose mode to diagnose issues:

```bash
ssh -vvv user@host
```

## Prevention

- Regularly rotate SSH keys
- Use SSH agent for key management
- Keep SSH client and server software updated

## Related Resources

- [GCP VM Access](gcp_vm_access.md)

## Last Updated

2025-12-05
