"""Offline checks independent of external Flask dependencies.

This is NOT a substitute for the pytest suite.
"""
import ast
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1]
files = sorted(root.rglob("*.py"))
for path in files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print(f"Python AST: OK ({len(files)} files)")
try:
    import yaml
except ImportError:
    sys.exit(0)
yaml.safe_load((root / "docker-compose.yml").read_text(encoding="utf-8"))
print("docker-compose.yml YAML: OK")
