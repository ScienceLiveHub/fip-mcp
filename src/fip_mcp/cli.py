"""`fip-check` — the same operations as the MCP tools, from the shell, as JSON."""
from __future__ import annotations

import argparse
import json

from . import service


def main() -> None:
    p = argparse.ArgumentParser(prog="fip-check", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("communities")
    sub.add_parser("profile").add_argument("community")
    r = sub.add_parser("recommend")
    r.add_argument("community")
    r.add_argument("topic")
    c = sub.add_parser("check")
    c.add_argument("community")
    c.add_argument("target")
    x = sub.add_parser("crosswalk")
    x.add_argument("source")
    x.add_argument("target")
    a = p.parse_args()
    args = [v for k, v in vars(a).items() if k != "cmd"]
    print(json.dumps(getattr(service, a.cmd)(*args), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
