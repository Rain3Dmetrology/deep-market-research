"""Tests for the key logic of scripts/readme_drift_check.py (R1-R7).

The drift gate is a top-level script (no importable functions), so these tests
exercise it two ways:
  1. end-to-end: run the script in a full repo COPY (tmp_path) after injecting
     a single drift mutation, asserting the expected gate error fires;
  2. pattern-level: replicate the R4/R7 regexes here and pin them against the
     real SKILL.md/CHANGELOG.md, with a literal-guard test verifying the script
     source still contains those exact regexes (kept in sync by this test).

Covers at minimum (audit H6 / P1-6 batch-2 item 5):
  - R7 version tokens aligned at all three locations (frontmatter, body header,
    reference-index history line);
  - R7 a single mismatched token triggers the gate warning/failure;
  - representative R1-R6 regex-parse cases.

Run:  pytest tests/test_readme_drift_check.py
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "readme_drift_check.py"

# --- regex mirrors of the script's R4/R7 patterns -----------------------------
# These MUST stay byte-identical to scripts/readme_drift_check.py; the guard
# test below fails if the script drifts away from them.
RE_CHANGELOG_TOP = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)
RE_R7_FRONTMATTER = re.compile(r'^version: "([\d.]+)"', re.MULTILINE)
RE_R7_BODY = re.compile(r"^> 版本: ([\d.]+) \|", re.MULTILINE)
RE_R7_HISTORY = re.compile(r"完整更新史（v[\d.]+ -> v([\d.]+)）")


def _changelog_top_version():
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = RE_CHANGELOG_TOP.search(changelog)
    assert m, "CHANGELOG.md top version unparseable"
    return m.group(1)


def _copy_repo(tmp_path):
    dst = tmp_path / "repo"
    shutil.copytree(
        REPO_ROOT, dst,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return dst


def _run_gate(cwd, extra_env=None):
    # stdin/stderr 显式 DEVNULL/合并：不继承父进程 stdio 句柄，
    # 规避 Windows 下父句柄不可继承时 Popen 报 WinError 6 的环境问题。
    env = None
    if extra_env:
        env = dict(os.environ)
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "scripts/readme_drift_check.py"],
        cwd=str(cwd), stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
        stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT, env=env,
    )


def _stale_version(top):
    # 构造一个合法的旧版本：patch 为 0 时向 minor 借位（2.8.0 -> 2.7.9），
    # 避免 patch-1 在 patch==0 时构造出非法令牌导致门禁正则误匹配。
    major, minor, patch = top.split(".")
    if int(patch) > 0:
        return "%s.%s.%d" % (major, minor, int(patch) - 1)
    return "%s.%d.9" % (major, int(minor) - 1)


def _mutate(path, old, new):
    text = Path(path).read_text(encoding="utf-8")
    assert old in text, "mutation anchor not found: %r" % old
    Path(path).write_text(text.replace(old, new), encoding="utf-8")


# --- pattern-level: R7 three-location alignment --------------------------------

def test_script_source_still_contains_the_pinned_regexes():
    # Guard: the mirrors above stay in sync with the actual script source.
    src = SCRIPT.read_text(encoding="utf-8")
    assert r'^version: "([\d.]+)"' in src
    assert r"^> 版本: ([\d.]+) \|" in src
    assert "完整更新史（v[\\d.]+ -> v([\\d.]+)）" in src
    assert r"^## \[(\d+\.\d+\.\d+)\]" in src


def test_r7_three_token_locations_aligned_with_changelog():
    # R7 核心：SKILL.md 三处版本令牌（frontmatter / 正文头 / 参考索引更新史行）
    # 均存在且全部等于 CHANGELOG 顶部版本。
    top = _changelog_top_version()
    skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = RE_R7_FRONTMATTER.findall(skill)
    body = RE_R7_BODY.findall(skill)
    history = RE_R7_HISTORY.findall(skill)
    assert frontmatter, "frontmatter version token missing"
    assert body, "body-header version token missing"
    assert history, "reference-index history version token missing"
    tokens = frontmatter + body + history
    assert set(tokens) == {top}, tokens


def test_gate_passes_on_current_repo(tmp_path):
    proc = _run_gate(_copy_repo(tmp_path))
    assert proc.returncode == 0, proc.stdout
    assert "README DRIFT GATE PASSED" in proc.stdout


# --- R7: a single mismatched token must fail the gate ---------------------------

def test_r7_single_mismatched_token_fails_gate(tmp_path):
    repo = _copy_repo(tmp_path)
    top = _changelog_top_version()
    stale = _stale_version(top)
    # 仅改动参考索引一处令牌（三处对齐 -> 一处失配）
    _mutate(repo / "SKILL.md",
            "完整更新史（v2.0.0 -> v%s）" % top,
            "完整更新史（v2.0.0 -> v%s）" % stale)
    proc = _run_gate(repo)
    assert proc.returncode == 1, proc.stdout
    assert "R7: SKILL.md version token %s" % stale in proc.stdout


# --- R1-R6 representative cases (one mutation each, expected error fires) -------

def test_r1_line_budget_exceeded(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n" * 250, encoding="utf-8")
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R1: README.md exceeds the 200-line budget" in proc.stdout


def test_r2_stale_template_count_claim(tmp_path):
    repo = _copy_repo(tmp_path)
    _mutate(repo / "README.md", "五套模板", "四套模板")
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R2: README.md lost the five-template claim" in proc.stdout


def test_r3_dead_skill_anchor(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n详见 SKILL.md 第八节。\n",
                      encoding="utf-8")
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R3: README.md references dead SKILL.md anchor" in proc.stdout


def test_r4_update_history_lags_changelog(tmp_path):
    repo = _copy_repo(tmp_path)
    top = _changelog_top_version()
    # 把 README 更新史行的终点版本改旧 -> 未达 CHANGELOG 顶部版本
    stale = _stale_version(top)
    _mutate(repo / "README.md",
            "v2.0.0 → v%s" % top,
            "v2.0.0 → v%s" % stale)
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R4: README.md update-history line does not reach CHANGELOG top version" in proc.stdout


def test_r5_banned_deleted_file_token(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n- release_body.md\n",
                      encoding="utf-8")
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R5: README.md still lists release_body.md" in proc.stdout


def test_r6_version_tagged_heading(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n## 特性（v2.8）\n",
                      encoding="utf-8")
    proc = _run_gate(repo)
    assert proc.returncode == 1
    assert "R6: README.md carries a version-tagged features heading" in proc.stdout


# --- Windows 受限编码控制台回归（cp1252/GBK） -----------------------------------
# 守护场景（对齐 validate_report / validate_param_card 的 _configure_stdio 先例）：
# 错误明细含中文（如 R3 死锚点 '第八节'、R6 '特性（v'），Windows cp1252/GBK 控制台
# 裸跑时 print 抛 UnicodeEncodeError，真实漂移失败与编码崩溃无法区分。
# 脚本入口的 _configure_stdio() 修复后：不得再抛编码异常，且退出码语义不变。

def test_cp1252_console_chinese_drift_error_does_not_crash(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    # 注入含中文的 R3 死锚点漂移（等价于 CI windows-latest 失败用例场景）
    readme.write_text(readme.read_text(encoding="utf-8") + "\n详见 SKILL.md 第八节。\n",
                      encoding="utf-8")
    proc = _run_gate(repo, extra_env={"PYTHONIOENCODING": "cp1252"})
    # 退出码语义不变：真实漂移失败仍为 1，而非编码崩溃的 traceback 退出
    assert proc.returncode == 1, proc.stdout
    assert "UnicodeEncodeError" not in proc.stdout
    assert "R3: README.md references dead SKILL.md anchor" in proc.stdout


def test_gbk_console_version_tagged_heading_error_does_not_crash(tmp_path):
    repo = _copy_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n## 特性（v2.8）\n",
                      encoding="utf-8")
    proc = _run_gate(repo, extra_env={"PYTHONIOENCODING": "gbk"})
    assert proc.returncode == 1, proc.stdout
    assert "UnicodeEncodeError" not in proc.stdout
    assert "R6: README.md carries a version-tagged features heading" in proc.stdout


def test_cp1252_console_clean_repo_still_passes(tmp_path):
    # 无漂移时：受限编码控制台下仍正常 PASS（退出码 0 语义不变）
    repo = _copy_repo(tmp_path)
    proc = _run_gate(repo, extra_env={"PYTHONIOENCODING": "cp1252"})
    assert proc.returncode == 0, proc.stdout
    assert "UnicodeEncodeError" not in proc.stdout
    assert "README DRIFT GATE PASSED" in proc.stdout
