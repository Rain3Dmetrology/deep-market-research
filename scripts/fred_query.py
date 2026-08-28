#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fred_query.py — 用本地 FRED_API_KEY 查询美联储经济数据 (FRED, https://fred.stlouisfed.org)

设计原则（与 setup_mcp.py 一致）：
  - 本脚本【不硬编码 key】；优先读环境变量 FRED_API_KEY，
    否则从 OneDrive 桌面 FREDAPIkey.txt 读取并自动剥前缀 (Rule 1)。
  - key 仅本机使用，绝不写进仓库 / SKILL.md。

用法：
  python fred_query.py GNPCA                      # 最新一条观测
  python fred_query.py GNPCA --limit 5            # 最近 5 条（倒序）
  python fred_query.py GNPCA --start 2010-01-01   # 起止区间
  python fred_query.py --search "gross domestic product" --limit 8   # 搜索系列

常见系列 ID（美国经济/金融）：
  GNPCA   实际 GDP（链式加权，十亿美元）
  GDP     名义 GDP
  CPIAUCSL  CPI 城市消费者（季调，月度）
  FEDFUNDS 联邦基金利率（有效，%）
  UNRATE  失业率（%）
  DGS10   10 年期国债收益率（%）
  PAYEMS  非农就业（千人）
  M2SL    M2 货币供给
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

PREFIX_RE = re.compile(r"^(?:APIKEY|APIkey|API\w*KEY|access\s*token|Key|Token)\s*[:：£º]?\s*", re.IGNORECASE)


def load_key() -> str | None:
    if os.environ.get("FRED_API_KEY"):
        return PREFIX_RE.sub("", os.environ["FRED_API_KEY"]).strip()
    for base in (
        os.path.expandvars(r"%OneDrive%\Desktop"),
        os.path.expanduser("~/OneDrive/Desktop"),
        os.path.expanduser("~/Desktop"),
    ):
        p = os.path.join(base, "FREDAPIkey.txt")
        if not os.path.isfile(p):
            continue
        with open(p, "rb") as f:
            raw = f.read()
        for enc in ("utf-8", "gbk", "latin-1"):
            try:
                txt = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            txt = raw.decode("utf-8", errors="ignore")
        first = None
        for line in txt.splitlines():
            line = line.strip()
            if not line:
                continue
            if first is None:
                first = line
            m = PREFIX_RE.match(line)
            if m:
                return line[m.end():].strip()
            if ":" not in line and "：" not in line:
                return line
        if first:
            return PREFIX_RE.sub("", first).strip()
    return None


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "dmr-fred/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[!] FRED API 返回 HTTP {e.code}: {e.reason}（请检查 series ID 与 API key）", file=sys.stderr)
        sys.exit(2)
    except TimeoutError:
        print("[!] FRED API 请求超时（30s），请稍后重试或检查网络", file=sys.stderr)
        sys.exit(2)
    except urllib.error.URLError as e:
        print(f"[!] 无法连接 FRED API（{e.reason}），请检查网络或代理设置", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError:
        print("[!] FRED API 返回了非 JSON 内容，无法解析", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description="查询 FRED 美联储经济数据")
    ap.add_argument("series", help="系列 ID（如 GNPCA）或 --search 关键词")
    ap.add_argument("--search", action="store_true", help="改为搜索系列而非取观测")
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--start", default=None, help="observation_start (YYYY-MM-DD)")
    ap.add_argument("--end", default=None, help="observation_end (YYYY-MM-DD)")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("FRED_API_KEY 未找到（请设环境变量或放桌面 FREDAPIkey.txt）", file=sys.stderr)
        sys.exit(1)

    base = "https://api.stlouisfed.org/fred"
    if args.search:
        q = urllib.parse.quote(args.series)
        url = f"{base}/series/search?search_text={q}&api_key={key}&file_type=json&limit={args.limit}"
        d = _get(url)
        rows = d.get("seriess", [])[: args.limit]
        if not rows:
            print("（无匹配系列）")
        for s in rows:
            print(f"{s['id']}\t{s.get('title', '')}\t[{s.get('frequency', '')}]")
    else:
        url = (f"{base}/series/observations?series_id={urllib.parse.quote(args.series, safe='')}&api_key={key}"
               f"&file_type=json&limit={args.limit}&sort_order=desc")
        if args.start:
            url += f"&observation_start={args.start}"
        if args.end:
            url += f"&observation_end={args.end}"
        d = _get(url)
        obs = d.get("observations", [])[: args.limit]
        if not obs:
            print("（无观测数据）")
        for o in obs:
            print(f"{o['date']}\t{o['value']}")


if __name__ == "__main__":
    main()
