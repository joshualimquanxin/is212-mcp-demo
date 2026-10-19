"""The library's circulation system, exposed as an MCP server.

A stand-in for the internal system every organisation has and no vendor will
ever ship a connector for. Runs locally over stdio; Claude Code starts it from
the entry in .mcp.json. Fees are computed with the same libfines rules the
circulation system uses in production.

    python circulation_server.py
"""

import sqlite3
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from libfines.fines import late_fee  # noqa: E402

mcp = MCPServer("circulation")

# (loan_id, member, item_type, title, days_late) - today's overdue loans.
LOANS = [
    (101, "Aisha Rahman",  "book",     "The Lighthouse Keeper",        100),
    (102, "Ben Ong",       "dvd",      "Planet Earth II",               45),
    (103, "Chloe Tan",     "magazine", "National Geographic, Mar 2026", 160),
    (104, "Daniel Lee",    "book",     "Introduction to Algorithms",     10),
    (105, "Elena Petrova", "book",     "A Short History of Nearly Everything", 25),
    (106, "Farhan Ismail", "dvd",      "Spirited Away",                  12),
    (107, "Grace Lim",     "dvd",      "The Blue Planet",                19),
    (108, "Hiro Tanaka",   "magazine", "Wired, Jun 2026",                30),
    (109, "Ivy Chen",      "book",     "Thinking, Fast and Slow",         3),
    (110, "Ben Ong",       "book",     "The Pragmatic Programmer",       38),
    (111, "Grace Lim",     "magazine", "The Economist, Sep 2026",         8),
    (112, "Aisha Rahman",  "dvd",      "Cosmos",                          5),
]

# The SDK runs tool handlers on a worker thread, so let the connection cross threads.
db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE loans (id, member, item_type, title, days_late)")
db.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?)", LOANS)


@mcp.tool()
def overdue_loans() -> list[dict]:
    """Every loan currently overdue, with the late fee each member owes today."""
    rows = db.execute("SELECT * FROM loans ORDER BY days_late DESC").fetchall()
    return [
        {"loan_id": i, "member": m, "item_type": t, "title": title,
         "days_late": d, "fee_today": late_fee(t, d)}
        for i, m, t, title, d in rows
    ]


@mcp.resource("circulation://summary")
def summary() -> str:
    """Headline numbers for the circulation desk."""
    loans = overdue_loans()
    members = {loan["member"] for loan in loans}
    total = round(sum(loan["fee_today"] for loan in loans), 2)
    return f"{len(loans)} overdue loans across {len(members)} members; ${total:.2f} outstanding"


@mcp.prompt()
def impact_report(story: str) -> str:
    """Draft an impact note for a fee-rule change."""
    return (f"Using overdue_loans, explain which members' fees change under {story} "
            "and by how much. Two sentences, numbers first.")


if __name__ == "__main__":
    mcp.run(transport="stdio")
