#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Read-only filesystem MCP rooted to user/project volumes."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Literal
from mcp.server.fastmcp import FastMCP
ROOTS=[Path('/Users/zincdigital').resolve(), Path('/Volumes/Satechi Hub').resolve()]
DENY_PARTS={'.ssh','.gnupg','.aws','.1password','.cache','.npm','.Trash'}
DENY_NAMES={'.env','auth.json','hosts.yml','id_rsa','id_ed25519'}
MAX_CHARS=50000
mcp=FastMCP('warbird_filesystem_mcp', instructions='Read-only filesystem MCP rooted at /Users/zincdigital and /Volumes/Satechi Hub. Secret-like paths are denied.')

def _fmt(payload: dict[str, Any], response_format: Literal['json','markdown']='markdown'):
    if response_format=='json': return payload
    return '```json\n'+json.dumps(payload, indent=2, sort_keys=True)+'\n```'

def _resolve(path: str) -> Path:
    return Path(path).expanduser().resolve()

def _check(path: str) -> tuple[bool, str, Path | None]:
    p=_resolve(path)
    if not any(p == r or r in p.parents for r in ROOTS):
        return False, 'Path is outside allowed roots', None
    if any(part in DENY_PARTS for part in p.parts) or p.name in DENY_NAMES or p.suffix.lower() in {'.pem','.key','.p12'}:
        return False, 'Path is denied because it may contain secrets', None
    return True, '', p

@mcp.tool()
def fs_roots(response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """Return allowed read-only roots."""
    return _fmt({'ok': True, 'roots': [str(r) for r in ROOTS]}, response_format)

@mcp.tool()
def fs_list(path: str, limit: int = 200, response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """List a directory under allowed roots."""
    ok,err,p=_check(path)
    if not ok: return _fmt({'ok':False,'error':err,'path':path}, response_format)
    if not p or not p.is_dir(): return _fmt({'ok':False,'error':'Not a directory','path':str(p)}, response_format)
    rows=[]
    for child in sorted(p.iterdir(), key=lambda x:(not x.is_dir(), x.name.lower()))[:max(1,min(limit,1000))]:
        if child.name in DENY_NAMES: continue
        try: st=child.stat()
        except OSError: continue
        rows.append({'name':child.name,'path':str(child),'type':'dir' if child.is_dir() else 'file','size':st.st_size})
    return _fmt({'ok':True,'path':str(p),'entries':rows}, response_format)

@mcp.tool()
def fs_read_text(path: str, max_chars: int = MAX_CHARS, response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """Read a text file under allowed roots, bounded and secret-path protected."""
    ok,err,p=_check(path)
    if not ok: return _fmt({'ok':False,'error':err,'path':path}, response_format)
    if not p or not p.is_file(): return _fmt({'ok':False,'error':'Not a file','path':str(p)}, response_format)
    data=p.read_bytes()[:max(1,min(max_chars,200000))+1]
    text=data[:max_chars].decode('utf-8', errors='replace')
    return _fmt({'ok':True,'path':str(p),'truncated':len(data)>max_chars,'text':text}, response_format)

if __name__=='__main__':
    mcp.run()
