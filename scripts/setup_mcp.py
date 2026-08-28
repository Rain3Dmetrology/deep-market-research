#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_mcp.py — 生成本机 ~/.workbuddy/mcp.json (从 OneDrive 桌面 key 文件读取)

设计原则：
  1. 本脚本【无任何硬编码 key】，纯读取桌面 key 文件 + 自动剥前缀 (Rule 1)
  2. 生成的 mcp.json 与「本机已验证」格式一致：**所有 server 一律剥前缀**（裸 token）
     ⚠️ 实测结论：exa/firecrawl/hf/modelscope 的 env 值若带 `APIKEY:`/`access token：` 前缀，
     上游 API 会 401 拒绝；裸 token 才通过。上游 API 不接受带前缀的 token。
  3. 可重复运行：先备份现有 mcp.json，再合并（保留脚本未管理的其他 server）
  4. 跨平台：Desktop 路径可配，默认按 OneDrive 常见位置探测

用法：
  python setup_mcp.py                         # 探测 Desktop，生成并写 ~/.workbuddy/mcp.json
  python setup_mcp.py --dry-run              # 只打印将生成的配置，不写文件
  python setup_mcp.py --desktop ~/OneDrive/Desktop
  python setup_mcp.py --out /path/to/mcp.json
  python setup_mcp.py --no-backup            # 不备份现有 mcp.json

依赖：Python 3.10+（代码使用 `str | None` 等联合类型语法），仅标准库。
"""
import json
import os
import re
import sys
import shutil
import getpass
import argparse
import subprocess
from datetime import datetime

# ---------------------------------------------------------------------------
# 1. Server → key 文件映射（仅文件名，不含任何 key 值）
# ---------------------------------------------------------------------------
SERVER_KEYFILES = {
    "exa":         "Exa_apikey.txt",
    "firecrawl":   "FirecrawlAPIKEY.txt",
    "tavily":      "TavilyAPIkey.txt",
    "huggingface": "huggingfaceaccestoken.txt",
    "modelscope":  "modelscopeToken.txt",
    "zhihu":       "zhihuAPItoken.txt",
    "readgzh":     "ReadGZH .txt",   # 远程 MCP（url + Bearer header），公众号全文提取
}

# ---------------------------------------------------------------------------
# 2. 非 MCP 的 key（REST API / 代理）—— 仅写入本机 dmr_keys.env（绝不入仓库）
#    用于 dmr 可选增强层（FRED 经济数据、Novada Web Unblocker 代理等）跨机器同步
# ---------------------------------------------------------------------------
NON_MCP_KEYFILES = {
    "FRED_API_KEY":   "FREDAPIkey.txt",
    "NOVADA_API_KEY": "novadaWeb UnblockerAPIkey.txt",
}

# 前缀正则：匹配 APIKEY: / APIkey：/ access token：/ Key£º / Token: 等
# 分隔符 [:：£º] 设为可选 —— 应对 GBK 全角冒号在 UTF-8 读取时被静默丢弃的情况
PREFIX_RE = re.compile(
    r"^(?:APIKEY|APIkey|API\w*KEY|access\s*token|Key|Token)\s*[:：£º]?\s*",
    re.IGNORECASE,
)

# ⚠️ 所有 server 一律剥前缀（实测：带前缀 token 上游 API 全 401 拒，裸 token 才通）
# 不再区分 env/header/url 类 —— 见设计原则 #2
KEEP_PREFIX = set()  # 空集 = 全部剥前缀（既然全剥，无需按名名单）


def detect_desktop() -> str:
    """探测 OneDrive Desktop 路径（仅用环境变量，不硬编码任何绝对路径以避免泄露机器信息）。"""
    candidates = [
        os.path.expandvars(r"%OneDrive%\Desktop"),
        os.path.expandvars(r"%OneDriveConsumer%\Desktop"),
        os.path.expandvars(r"%OneDriveCommercial%\Desktop"),
        os.path.expanduser(r"~/OneDrive/Desktop"),
        os.path.expanduser(r"~/OneDrive - Personal/Desktop"),
        os.path.expanduser(r"~/Desktop"),
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return os.path.expanduser(r"~/Desktop")


def read_text(path: str) -> str:
    """鲁棒读取：二进制读后按 utf-8 → gbk → latin-1 回退解码。"""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def _restrict_to_owner(path: str) -> None:
    """将敏感文件（含密钥）权限收窄为仅当前用户可读（跨平台，纯标准库）。

    - POSIX：`os.chmod 0o600` 直接限所有者读写。
    - Windows：无 600 语义，依赖 NTFS ACL —— 用 `icacls` 移除继承后仅授予当前用户读权限；
      若 icacls 不可用或执行失败，仅告警不阻断（文件仍受默认用户目录 ACL 保护）。
    """
    if os.name != "nt":
        os.chmod(path, 0o600)
        return
    try:
        subprocess.run(
            ["icacls", path, "/inheritance:r", "/grant:r", f"{getpass.getuser()}:(R)"],
            capture_output=True, text=True, shell=False, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        print(
            f"[!] WARN: 无法通过 icacls 收窄 {path} 的 NTFS ACL（{e}）；"
            f"请人工确认仅当前用户可读",
            file=sys.stderr,
        )


def _warn_if_in_repo(path: str) -> None:
    """若 path 位于 git 工作树内，向 stderr 打印 WARNING（含密钥，切勿提交）。

    通过 `git -C <父目录> rev-parse --is-inside-work-tree` 判定；
    shell=False（强制）以避免命令注入。判定失败（git 不存在等）时静默跳过。
    """
    parent = os.path.dirname(os.path.abspath(path)) or "."
    try:
        res = subprocess.run(
            ["git", "-C", parent, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, shell=False,
        )
    except (OSError, ValueError):
        return
    if res.stdout.strip() == "true":
        print(
            f"[!] WARN: 输出文件 {path} 位于 git 工作树内，"
            f"请确保它已被 .gitignore 忽略（含密钥，切勿提交）",
            file=sys.stderr,
        )


def extract_key(path: str, keep_prefix: bool) -> str | None:
    """
    从 key 文件提取 token。
    - 多行文件（如 Exa 367 行文档+key）取首个含前缀的行
    - 多 token 文件（如 modelscope read/write）取第一个
    - keep_prefix=False 时剥掉所有已知前缀
    """
    try:
        text = read_text(path)
        lines = text.splitlines()
    except OSError:
        return None

    first_line = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if first_line is None:
            first_line = line
        m = PREFIX_RE.match(line)
        if m:
            token = line[m.end():].strip()
            if not keep_prefix:
                # 二次保险：若仍有残留前缀（罕见）再剥一次
                token = PREFIX_RE.sub("", token).strip()
            return token
        # 退化匹配：含分隔符且非 label 行
        if any(sep in line for sep in (":", "：", "£º")):
            sep = next(s for s in (":", "：", "£º") if s in line)
            k, _, v = line.partition(sep)
            if k.strip().lower() not in ("name", "label", "webhook signing secret"):
                token = v.strip()
                if not keep_prefix:
                    token = PREFIX_RE.sub("", token).strip()
                return token
    # 兜底：纯裸 key 文件（无前缀、无分隔符，如 novada 单行长 key，可能带前导空格）
    if first_line:
        token = first_line
        if not keep_prefix:
            token = PREFIX_RE.sub("", token).strip()
        return token
    return None


def build_servers(keys: dict) -> dict:
    """根据提取到的 key / UA 构造 10 个 key/UA-based + 1 keyless (deepwiki) server 配置（无硬编码 key）。"""
    servers: dict = {}

    if "exa" in keys:
        servers["exa"] = {
            "command": "npx",
            "args": ["-y", "exa-mcp-server"],
            "env": {"EXA_API_KEY": keys["exa"]},
        }

    if "firecrawl" in keys:
        servers["firecrawl"] = {
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"],
            "env": {"FIRECRAWL_API_KEY": keys["firecrawl"]},
        }

    if "tavily" in keys:
        # 官方 stdio 包：读 TAVILY_API_KEY env，免 mcp-remote 桥的浏览器 OAuth，无头可自动化
        servers["tavily"] = {
            "command": "npx",
            "args": ["-y", "tavily-mcp"],
            "env": {"TAVILY_API_KEY": keys["tavily"]},
        }

    if "huggingface" in keys:
        servers["huggingface"] = {
            "command": "uvx",
            "args": ["huggingface-mcp-server"],
            "env": {"HF_TOKEN": keys["huggingface"],
                    "DEFAULT_HF_TOKEN": keys["huggingface"]},
        }

    if "modelscope" in keys:
        servers["modelscope"] = {
            "command": "uvx",
            "args": ["modelscope-mcp-server"],
            "env": {"MODELSCOPE_API_TOKEN": keys["modelscope"]},
        }

    if "zhihu" in keys:
        z = keys["zhihu"]
        hdr = f"Authorization: Bearer {z}"
        # 官方 MCP-over-SSE 端点（注意正确路径含 /api 与 /v1）
        # ⚠️ 必须 --transport sse-only：mcp-remote 默认 http-first 会对 SSE 端点返回 405/SpA HTML 而失败；
        #    sse-only 直连 SSE 传输，已实测稳定连通并成功 tools/call 返回真实知乎结果。
        zhihu_endpoints = {
            "zhihu-search":   "https://developer.zhihu.com/api/mcp/zhihu_search/v1/sse",
            "zhihu-global":   "https://developer.zhihu.com/api/mcp/global_search/v1/sse",
            "zhihu-hotlist":  "https://developer.zhihu.com/api/mcp/hot_list/v1/sse",
        }
        for name, url in zhihu_endpoints.items():
            servers[name] = {
                "command": "npx",
                "args": ["-y", "mcp-remote", url, "--transport", "sse-only", "--header", hdr],
                "env": {},
            }

    if "readgzh" in keys:
        # 远程 MCP（url + Bearer header），微信公众号全文提取（ReadGZH-Agent）
        # 键文件 ReadGZH .txt 已被统一剥前缀（APIKey: 前缀去除 → 裸 token）
        servers["readgzh"] = {
            "url": "https://api.readgzh.site/mcp-server",
            "headers": {"Authorization": f"Bearer {keys['readgzh']}"},
        }

    # DeepWiki: keyless 远程 MCP（免 key 免 headers 免 env），GitHub 仓库文档问答
    # 一键连接（WorkBuddy MCP 管理页点 Trust 激活），代码/项目研究层补全
    servers["deepwiki"] = {
        "url": "https://mcp.deepwiki.com/mcp"
    }

    return servers


def _configure_stdio() -> None:
    """把 stdout/stderr 设为 UTF-8，避免 Windows GBK 控制台无法输出 ✓/← 等字符时崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main():
    _configure_stdio()
    ap = argparse.ArgumentParser(description="生成 ~/.workbuddy/mcp.json (从桌面 key 文件)")
    ap.add_argument("--desktop", default=None, help="桌面 key 文件目录")
    ap.add_argument("--out", default=os.path.expanduser(r"~/.workbuddy/mcp.json"))
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    ap.add_argument("--no-backup", action="store_true", help="不备份现有 mcp.json")
    args = ap.parse_args()

    desktop = args.desktop or detect_desktop()
    print(f"[i] Desktop 路径: {desktop}")
    if not os.path.isdir(desktop):
        print(f"[!] Desktop 不存在: {desktop}", file=sys.stderr)
        sys.exit(1)

    # 提取 key
    keys = {}
    missing = []
    for srv, fname in SERVER_KEYFILES.items():
        fpath = os.path.join(desktop, fname)
        if not os.path.isfile(fpath):
            missing.append((srv, fname))
            continue
        keep = srv in KEEP_PREFIX
        tok = extract_key(fpath, keep_prefix=keep)
        if tok:
            keys[srv] = tok
            print(f"  [✓] {srv:<12} ← {fname} ({len(tok)} chars)")
        else:
            missing.append((srv, fname))
            print(f"  [✗] {srv:<12} ← {fname} (无法提取 key)")

    if missing:
        print(f"[!] 未找到/未提取: {', '.join(m[0] for m in missing)}")

    if not keys:
        print("[!] 无任何 key / UA 可配置，退出", file=sys.stderr)
        sys.exit(1)

    new_servers = build_servers(keys)

    # 合并现有 mcp.json（保留脚本未管理的 server）
    existing = {}
    if os.path.isfile(args.out):
        try:
            with open(args.out, "r", encoding="utf-8") as f:
                existing = json.load(f).get("mcpServers", {})
        except (OSError, json.JSONDecodeError):
            existing = {}

    managed = set(new_servers.keys())
    preserved = {k: v for k, v in existing.items() if k not in managed}
    if preserved:
        print(f"[i] 保留现有未管理 server: {', '.join(preserved.keys())}")

    merged = {**preserved, **new_servers}
    out_obj = {"mcpServers": merged}

    if args.dry_run:
        print("\n[DRY-RUN] 将写入以下 mcp.json:")
        print(json.dumps(out_obj, indent=2, ensure_ascii=False))
        # 非 MCP key 也预览
        non_mcp_preview = {}
        for env_name, fname in NON_MCP_KEYFILES.items():
            fpath = os.path.join(desktop, fname)
            if os.path.isfile(fpath):
                tok = extract_key(fpath, keep_prefix=False)
                if tok:
                    non_mcp_preview[env_name] = f"{tok[:6]}…({len(tok)} chars)"
        if non_mcp_preview:
            print("[DRY-RUN] 将写入 dmr_keys.env:", non_mcp_preview)
        return

    # 备份
    if os.path.isfile(args.out) and not args.no_backup:
        ts = datetime.now().strftime("%Y%m%d-%H%M")
        bak = f"{args.out}.bak.{ts}"
        shutil.copy2(args.out, bak)
        print(f"[i] 已备份: {bak}")

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2, ensure_ascii=False)
    _restrict_to_owner(args.out)
    _warn_if_in_repo(args.out)
    print(f"\n[✓] 已生成 {args.out}")
    print(f"    共 {len(merged)} 个 server（本次管理 {len(new_servers)}，保留 {len(preserved)}）")

    # 非 MCP key：写入本机 dmr_keys.env（仅本机/跨机器同步用，绝不提交仓库）
    non_mcp = {}
    for env_name, fname in NON_MCP_KEYFILES.items():
        fpath = os.path.join(desktop, fname)
        if not os.path.isfile(fpath):
            continue
        tok = extract_key(fpath, keep_prefix=False)
        if tok:
            non_mcp[env_name] = tok
            print(f"  [✓] {env_name:<16} ← {fname}")
    if non_mcp:
        env_path = os.path.join(os.path.dirname(args.out), "dmr_keys.env")
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in non_mcp.items():
                f.write(f"{k}={v}\n")
        _restrict_to_owner(env_path)
        _warn_if_in_repo(env_path)
        print(f"[i] 已生成 {env_path}（本机专用，勿提交仓库）")

    print("\n下一步：WorkBuddy → MCP 服务管理 → 对每个新 server 点 Trust 激活")


if __name__ == "__main__":
    main()
