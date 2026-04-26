# Skill: Secure API Caller

> **Description**: A standardized pattern for invoking third-party APIs (like Nullscript) using encrypted local storage.
> **Security Level**: High (OS Keyring backed).

## 📐 Mechanism
1.  **Check**: Does the service credential exist in the OS Keyring?
2.  **Store**: If missing, prompt the user to input the Token, then encrypt & save it.
3.  **Retrieve**: Securely load the Token into memory.
4.  **Execute**: Perform the API request.
5.  **Cleanup**: Purge the Token from memory variables immediately after use.

## 🔑 Key Management
-   **Tool**: `keyring` (Python library).
-   **Storage**: OS Keyring (e.g., Windows Credential Manager).
-   **Naming Convention**:
    -   **Service Name**: `[provider]_service` (e.g., `nullscript_service`)
    -   **Username/Key**: `access_token`

## 🛠️ Standard Usage (Safe Mode)

### 💻 Command Line Interaction (Zero-Log Injection)
**CRITICAL**: Never print the token to stdout/logs. Inject directly into environment variables.

**PowerShell**:
```powershell
# 1. Retrieve & Inject (Silent)
$env:API_KEY = (python helper.py nullscript get)

# 2. Use it
curl -H "Authorization: Bearer $env:API_KEY" ...

# 3. Purge memory
$env:API_KEY = $null
```

### 🐍 Python Interaction
```python
import keyring

SERVICE = "nullscript_service"
USER = "access_token"

# Direct retrieval into variable (Safe)
token = keyring.get_password(SERVICE, USER)
# ... use token in headers ...
del token # Clear from memory immediately
```

## 📂 File Structure
```text
desk/agent/skills/secure_call/
├── SKILL.md          # This file
└── helper.py         # Standardized helper script
```
