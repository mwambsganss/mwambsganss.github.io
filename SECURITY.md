# Security Policy

## 🔒 Security Measures

This repository implements multiple layers of security to prevent accidental exposure of secrets and credentials.

---

## Protected Information

### ❌ Never Commit These

1. **Environment Variables**
   - `.env`, `.env.local`, `.env.*` files
   - Any file containing environment-specific configuration

2. **Credentials & Secrets**
   - API keys, access tokens, refresh tokens
   - Passwords, passphrases
   - Private keys (`.pem`, `.key`, `.p12`, `.pfx`)
   - Service account files
   - SSH keys

3. **Cloud Provider Credentials**
   - AWS: `.aws/credentials`, access keys (`AKIA...`)
   - Azure: Client IDs, client secrets, tenant IDs
   - GCP: Service account JSON files
   - Kubernetes: `.kube/config`

4. **Authentication Tokens**
   - Bearer tokens
   - OAuth tokens
   - JWT tokens
   - GitHub personal access tokens

---

## Security Features

### 1. `.gitignore` Protection
Root-level `.gitignore` blocks common secret file patterns:
- Environment files (`.env*`)
- Credential files (`credentials.json`, `*secret*`, `*password*`)
- Private keys (`*.pem`, `*.key`, etc.)
- Cloud provider config directories (`.aws/`, `.azure/`, etc.)
- Backup files (`*.bak`)

### 2. Secret Sanitization
The Web Crawler includes automatic sanitization:
- Azure AD client secrets (Q~ pattern)
- Client IDs (UUIDs in context)
- Bearer tokens
- API keys
- Access tokens

See: [`Web Crawler/web_crawler.py`](Web%20Crawler/web_crawler.py) - `sanitize_html()` function

### 3. Claude Code Permissions
Claude Code is configured to deny reading sensitive files:
```json
"permissions": {
  "deny": [
    "Read(./.env)",
    "Read(**/*.pem)",
    "Read(**/*.key)",
    "Read(~/.ssh/**)",
    "Read(~/.aws/**)",
    "Read(**/*password*)",
    "Read(**/*token*)",
    "Read(**/*secret*)"
  ]
}
```

### 4. Test Data Safety
All test secrets in `Web Crawler/Tester/fixtures/` are:
- ✅ Clearly marked as FAKE
- ✅ Documented in test files
- ✅ Non-functional placeholders
- ✅ Safe for public repositories

### 5. GitLeaks Configuration
`.gitleaks.toml` provides automated secret scanning:
- Detects Azure secrets, API keys, AWS keys
- Scans for bearer tokens and private keys
- Allows test fixtures and documentation examples

---

## Verification

### Manual Secret Scan

```bash
# Search for potential secrets
grep -r -i "password\|api_key\|secret_key\|access_token" \
  --include="*.py" \
  --include="*.js" \
  --include="*.json" \
  --exclude-dir=".git" \
  --exclude-dir="Tester" \
  .

# Check for secret files
find . -type f \( \
  -name "*.env*" \
  -o -name "*credentials*" \
  -o -name "*secret*" \
  -o -name "*.pem" \
  -o -name "*.key" \
\) ! -path "./.git/*" ! -path "*/Tester/fixtures/*"
```

### GitLeaks Scan (if installed)

```bash
# Install gitleaks
brew install gitleaks

# Scan repository
gitleaks detect --config .gitleaks.toml --verbose

# Scan git history
gitleaks detect --config .gitleaks.toml --log-opts="--all"
```

---

## If You Accidentally Commit a Secret

### Immediate Actions

1. **Revoke the credential immediately**
   - Rotate API keys
   - Regenerate tokens
   - Change passwords

2. **Remove from git history**
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   git filter-repo --invert-paths --path path/to/secret/file

   # Or for specific strings
   git filter-repo --replace-text <(echo "SECRET_TO_REMOVE==>REMOVED")
   ```

3. **Force push (with caution)**
   ```bash
   git push --force-with-lease origin master
   ```

4. **Notify your security team**
   - Report the incident
   - Document what was exposed
   - Confirm the credential has been revoked

---

## Best Practices

### ✅ Do This

1. **Use Environment Variables**
   ```python
   import os
   api_key = os.getenv('API_KEY')
   ```

2. **Use Secret Management**
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault

3. **Commit .env.example**
   ```bash
   # .env.example (safe to commit)
   API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:password@localhost/db
   ```

4. **Review Before Committing**
   ```bash
   git diff --cached  # Review staged changes
   git status         # Check what's being committed
   ```

5. **Use Pre-commit Hooks**
   Install tools like `gitleaks` or `detect-secrets` as pre-commit hooks

### ❌ Don't Do This

1. **Don't hardcode secrets**
   ```python
   # BAD ❌
   api_key = "sk_live_abc123..."

   # GOOD ✅
   api_key = os.getenv('API_KEY')
   ```

2. **Don't commit credentials in comments**
   ```python
   # BAD ❌
   # API Key: sk_live_abc123xyz456

   # GOOD ✅
   # API Key loaded from environment variable
   ```

3. **Don't use weak .gitignore patterns**
   ```
   # BAD ❌
   config.json

   # GOOD ✅
   *config*.json
   credentials*.json
   ```

---

## Security Contacts

### Internal (Lilly Employees)
- **Security Team**: [Lilly Information Security]
- **IT Support**: [Lilly IT Help Desk]

### External Contributors
- **GitHub Security**: Report via GitHub's security advisory feature
- **Email**: [If you want to provide a security contact email]

---

## Compliance

This repository follows:
- ✅ Lilly security policies
- ✅ GitHub security best practices
- ✅ OWASP secure coding guidelines
- ✅ Principle of least privilege

---

## Audit Log

| Date | Action | Description |
|------|--------|-------------|
| 2026-03-02 | Created | Initial security policy and .gitignore |
| 2026-02-26 | Implemented | Secret sanitization in web_crawler.py |
| 2026-02-26 | Added | Claude Code permission restrictions |

---

*Last Updated: 2026-03-02*
*This document should be reviewed and updated regularly*
