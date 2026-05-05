import json
import os
from pathlib import Path
from threading import Lock
from urllib import error, parse, request as urllib_request

from flask import Flask, jsonify, request

app = Flask(__name__)
application = app

LEADERBOARD_LIMIT = 10
LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
_leaderboard_lock = Lock()
_leaderboard_cache = []


QUESTIONS = [
    {
        "code": "def add(a, b):\n    return a - b",
        "options": ["Swap a and b", "Replace - with +", "Remove return", "Use print"],
        "correct": 1,
    },
    {
        "code": "nums = [1,2,3]\nprint(nums[3])",
        "options": ["Use nums[1]", "Add element", "Use nums[2]", "Remove print"],
        "correct": 2,
    },
    {
        "code": "for i in range(5):\n    if i = 2:\n        print(i)",
        "options": ["Indent print", "Replace = with ==", "Remove if", "Use >"],
        "correct": 1,
    },
    {
        "code": "let x = 5;\nif(x = 3){ console.log(x); }",
        "options": ["Use == or ===", "Remove if", "Use !==", "Change let to var"],
        "correct": 0,
    },
    {
        "code": "<div>\n  <p>Hello\n</div>",
        "options": ["Remove <p>", "Add <span>", "Close </p>", "Add class"],
        "correct": 2,
    },
    {
        "code": "def greet(name):\n    print('Hello ' + names)",
        "options": ["Use f-string", "Remove print", "Use name", "Add return"],
        "correct": 2,
    },
    {
        "code": "let arr = [1,2,3];\nconsole.log(arr[5]);",
        "options": ["Use arr[2]", "Change to object", "Add loop", "Remove console"],
        "correct": 0,
    },
    {
        "code": "<img src='a.png'></img>",
        "options": ["Use <image>", "Remove closing tag", "Add alt", "Wrap div"],
        "correct": 1,
    },
    {
        "code": "total = 0\nfor i in range(3):\n    total += 1\nprint(i)",
        "options": ["Print total", "Move print", "Use +=2", "Change loop"],
        "correct": 0,
    },
    {
        "code": "let x;\nconsole.log(x + 2);",
        "options": ["Remove +2", "Use const", "Initialize x", "Use var"],
        "correct": 2,
    },
    {
        "code": "def sum_list(lst):\n    for n in lst:\n        total += n\n    return total",
        "options": ["Use sum()", "Initialize total = 0", "Remove return", "Use list"],
        "correct": 1,
    },
    {
        "code": "let count = 0;\nwhile(count < 5){\n  console.log(count);\n}",
        "options": ["Use for loop", "Change <", "Remove log", "Increment count"],
        "correct": 3,
    },
    {
        "code": "<ul>\n  <li>One\n  <li>Two</li>\n</ul>",
        "options": ["Use <ol>", "Close first <li>", "Remove li", "Add div"],
        "correct": 1,
    },
    {
        "code": "def find_max(a,b):\n    if a > b:\n        return b\n    return a",
        "options": ["Swap returns", "Add else", "Use >=", "Remove return"],
        "correct": 0,
    },
    {
        "code": "async function load(){\n  let data = fetch('/api');\n  console.log(await data.json());\n}",
        "options": ["Use then()", "Remove async", "Await fetch()", "Move console"],
        "correct": 2,
    },
    {
        "code": "<table>\n<tr>\n<td>Hi\n</table>",
        "options": ["Add tbody", "Close td/tr", "Remove tr", "Use th"],
        "correct": 1,
    },
    {
        "code": "nums=[1,2,3]\nfor i in range(len(nums)+1):\n print(nums[i])",
        "options": ["Use len(nums)", "Use i-1", "Change list", "Remove loop"],
        "correct": 0,
    },
    {
        "code": "let x=10;\nfunction t(){\n console.log(x);\n let x=5;\n}",
        "options": ["Use var", "Rename x", "Move declaration", "Remove console"],
        "correct": 2,
    },
    {
        "code": "<div><span>Hi</div></span>",
        "options": ["Add class", "Remove span", "Fix nesting", "Use p"],
        "correct": 2,
    },
    {
        "code": "def sub(a,b):\n result=a-b\nprint(result)",
        "options": ["Return result", "Indent print", "Use +", "Rename"],
        "correct": 1,
    },
    {
        "code": "async function f(){\n const r=await fetch('/');\n return r.json();\n}\nconsole.log(f());",
        "options": ["Use text()", "Remove return", "Await f()", "Move log"],
        "correct": 2,
    },
    {
        "code": "def merge(a,b):\n c=a\n c.extend(b)\n return a",
        "options": ["Use append", "Copy list", "Return c", "Remove extend"],
        "correct": 2,
    },
    {
        "code": "<form>\n<button>Go\n</form>",
        "options": ["Use submit", "Add label", "Close button", "Add input"],
        "correct": 2,
    },
    {
        "code": "let a=[1,2,3];\nfor(let i=0;i<=a.length;i++){\n console.log(a[i]);\n}",
        "options": ["Use < instead of <=", "Use i--", "Change array", "Remove loop"],
        "correct": 0,
    },
    {
        "code": "def calc(x):\n if x>0:\n  y=x\n return y",
        "options": ["Initialize y", "Add else", "Return x", "Remove if"],
        "correct": 0,
    },
    {
        "code": "<div>\n<p>A</p>\n<p>B\n</div>",
        "options": ["Use span", "Remove p", "Close second p", "Add br"],
        "correct": 2,
    },
    {
        "code": "function loop(){\n for(var i=0;i<3;i++){\n  setTimeout(()=>console.log(i),0);\n }\n}",
        "options": ["Remove timeout", "Use let", "Change <", "Use i--"],
        "correct": 1,
    },
    {
        "code": "def divide(a,b):\n if b==0:\n  print('err')\n return a/b",
        "options": ["Remove if", "Use ab", "Return after error", "Change =="],
        "correct": 2,
    },
    {
        "code": "<h1>Hi</h2>",
        "options": ["Use h3", "Remove h1", "Add div", "Fix closing tag"],
        "correct": 3,
    },
]


def _sanitize_entry(name, score):
    clean_name = (name or "").strip()
    if not clean_name:
        raise ValueError("Name is required.")
    if len(clean_name) > 24:
        raise ValueError("Name must be 24 characters or less.")
    if not isinstance(score, int):
        raise ValueError("Score must be an integer.")
    if score < 0:
        raise ValueError("Score must be zero or higher.")
    return {"name": clean_name, "score": score}


def _supabase_config():
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    table = os.getenv("SUPABASE_LEADERBOARD_TABLE", "leaderboard_entries")
    if not url or not key:
        return None
    return {"url": url, "key": key, "table": table}


def _supabase_request(method, path, params=None, payload=None):
    cfg = _supabase_config()
    if not cfg:
        raise RuntimeError("Supabase is not configured.")

    base_url = f"{cfg['url']}/rest/v1/{cfg['table']}"
    query = f"?{parse.urlencode(params)}" if params else ""
    url = f"{base_url}{query}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "apikey": cfg["key"],
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    if method == "POST":
        headers["Prefer"] = "return=representation"

    req = urllib_request.Request(url=url, data=body, headers=headers, method=method)
    with urllib_request.urlopen(req, timeout=8) as response:
        text = response.read().decode("utf-8") or "[]"
        return json.loads(text)


def _load_local_leaderboard():
    global _leaderboard_cache
    if _leaderboard_cache:
        return _leaderboard_cache

    if not LEADERBOARD_FILE.exists():
        _leaderboard_cache = []
        return _leaderboard_cache

    try:
        _leaderboard_cache = json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _leaderboard_cache = []
    return _leaderboard_cache


def _write_local_leaderboard(entries):
    try:
        LEADERBOARD_FILE.write_text(json.dumps(entries), encoding="utf-8")
    except OSError:
        pass


def _get_local_entries():
    entries = _load_local_leaderboard()
    sorted_entries = sorted(entries, key=lambda item: (-item["score"], item.get("created_at", "")))
    return sorted_entries[:LEADERBOARD_LIMIT]


def _add_local_entry(entry):
    with _leaderboard_lock:
        entries = _load_local_leaderboard()
        entries.append(
            {
                "name": entry["name"],
                "score": entry["score"],
                "created_at": entry.get("created_at", ""),
            }
        )
        entries = sorted(entries, key=lambda item: (-item["score"], item.get("created_at", "")))[:100]
        _leaderboard_cache[:] = entries
        _write_local_leaderboard(entries)


def _leaderboard_from_supabase():
    params = {
        "select": "name,score,created_at",
        "order": "score.desc,created_at.asc",
        "limit": str(LEADERBOARD_LIMIT),
    }
    rows = _supabase_request("GET", "leaderboard", params=params)
    return [{"name": row["name"], "score": int(row["score"])} for row in rows]


def _insert_supabase_entry(entry):
    row = _supabase_request("POST", "leaderboard", payload={"name": entry["name"], "score": entry["score"]})
    return row


@app.route("/")
@app.route("/api")
@app.route("/api/questions")
def handler():
    return jsonify(QUESTIONS)


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        return jsonify(_leaderboard_from_supabase())
    except (RuntimeError, error.URLError, error.HTTPError, TimeoutError, ValueError):
        return jsonify(_get_local_entries())


@app.route("/api/leaderboard", methods=["POST"])
def post_leaderboard():
    body = request.get_json(silent=True) or {}
    try:
        entry = _sanitize_entry(body.get("name"), body.get("score"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        _insert_supabase_entry(entry)
        leaderboard = _leaderboard_from_supabase()
        return jsonify({"ok": True, "leaderboard": leaderboard}), 201
    except (RuntimeError, error.URLError, error.HTTPError, TimeoutError, ValueError):
        _add_local_entry(entry)
        return jsonify({"ok": True, "leaderboard": _get_local_entries(), "storage": "local-fallback"}), 201
