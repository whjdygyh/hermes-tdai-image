#!/usr/bin/env python3
"""
verify_session_agent.py — 验证单个JSONL session文件的代理归属

用途：quick_session_scan.py 报告 found_lover_messages=true 时，
      用本脚本二次验证候选session文件是Lover还是Hot/Buffett/国学术数等。

用法：
  python3 verify_session_agent.py <path_to_jsonl>

输出：
  一行JSON verdict: {"agent": "LOVER"|"HOT"|"BUFFETT"|"BAZI"|"UNKNOWN",
                      "tools": ["browser_back", ...],
                      "file": "20260517_221745_...jsonl",
                      "confidence": "high"|"medium"|"low"}

JSONL格式预期（Hermes系统格式）：
  Line 1: {"role": "session_meta", "tools": [...], "model": "..."}
  Lines 2-N: {"role": "user", "content": "..."} / {"role": "assistant", "content": "...", "reasoning": "..."}

设计原则：
  • 无pipe-to-interpreter：直接 terminal("python3 script.py file") 即可
  • 无临时文件：读入后全在内存处理
  • 无外部依赖：纯标准库
  • 第一阶段仅读第一行（~<1KB），即使大session文件也秒出
  • 支持 --full 参数触发完整验证（读所有行做推理文本分析）

参考：
  partner-engine §3.4a 静默保护维护 → 跨代理验证
  references/cross-agent-verification-20260518.md
"""

import json
import sys

# ── Agent分类关键词 ──────────────────────────────────────────

# Hot代理的典型工具
HOT_TOOL_SIGNALS = {'browser', 'browser_back', 'browser_click', 'browser_navigate',
                    'web_search', 'web_fetch', 'page_down', 'html',
                    'page_up', 'click', 'scroll'}

# Lover代理的典型工具
LOVER_TOOL_SIGNALS = {'send_message', 'send_feishu_message', 'feishu',
                      'memory', 'skill_manage', 'append_msg_log'}

# 国学术数代理
BAZI_TOOL_SIGNALS = {'chinese_metaphysics', 'ba_zi', 'divination', 'bazi', 'zi_wei'}

# 金融代理
BUFFETT_TOOL_SIGNALS = {'stock', 'finance', 'market', 'ticker'}

# ── 助手推理文本关键词 ────────────────────────────────────────

HOT_REASONING_SIGNALS = [
    "i'm hot", "我是hot", "作为私人助理", "我是助理",
    "as hot", "老板", "hot replied",
]

LOVER_REASONING_SIGNALS = [
    "作为你的伴侣", "alexander", "lover replied",
    "我是alexander", "your lover",
]

BUFFETT_REASONING_SIGNALS = [
    "buffett", "barron", "金融", "财经", "股票",
]

BAZI_REASONING_SIGNALS = [
    "八字", "排盘", "断事", "国学术数", "周易", "命理",
]


def classify_by_tools(tool_names):
    """用工具列表做快速分类。返回 (agent, confidence)"""
    tool_set = set(t.lower() for t in tool_names)
    
    # Browser工具 → 高概率Hot
    if tool_set & HOT_TOOL_SIGNALS:
        if any('finance' in t or 'stock' in t for t in tool_names):
            return "BUFFETT", "high"
        return "HOT", "high"
    
    # 国学术数工具
    if tool_set & BAZI_TOOL_SIGNALS:
        return "BAZI", "high"
    
    # 金融工具
    if tool_set & BUFFETT_TOOL_SIGNALS:
        return "BUFFETT", "high"
    
    # Lover工具
    if tool_set & LOVER_TOOL_SIGNALS:
        return "LOVER", "high"
    
    # 空工具集 → 不确定
    if not tool_set:
        return "UNKNOWN", "low"
    
    return "UNKNOWN", "medium"


def classify_by_reasoning(text):
    """用助手推理文本做辅助分类。返回 (agent, confidence)"""
    text_lower = text.lower()
    
    for signal in HOT_REASONING_SIGNALS:
        if signal in text_lower:
            return "HOT", "medium"
    
    for signal in LOVER_REASONING_SIGNALS:
        if signal in text_lower:
            return "LOVER", "medium"
    
    for signal in BUFFETT_REASONING_SIGNALS:
        if signal in text_lower:
            return "BUFFETT", "medium"
    
    for signal in BAZI_REASONING_SIGNALS:
        if signal in text_lower:
            return "BAZI", "medium"
    
    return "UNKNOWN", "low"


def extract_tool_names(session_meta):
    """从session_meta提取工具名列表"""
    tools = session_meta.get('tools', [])
    names = []
    for t in tools:
        if isinstance(t, dict):
            fn = t.get('function', {})
            names.append(fn.get('name', str(t)))
        elif isinstance(t, str):
            names.append(t)
        else:
            names.append(str(t))
    return names


def load_session_file(filepath, full_scan=False):
    """读JSONL session文件，返回分析结果"""
    result = {
        'file': filepath.split('/')[-1],
        'tools': [],
        'agent': 'UNKNOWN',
        'confidence': 'low',
        'model': None,
        'sample_user_messages': [],
        'sample_assistant_messages': [],
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            role = data.get('role', '')
            
            if role == 'session_meta':
                result['tools'] = extract_tool_names(data)
                result['model'] = data.get('model')
                agent, conf = classify_by_tools(result['tools'])
                result['agent'] = agent
                result['confidence'] = conf
                
                if not full_scan and agent != 'UNKNOWN':
                    return result
                
            elif full_scan and role == 'assistant':
                content = data.get('content', '')
                reasoning = data.get('reasoning', '') or data.get('thinking', '') or ''
                combined = (reasoning + ' ' + content)[:500]
                result['sample_assistant_messages'].append(combined)
                
                if result['agent'] == 'UNKNOWN' or result['confidence'] == 'low':
                    agent, conf = classify_by_reasoning(combined)
                    if conf != 'low':
                        result['agent'] = agent
                        result['confidence'] = conf
                        if not full_scan:
                            return result
                
            elif role == 'user':
                content = data.get('content', '')
                if content and len(result['sample_user_messages']) < 2:
                    result['sample_user_messages'].append(content[:300])
    
    return result


def main():
    # Robust arg parsing: --full can appear before or after the filepath
    full_scan = '--full' in sys.argv
    
    # Find the filepath: first positional arg (non-flag) in sys.argv[1:]
    filepath = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            filepath = arg
            break
    
    if filepath is None:
        print("Usage: python3 verify_session_agent.py [--full] <path_to_jsonl>")
        sys.exit(1)
    
    result = load_session_file(filepath, full_scan=full_scan)
    
    print(json.dumps({
        'agent': result['agent'],
        'tools': result['tools'][:8],
        'file': result['file'],
        'model': result['model'],
        'confidence': result['confidence'],
        'full_scan': full_scan,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
