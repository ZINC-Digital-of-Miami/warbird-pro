#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Read-only Supabase REST MCP for Warbird using anon/publishable key."""
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from pathlib import Path
from typing import Any, Literal
from mcp.server.fastmcp import FastMCP
ENV_PATH=Path('/Volumes/Satechi Hub/warbird-pro/.env.local')
mcp=FastMCP('warbird_supabase_ro_mcp', instructions='Read-only Supabase REST select helper. Exposes GET/select only; no inserts, updates, deletes, RPC, or SQL execution.')

def _env(name: str) -> str:
    if os.getenv(name): return os.getenv(name,'')
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(errors='ignore').splitlines():
            if line.startswith(name+'='):
                return line.split('=',1)[1].strip().strip('"').strip("'")
    return ''

def _fmt(payload: dict[str, Any], response_format: Literal['json','markdown']='markdown'):
    if response_format=='json': return payload
    return '```json\n'+json.dumps(payload, indent=2, sort_keys=True)+'\n```'

@mcp.tool()
def supabase_ro_status(response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """Report whether Supabase URL and anon/publishable key are available, without exposing secrets."""
    url=_env('NEXT_PUBLIC_SUPABASE_URL') or _env('SUPABASE_URL')
    key=_env('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY') or _env('SUPABASE_PUBLISHABLE_KEY') or _env('NEXT_PUBLIC_SUPABASE_ANON_KEY') or _env('SUPABASE_ANON_KEY')
    return _fmt({'ok':bool(url and key),'url_present':bool(url),'anon_or_publishable_key_present':bool(key),'env_path':str(ENV_PATH)}, response_format)

@mcp.tool()
def supabase_rest_select(table: str, select: str='*', limit: int=10, filters_json: str='{}', response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """Read rows through Supabase REST with GET/select only. filters_json maps column/operator to value, e.g. {\"symbol\":\"eq.ES\"}."""
    if not table.replace('_','').replace('-','').isalnum():
        return _fmt({'ok':False,'error':'Unsafe table name'}, response_format)
    url=(_env('NEXT_PUBLIC_SUPABASE_URL') or _env('SUPABASE_URL')).rstrip('/')
    key=_env('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY') or _env('SUPABASE_PUBLISHABLE_KEY') or _env('NEXT_PUBLIC_SUPABASE_ANON_KEY') or _env('SUPABASE_ANON_KEY')
    if not url or not key: return _fmt({'ok':False,'error':'Supabase URL/key not available'}, response_format)
    try: filters=json.loads(filters_json or '{}')
    except Exception as e: return _fmt({'ok':False,'error':'Invalid filters_json: '+repr(e)}, response_format)
    params={'select':select,'limit':str(max(1,min(limit,100)))}
    params.update({str(k):str(v) for k,v in filters.items()})
    endpoint=f"{url}/rest/v1/{urllib.parse.quote(table)}?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(endpoint, headers={'apikey':key,'Authorization':'Bearer '+key,'Accept':'application/json','User-Agent':'Hermes-Warbird-Supabase-RO/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data=json.loads(r.read().decode('utf-8'))
            payload={'ok':True,'table':table,'count':len(data) if isinstance(data,list) else None,'data':data}
    except Exception as e: payload={'ok':False,'table':table,'error':repr(e)}
    return _fmt(payload, response_format)

if __name__=='__main__':
    mcp.run()
