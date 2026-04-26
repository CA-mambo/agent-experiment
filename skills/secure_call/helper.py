# -*- coding: utf-8 -*-
"""
Helper Script for Secure API Calls
Provides a unified interface to interact with OS Keyring.
"""

import keyring
import sys

def get_service_name(provider):
    """Standardize service name."""
    return f"{provider}_service"

def save_token(provider, token):
    """Store token securely."""
    service = get_service_name(provider)
    keyring.set_password(service, "access_token", token)
    print(f"[INFO] Token for '{provider}' saved securely.")

def get_token(provider):
    """Retrieve token securely."""
    service = get_service_name(provider)
    token = keyring.get_password(service, "access_token")
    if not token:
        print(f"[ERROR] No token found for '{provider}'.")
        sys.exit(1)
    return token

def check_exists(provider):
    """Check if token exists."""
    service = get_service_name(provider)
    token = keyring.get_password(service, "access_token")
    return token is not None

if __name__ == "__main__":
    # CLI Usage: helper.py <provider> <get|save|check> [token]
    if len(sys.argv) < 3:
        print("Usage: helper.py <provider> <get|save|check> [token]")
        sys.exit(1)

    provider = sys.argv[1]
    action = sys.argv[2]

    if action == "save":
        if len(sys.argv) < 4:
            print("Please provide the token.")
        else:
            save_token(provider, sys.argv[3])
    elif action == "get":
        # Output token directly to stdout for capturing
        print(get_token(provider))
    elif action == "check":
        print("exists" if check_exists(provider) else "missing")
