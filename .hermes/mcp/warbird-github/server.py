#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Read-only GitHub MCP for Warbird."""
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from pathlib import Path
from typing import Any, Literal
from mcp.server.fastmcp import FastMCP
DEFAULT_OWNER='zincdigitalofmiami'; DEFAULT_REPO='warbird-pro'
mcp=FastMCP('warbird_github_mcp', instructions='Read-only GitHub REST helpers for Warbird. No mutation tools are exposed.')

def _load_env_key(name: str) -> str:
    if os.getenv(name): return os.getenv(name,'')
    p=Path.home()/'.hermes/.env'
    if p.exists():
        for line in p.read_text(errors='ignore').splitlines():
            if line.startswith(name+'='):
                return line.split('=',1)[1].strip().strip('"').strip("'")
    return ''

def _fmt(payload: dict[str, Any], response_format: Literal['json','markdown']='markdown'):
    if response_format=='json': return payload
    return '```json\n'+json.dumps(payload, indent=2, sort_keys=True)+'\n```'

def _gh(path: str, params: dict[str, Any] | None=None) -> dict[str, Any]:
    token=_load_env_key('GITHUB_TOKEN')
    url='https://api.github.com'+path
    if params: url += '?' + urllib.parse.urlencode(params)
    headers={'Accept':'application/vnd.github+json','User-Agent':'Hermes-Warbird-GitHub/1.0'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return {'status':getattr(r,'status',None),'data':json.loads(r.read().decode('utf-8'))}

@mcp.tool()
def github_repo_summary(owner: str=DEFAULT_OWNER, repo: str=DEFAULT_REPO, response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """Return read-only GitHub repository summary."""
    try:
        d=_gh(f'/repos/{owner}/{repo}')['data']
        payload={'ok':True,'full_name':d.get('full_name'),'default_branch':d.get('default_branch'),'private':d.get('private'),'open_issues_count':d.get('open_issues_count'),'pushed_at':d.get('pushed_at'),'updated_at':d.get('updated_at')}
    except Exception as e:
        payload={'ok':False,'error':repr(e)}
    return _fmt(payload, response_format)

@mcp.tool()
def github_open_prs(owner: str=DEFAULT_OWNER, repo: str=DEFAULT_REPO, limit: int=20, response_format: Literal['json','markdown']='markdown') -> str | dict[str, Any]:
    """List open pull requests read-only."""
    try:
        data=_gh(f'/repos/{owner}/{repo}/pulls', {'state':'open','per_page':max(1,min(limit,100))})['data']
        prs=[{'number':x.get('number'),'title':x.get('title'),'head':x.get('head',{}).get('ref'),'base':x.get('base',{}).get('ref'),'user':x.get('user',{}).get('login')} for x in data]
        payload={'ok':True,'pull_requests':prs}
    except Exception as e: payload={'ok':False,'error':repr(e)}
    return _fmt(payload, response_format)

if __name__=='__main__':
    mcp.run()
