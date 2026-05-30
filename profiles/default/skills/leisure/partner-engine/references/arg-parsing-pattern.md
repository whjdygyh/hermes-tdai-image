# `--base` Arg Parsing Pattern

## Context

Python scripts in this project accept `--base <PATH>` to override the default root directory.
A naive implementation using `sys.argv.index()` or filtering by `startswith('--')` fails when
the `--base` *value* (a file path) doesn't start with `--`, causing path leakage into arguments.

## The Naive Bug

```python
# ❌ BUGGY: --base value leaks into positional args
args = [a for a in sys.argv[1:] if not a.startswith('--')]
# With: script.py --base /some/path bot "content"
# args = ['/some/path', 'bot', 'content'] ← /some/path is NOT a positional arg!
```

```python
# ❌ ALSO BUGGY: sys.argv.index('--base') returns FIRST occurrence only
if '--base' in sys.argv:
    idx = sys.argv.index('--base')
    return sys.argv[idx + 1]
# The value is still in the unfiltered arg list for positional parsing
```

## The Fix: Consume as a Pair

```python
def get_base():
    """Parse --base from sys.argv, consuming flag+value as a pair."""
    for i, arg in enumerate(sys.argv):
        if arg == '--base' and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return fallback  # env var or expanduser

def get_positional_args():
    """Return strictly positional args, excluding --base VALUE."""
    result = []
    skip_next = False
    for arg in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg == '--base':
            skip_next = True   # consume the next arg as the value
            continue
        if arg.startswith('--'):
            continue
        result.append(arg)
    return result
```

## Why This Works

- `get_base()` iterates `sys.argv` to find `--base` and reads the next element as its value.
- `get_positional_args()` uses `skip_next` to skip the VALUE after `--base`, not just the flag.
- Order of `--base` doesn't matter.
- Multiple `--` flags are safe.
