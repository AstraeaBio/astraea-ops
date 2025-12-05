# SSH Issues

## Overview

Common SSH connection and authentication problems encountered when accessing remote servers and VMs.

## Symptoms

- Connection refused errors
- Permission denied (publickey) errors
- Connection timeout issues
- Host key verification failed

## Common Causes

1. **Incorrect SSH key permissions**: SSH keys must have restricted permissions
2. **Missing or incorrect SSH config**: Configuration file may be misconfigured
3. **Firewall blocking port 22**: Network restrictions preventing connections
4. **Expired or revoked keys**: SSH keys may no longer be valid

## Solutions

### Solution 1: Fix SSH Key Permissions

Ensure your SSH key files have the correct permissions:

```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 700 ~/.ssh
```

### Solution 2: Verify SSH Config

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

### Solution 3: Test SSH Connection Verbosely

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
