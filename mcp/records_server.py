#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""A small MCP server for the benchmark: support tickets, read one at a time.

It speaks MCP over stdio (one JSON-RPC message per line) using only the Python
standard library, so there is nothing to install. bin/run.py starts it for
every test session.

Tools:
  list_tickets(page)   ticket ids, 40 per page
  get_ticket(id)       one whole ticket

Both tools only read, and say so, so a client may run several calls at once.

If RECORDS_CALL_LOG is set, each tool call adds one JSON line to that file with
the time, this process's id, the tool and its arguments. bin/check.py uses it to
confirm that a run really fetched every ticket from one server.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from records import PER_PAGE, make_tickets  # noqa: E402

TICKETS = make_tickets()
BY_ID = {t["id"]: t for t in TICKETS}
PAGES = (len(TICKETS) + PER_PAGE - 1) // PER_PAGE
CALL_LOG = os.environ.get("RECORDS_CALL_LOG")
READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}

TOOLS = [
    {
        "name": "list_tickets",
        "description": (
            "List support ticket ids, 40 per page. Returns the page number, the number of "
            "pages and the ids on that page. It returns ids only: call get_ticket for a "
            "ticket's product, status and other fields."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Page number, starting at 1",
                }
            },
            "required": ["page"],
        },
        "annotations": READ_ONLY,
    },
    {
        "name": "get_ticket",
        "description": (
            "Get one support ticket by id, for example TCK-1001. Returns its customer, plan, "
            "product, status, priority, opened date, refund_requested amount and body text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Ticket id, such as TCK-1001"}
            },
            "required": ["id"],
        },
        "annotations": READ_ONLY,
    },
]


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def result(request_id, value):
    send({"jsonrpc": "2.0", "id": request_id, "result": value})


def error(request_id, code, text):
    send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": text}})


def text_result(value, failed=False):
    return {
        "content": [{"type": "text", "text": json.dumps(value, indent=2)}],
        "isError": failed,
    }


def log_call(name, args):
    if not CALL_LOG:
        return
    entry = {
        "ts": round(time.time(), 3),
        "pid": os.getpid(),
        "tool": name,
        "args": args,
    }
    with open(CALL_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def call_tool(name, args):
    log_call(name, args)
    if name == "list_tickets":
        page = args.get("page", 1)
        if not isinstance(page, int) or page < 1 or page > PAGES:
            return text_result(
                {"error": f"page must be a whole number from 1 to {PAGES}"}, failed=True
            )
        ids = [t["id"] for t in TICKETS[(page - 1) * PER_PAGE : page * PER_PAGE]]
        return text_result({"page": page, "pages": PAGES, "ids": ids})
    if name == "get_ticket":
        ticket = BY_ID.get(str(args.get("id", "")).strip())
        if ticket is None:
            return text_result({"error": "no ticket with that id"}, failed=True)
        return text_result(ticket)
    return text_result({"error": f"unknown tool: {name}"}, failed=True)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        method, request_id = message.get("method"), message.get("id")
        params = message.get("params") or {}
        if method == "initialize":
            result(
                request_id,
                {
                    "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "records", "version": "1.1.0"},
                },
            )
        elif method == "ping":
            result(request_id, {})
        elif method == "tools/list":
            result(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            result(
                request_id, call_tool(params.get("name"), params.get("arguments") or {})
            )
        elif request_id is not None:
            error(request_id, -32601, f"method not found: {method}")
        # Notifications, such as notifications/initialized, need no reply.


if __name__ == "__main__":
    main()
