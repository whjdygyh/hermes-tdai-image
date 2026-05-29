#!/usr/bin/env python3
"""
R2 S3 Tools - Zero dependency Cloudflare R2 read/write tool for Alex2.
Uses only Python stdlib + AWS Signature V4.

Usage:
  python r2_tools.py read <key>           # Read file content from R2
  python r2_tools.py write <key> <text>   # Write text to R2
  python r2_tools.py list [prefix]        # List files in R2
  python r2_tools.py delete <key>         # Delete file from R2

Env vars required:
  R2_ENDPOINT       e.g. https://xxx.r2.cloudflarestorage.com
  R2_ACCESS_KEY_ID
  R2_SECRET_ACCESS_KEY
  R2_BUCKET         e.g. mingyang
"""

import os
import sys
import hashlib
import hmac
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(secret_key, date_stamp, region, service):
    k_date = sign(('AWS4' + secret_key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def s3_request(method, key, body=None, query_params=None):
    """Make an S3-compatible request to R2."""
    endpoint = os.environ['R2_ENDPOINT'].rstrip('/')
    access_key = os.environ['R2_ACCESS_KEY_ID']
    secret_key = os.environ['R2_SECRET_ACCESS_KEY']
    bucket = os.environ['R2_BUCKET']
    region = 'auto'
    service = 's3'

    # Parse endpoint
    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.netloc

    # Build canonical URI
    canonical_uri = '/' + key if key else '/'
    canonical_uri = urllib.parse.quote(canonical_uri, safe='/')

    # Build canonical query string
    canonical_querystring = ''
    if query_params:
        canonical_querystring = urllib.parse.urlencode(sorted(query_params.items()))

    # Prepare request
    url = f"{endpoint}/{key}" if key else endpoint
    if canonical_querystring:
        url += '?' + canonical_querystring

    body_bytes = body.encode('utf-8') if body else b''
    content_type = 'application/octet-stream' if body else ''

    # AWS Signature V4
    t = datetime.now(timezone.utc)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    # Canonical request
    canonical_headers = f'host:{host}\nx-amz-content-sha256:{sha256_hex(body_bytes)}\nx-amz-date:{amz_date}\n'
    signed_headers = 'host;x-amz-content-sha256;x-amz-date'

    canonical_request = '\n'.join([
        method,
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        sha256_hex(body_bytes)
    ])

    # String to sign
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = '\n'.join([
        algorithm,
        amz_date,
        credential_scope,
        sha256_hex(canonical_request.encode('utf-8'))
    ])

    # Signing key
    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )

    headers = {
        'Host': host,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': sha256_hex(body_bytes),
        'Authorization': authorization,
    }
    if content_type:
        headers['Content-Type'] = content_type

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def cmd_read(key):
    status, data = s3_request('GET', key)
    if status == 200:
        print(data.decode('utf-8'))
    elif status == 404:
        print(f"❌ 文件不存在: {key}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"❌ 读取失败 (HTTP {status}): {data.decode('utf-8', errors='replace')[:200]}", file=sys.stderr)
        sys.exit(1)


def cmd_write(key, text):
    status, data = s3_request('PUT', key, body=text)
    if status == 200:
        print(f"✅ 写入成功: {key}")
    else:
        print(f"❌ 写入失败 (HTTP {status}): {data.decode('utf-8', errors='replace')[:200]}", file=sys.stderr)
        sys.exit(1)


def cmd_list(prefix=''):
    params = {'list-type': '2', 'prefix': prefix} if prefix else {'list-type': '2'}
    status, data = s3_request('GET', '', query_params=params)
    if status == 200:
        root = ET.fromstring(data)
        ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
        contents = root.findall('.//s3:Contents', ns)
        if not contents:
            print(f"(空) - 前缀: '{prefix}'" if prefix else "(空)")
            return
        for obj in contents:
            key_elem = obj.find('s3:Key', ns)
            size_elem = obj.find('s3:Size', ns)
            lastmod = obj.find('s3:LastModified', ns)
            if key_elem is not None:
                size = int(size_elem.text) if size_elem is not None else 0
                mod = lastmod.text[:19] if lastmod is not None else '?'
                print(f"  {key_elem.text}  ({size:,} bytes, {mod})")
    else:
        print(f"❌ 列出失败 (HTTP {status})", file=sys.stderr)
        sys.exit(1)


def cmd_delete(key):
    status, data = s3_request('DELETE', key)
    if status in (200, 204):
        print(f"✅ 删除成功: {key}")
    else:
        print(f"❌ 删除失败 (HTTP {status}): {data.decode('utf-8', errors='replace')[:200]}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    required = ['R2_ENDPOINT', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET']
    missing = [v for v in required if v not in os.environ]
    if missing:
        print(f"❌ 缺少环境变量: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'read':
        if len(sys.argv) < 3:
            print("用法: r2_tools.py read <key>", file=sys.stderr)
            sys.exit(1)
        cmd_read(sys.argv[2])

    elif cmd == 'write':
        if len(sys.argv) < 4:
            print("用法: r2_tools.py write <key> <text>", file=sys.stderr)
            sys.exit(1)
        cmd_write(sys.argv[2], sys.argv[3])

    elif cmd == 'list':
        prefix = sys.argv[2] if len(sys.argv) > 2 else ''
        cmd_list(prefix)

    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("用法: r2_tools.py delete <key>", file=sys.stderr)
            sys.exit(1)
        cmd_delete(sys.argv[2])

    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
