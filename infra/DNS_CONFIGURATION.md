# DNS Configuration for Return-to-Print

## Route 53 Hosted Zone Details

**Domain**: returntoprint.xyz
**Hosted Zone ID**: Z03595423QUR7NOOMU64T
**Status**: Active

## Nameservers to Configure in Squarespace

You need to update the nameservers in your Squarespace domain settings to point to AWS Route 53:

1. **ns-1738.awsdns-25.co.uk**
2. **ns-1398.awsdns-46.org**
3. **ns-233.awsdns-29.com**
4. **ns-662.awsdns-18.net**

## Steps to Update Squarespace DNS

1. Log in to your Squarespace account
2. Go to Settings → Domains → returntoprint.xyz
3. Click on "Advanced Settings" or "DNS Settings"
4. Look for "Custom Nameservers" or "Use Custom Nameservers"
5. Replace the existing nameservers with the four AWS Route 53 nameservers listed above
6. Save the changes

## DNS Propagation

- DNS changes typically propagate within 24-48 hours
- You can check propagation status using: `dig returntoprint.xyz NS`
- Once propagated, AWS Route 53 will handle all DNS records for this domain

## Next Steps (After DNS Propagation)

1. Configure Amplify custom domain to point to `www.returntoprint.xyz`
2. Amplify will automatically create the necessary DNS records in Route 53
3. SSL/TLS certificate will be provisioned automatically via AWS Certificate Manager (ACM)

## Testing DNS Configuration

Check if nameservers are updated:
```bash
dig returntoprint.xyz NS +short
```

Expected output (after propagation):
```
ns-1738.awsdns-25.co.uk.
ns-1398.awsdns-46.org.
ns-233.awsdns-29.com.
ns-662.awsdns-18.net.
```

