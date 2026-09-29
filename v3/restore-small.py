#!/usr/bin/env python3
"""Verify and decrypt a small sealed Python payload locally."""
import getpass
import hashlib
import json
import os
import pathlib
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

here = pathlib.Path(__file__).resolve().parent
manifest = json.loads((here / 'manifest.json').read_text(encoding='utf-8'))
sealed = (here / 'payload.enc').read_bytes()
if hashlib.sha256(sealed).hexdigest() != manifest['cipher_sha256']:
    raise SystemExit('ERROR: encrypted payload checksum mismatch')
secret = os.environ.get('SEAL_KEY_IV') or getpass.getpass('Paste KEY:IV: ')
secret = secret.strip()
try:
    key_hex, iv_hex = secret.split(':', 1)
    key, iv = bytes.fromhex(key_hex), bytes.fromhex(iv_hex)
    if len(key) != 32 or len(iv) != 16:
        raise ValueError()
except ValueError:
    raise SystemExit('ERROR: expected 64 hex characters, colon, 32 hex characters')
decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
padded = decryptor.update(sealed) + decryptor.finalize()
try:
    unpadder = padding.PKCS7(128).unpadder()
    plain = unpadder.update(padded) + unpadder.finalize()
except ValueError:
    raise SystemExit('ERROR: wrong key or damaged payload')
if hashlib.sha256(plain).hexdigest() != manifest['plain_sha256']:
    raise SystemExit('ERROR: decrypted payload checksum mismatch')
target = here / 'runner.py'
target.write_bytes(plain)
print('RESTORE=PASS')
