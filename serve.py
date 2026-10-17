import http.server
import socketserver
import webbrowser
import os
import urllib.request
import urllib.error
import urllib.parse
import json
import sqlite3
import hashlib
import secrets
import re
import html
import time
from datetime import datetime, timezone, timedelta

PORT = int(os.environ.get("PORT", 3000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIRECTORY, "findit.db")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
UPPER_REGEX = re.compile(r"[A-Z]")
LOWER_REGEX = re.compile(r"[a-z]")
DIGIT_REGEX = re.compile(r"[0-9]")
SPECIAL_REGEX = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]")

COMMON_STOP_WORDS = {
    "a", "an", "and", "at", "by", "found", "for", "from", "i", "in", "is",
    "it", "lost", "near", "of", "on", "the", "to", "with", "my", "this", "that"
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tokenize(text: str) -> set:
    if not text:
        return set()
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    words = cleaned.split()
    return {w for w in words if len(w) > 1 and w not in COMMON_STOP_WORDS}

def jaccard_similarity(text1: str, text2: str) -> float:
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return float(len(intersection)) / float(len(union))

def compute_match_score(lost_row, found_row) -> float:
    cat_score = 1.0 if (lost_row['category'] or '').lower() == (found_row['category'] or '').lower() else 0.0
    text_score = jaccard_similarity(
        f"{lost_row['title']} {lost_row['description']}",
        f"{found_row['title']} {found_row['description']}"
    )
    loc_score = 1.0 if (lost_row['location'] or '').lower() == (found_row['location'] or '').lower() else jaccard_similarity(lost_row['location'], found_row['location'])
    
    days_apart = 0.0
    try:
        d1 = datetime.fromisoformat(lost_row['item_date'].replace('Z', '+00:00'))
        d2 = datetime.fromisoformat(found_row['item_date'].replace('Z', '+00:00'))
        days_apart = abs((d2 - d1).total_seconds()) / 86400.0
    except Exception:
        pass
    time_score = max(0.0, 1.0 - (days_apart / 30.0))
    
    return round((0.25 * cat_score) + (0.45 * text_score) + (0.20 * loc_score) + (0.10 * time_score), 3)

def run_auto_match_for_item(conn, item_id: int):
    c = conn.cursor()
    target = c.execute("SELECT * FROM findit_items WHERE id = ?", (item_id,)).fetchone()
    if not target:
        return
    opp_type = "FOUND" if target['type'] == 'LOST' else "LOST"
    candidates = c.execute("SELECT * FROM findit_items WHERE type = ? AND status != 'RETURNED'", (opp_type,)).fetchall()
    
    for cand in candidates:
        lost = target if target['type'] == 'LOST' else cand
        found = cand if target['type'] == 'LOST' else target
        score = compute_match_score(lost, found)
        if score >= 0.34:
            c.execute("""
                INSERT INTO findit_matches (lost_item_id, found_item_id, score, verified, lost_confirmed, found_confirmed)
                VALUES (?, ?, ?, 0, 0, 0)
                ON CONFLICT(lost_item_id, found_item_id) DO UPDATE SET score = excluded.score
            """, (lost['id'], found['id'], score))
            c.execute("UPDATE findit_items SET status = 'MATCHED' WHERE id IN (?, ?) AND status = 'OPEN'", (lost['id'], found['id']))
    conn.commit()

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS findit_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            reporter TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            item_date TEXT NOT NULL,
            photo_url TEXT,
            private_detail TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'OPEN',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS findit_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lost_item_id INTEGER NOT NULL,
            found_item_id INTEGER NOT NULL,
            score REAL NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            lost_confirmed INTEGER NOT NULL DEFAULT 0,
            found_confirmed INTEGER NOT NULL DEFAULT 0,
            attempts_count INTEGER NOT NULL DEFAULT 0,
            locked_until TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(lost_item_id, found_item_id)
        );

        CREATE TABLE IF NOT EXISTS findit_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            text TEXT NOT NULL,
            sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS findit_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS findit_sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS findit_auth_attempts (
            ip TEXT PRIMARY KEY,
            attempts INTEGER NOT NULL DEFAULT 1,
            last_attempt TEXT NOT NULL
        );
        """)
        
        c = conn.cursor()
        def add_column_if_missing(table, col, col_def):
            cols = [r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
            if col not in cols:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
                conn.commit()
                
        add_column_if_missing("findit_items", "user_id", "INTEGER")
        add_column_if_missing("findit_sessions", "expires_at", "TEXT")
        add_column_if_missing("findit_matches", "attempts_count", "INTEGER NOT NULL DEFAULT 0")
        add_column_if_missing("findit_matches", "locked_until", "TEXT")
        
        c.execute("SELECT COUNT(*) FROM findit_items")
        if c.fetchone()[0] == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            c.execute("""
                INSERT INTO findit_items (type, reporter, title, category, description, location, item_date, private_detail, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("LOST", "Anaya S.", "Brown leather wallet", "Accessories", "Slim brown leather wallet with a brass snap closure.", "Central Library, East Entrance", now_iso, "small blue stitch", "OPEN"))
            
            c.execute("""
                INSERT INTO findit_items (type, reporter, title, category, description, location, item_date, private_detail, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("FOUND", "Rohan P.", "Found brown card wallet", "Accessories", "Brown leather wallet with brass snap, found by the library east entrance.", "Central Library, East Entrance", now_iso, "two cards inside", "OPEN"))
            conn.commit()

        c.execute("SELECT COUNT(*) FROM findit_matches")
        if c.fetchone()[0] == 0:
            c.execute("SELECT id FROM findit_items")
            all_items = [r[0] for r in c.fetchall()]
            if len(all_items) >= 2:
                run_auto_match_for_item(conn, all_items[0])

def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    pwd_bytes = password.encode('utf-8')
    key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt, 65536, dklen=32)
    return key.hex()

def generate_salt() -> str:
    return secrets.token_hex(16)

def verify_password(password: str, stored_hash: str, stored_salt_hex: str) -> bool:
    computed = hash_password(password, stored_salt_hex)
    return secrets.compare_digest(computed, stored_hash)

JAVA_AVAILABLE = False
LAST_JAVA_CHECK = 0.0

def is_java_alive() -> bool:
    global JAVA_AVAILABLE, LAST_JAVA_CHECK
    now = time.time()
    if now - LAST_JAVA_CHECK < 5.0:
        return JAVA_AVAILABLE
    LAST_JAVA_CHECK = now
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.04)
    try:
        s.connect(('127.0.0.1', 8080))
        s.close()
        JAVA_AVAILABLE = True
    except Exception:
        JAVA_AVAILABLE = False
    return JAVA_AVAILABLE

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Security headers for every response
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Auth-Token')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api'):
            self.proxy_or_handle_api()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api'):
            self.proxy_or_handle_api()
        else:
            self.send_error(405, "Method Not Allowed")

    def proxy_or_handle_api(self):
        body = None
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > 0:
            body = self.rfile.read(content_len)

        if not is_java_alive():
            self.handle_python_api(body)
            return

        target_url = f"http://localhost:8080{self.path}"
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
        req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp.read())
                return
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                self.send_header(k, v)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(e.read())
            return
        except Exception:
            # Fallback to internal Python SQLite API Server
            self.handle_python_api(body)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Auth-Token')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_json_error(self, message, status=400):
        self.send_json({"error": message}, status=status)

    def get_current_user(self):
        auth_hdr = self.headers.get('Authorization', '')
        custom_hdr = self.headers.get('X-Auth-Token', '')
        token = None
        if auth_hdr.lower().startswith('bearer '):
            token = auth_hdr[7:].strip()
        elif custom_hdr:
            token = custom_hdr.strip()

        if not token:
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            row = conn.execute("""
                SELECT u.id, u.full_name, u.email, u.created_at, s.expires_at
                FROM findit_users u
                JOIN findit_sessions s ON u.id = s.user_id
                WHERE s.token = ?
            """, (token,)).fetchone()

            if not row:
                return None

            if row["expires_at"] and row["expires_at"] < now_iso:
                conn.execute("DELETE FROM findit_sessions WHERE token = ?", (token,))
                conn.commit()
                return None

            return {
                "id": row["id"],
                "fullName": row["full_name"],
                "email": row["email"],
                "createdAt": row["created_at"]
            }

    def handle_python_api(self, raw_body):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        body_json = {}
        if raw_body:
            try:
                body_json = json.loads(raw_body.decode('utf-8'))
            except Exception:
                pass

        # Routes
        if path == '/api/healthz' and self.command == 'GET':
            self.send_json({"status": "healthy", "service": "findit-python-sqlite"})
            return

        if path == '/api/dashboard' and self.command == 'GET':
            with get_db() as conn:
                c = conn.cursor()
                total = c.execute("SELECT COUNT(*) FROM findit_items").fetchone()[0]
                lost = c.execute("SELECT COUNT(*) FROM findit_items WHERE type = 'LOST'").fetchone()[0]
                found = c.execute("SELECT COUNT(*) FROM findit_items WHERE type = 'FOUND'").fetchone()[0]
                open_cnt = c.execute("SELECT COUNT(*) FROM findit_items WHERE status = 'OPEN'").fetchone()[0]
                potential = c.execute("SELECT COUNT(*) FROM findit_matches WHERE verified = 0").fetchone()[0]
                returned = c.execute("SELECT COUNT(*) FROM findit_matches WHERE lost_confirmed = 1 AND found_confirmed = 1").fetchone()[0]
                self.send_json({
                    "totalReports": total,
                    "lostReports": lost,
                    "foundReports": found,
                    "openReports": open_cnt,
                    "potentialMatches": potential,
                    "returnedItems": returned
                })
                return

        if path == '/api/items' and self.command == 'GET':
            type_filter = query.get('type', [None])[0]
            search_filter = query.get('q', [None])[0]
            sql = "SELECT * FROM findit_items WHERE 1=1"
            params = []
            if type_filter:
                sql += " AND type = ?"
                params.append(type_filter.upper())
            if search_filter:
                sql += " AND (title LIKE ? OR description LIKE ? OR location LIKE ? OR category LIKE ? OR reporter LIKE ?)"
                term = f"%{search_filter.strip()}%"
                params.extend([term, term, term, term, term])
            sql += " ORDER BY id DESC"

            with get_db() as conn:
                rows = conn.execute(sql, params).fetchall()
                items = []
                for r in rows:
                    items.append({
                        "id": r["id"],
                        "type": r["type"],
                        "reporter": r["reporter"],
                        "title": r["title"],
                        "category": r["category"],
                        "description": r["description"],
                        "location": r["location"],
                        "itemDate": r["item_date"],
                        "photoUrl": r["photo_url"],
                        "status": r["status"],
                        "createdAt": r["created_at"]
                    })
                self.send_json(items)
                return

        if path == '/api/items' and self.command == 'POST':
            current_user = self.get_current_user()
            user_id = current_user['id'] if current_user else None

            title = (body_json.get('title') or '').strip()
            item_type = (body_json.get('type') or '').strip().upper()
            reporter = (body_json.get('reporter') or (current_user['fullName'] if current_user else '')).strip()
            category = (body_json.get('category') or '').strip()
            description = (body_json.get('description') or '').strip()
            location = (body_json.get('location') or '').strip()
            item_date = (body_json.get('itemDate') or '').strip() or datetime.now(timezone.utc).isoformat()
            photo_url = (body_json.get('photoUrl') or '').strip() or None
            private_detail = (body_json.get('privateDetail') or '').strip()

            if not title or not item_type or not reporter or not category or not description or not location:
                self.send_json_error("Please fill in all required report fields.")
                return

            if photo_url and not (photo_url.startswith('http://') or photo_url.startswith('https://')):
                self.send_json_error("Photo URL must start with http:// or https://")
                return

            # Sanitize text
            safe_title = html.escape(title[:140])
            safe_reporter = html.escape(reporter[:100])
            safe_category = html.escape(category[:60])
            safe_desc = html.escape(description[:1000])
            safe_loc = html.escape(location[:180])

            with get_db() as conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO findit_items (user_id, type, reporter, title, category, description, location, item_date, photo_url, private_detail, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """, (user_id, item_type, safe_reporter, safe_title, safe_category, safe_desc, safe_loc, item_date, photo_url, private_detail))
                conn.commit()
                new_id = c.lastrowid
                
                # Trigger real matching algorithm in background
                run_auto_match_for_item(conn, new_id)

                row = conn.execute("SELECT * FROM findit_items WHERE id = ?", (new_id,)).fetchone()
                self.send_json({
                    "id": row["id"],
                    "type": row["type"],
                    "reporter": row["reporter"],
                    "title": row["title"],
                    "category": row["category"],
                    "description": row["description"],
                    "location": row["location"],
                    "itemDate": row["item_date"],
                    "photoUrl": row["photo_url"],
                    "status": row["status"],
                    "createdAt": row["created_at"]
                }, status=201)
                return

        # MATCHES ENDPOINTS
        if path == '/api/matches' and self.command == 'GET':
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT m.*,
                           l.title as lost_title, l.description as lost_desc, l.reporter as lost_reporter, l.location as lost_loc, l.item_date as lost_date, l.photo_url as lost_photo,
                           f.title as found_title, f.description as found_desc, f.reporter as found_reporter, f.location as found_loc, f.item_date as found_date, f.photo_url as found_photo
                    FROM findit_matches m
                    JOIN findit_items l ON m.lost_item_id = l.id
                    JOIN findit_items f ON m.found_item_id = f.id
                    ORDER BY m.score DESC, m.id DESC
                """).fetchall()
                result = []
                for r in rows:
                    result.append({
                        "id": r["id"],
                        "lostItemId": r["lost_item_id"],
                        "foundItemId": r["found_item_id"],
                        "score": r["score"],
                        "scorePercent": int(round(r["score"] * 100)),
                        "verified": bool(r["verified"]),
                        "lostConfirmed": bool(r["lost_confirmed"]),
                        "foundConfirmed": bool(r["found_confirmed"]),
                        "attemptsCount": r["attempts_count"],
                        "createdAt": r["created_at"],
                        "lostItem": {
                            "id": r["lost_item_id"],
                            "title": r["lost_title"],
                            "description": r["lost_desc"],
                            "reporter": r["lost_reporter"],
                            "location": r["lost_loc"],
                            "date": r["lost_date"],
                            "photoUrl": r["lost_photo"]
                        },
                        "foundItem": {
                            "id": r["found_item_id"],
                            "title": r["found_title"],
                            "description": r["found_desc"],
                            "reporter": r["found_reporter"],
                            "location": r["found_loc"],
                            "date": r["found_date"],
                            "photoUrl": r["found_photo"]
                        }
                    })
                self.send_json(result)
                return

        match_id_match = re.match(r"^/api/matches/(\d+)$", path)
        if match_id_match and self.command == 'GET':
            m_id = int(match_id_match.group(1))
            with get_db() as conn:
                r = conn.execute("""
                    SELECT m.*,
                           l.title as lost_title, l.description as lost_desc, l.reporter as lost_reporter, l.location as lost_loc, l.item_date as lost_date, l.photo_url as lost_photo,
                           f.title as found_title, f.description as found_desc, f.reporter as found_reporter, f.location as found_loc, f.item_date as found_date, f.photo_url as found_photo
                    FROM findit_matches m
                    JOIN findit_items l ON m.lost_item_id = l.id
                    JOIN findit_items f ON m.found_item_id = f.id
                    WHERE m.id = ?
                """, (m_id,)).fetchone()
                if not r:
                    self.send_json_error("Match not found.", status=404)
                    return
                self.send_json({
                    "id": r["id"],
                    "lostItemId": r["lost_item_id"],
                    "foundItemId": r["found_item_id"],
                    "score": r["score"],
                    "scorePercent": int(round(r["score"] * 100)),
                    "verified": bool(r["verified"]),
                    "lostConfirmed": bool(r["lost_confirmed"]),
                    "foundConfirmed": bool(r["found_confirmed"]),
                    "attemptsCount": r["attempts_count"],
                    "createdAt": r["created_at"],
                    "lostItem": {
                        "id": r["lost_item_id"],
                        "title": r["lost_title"],
                        "description": r["lost_desc"],
                        "reporter": r["lost_reporter"],
                        "location": r["lost_loc"],
                        "date": r["lost_date"],
                        "photoUrl": r["lost_photo"]
                    },
                    "foundItem": {
                        "id": r["found_item_id"],
                        "title": r["found_title"],
                        "description": r["found_desc"],
                        "reporter": r["found_reporter"],
                        "location": r["found_loc"],
                        "date": r["found_date"],
                        "photoUrl": r["found_photo"]
                    }
                })
                return

        match_verify_match = re.match(r"^/api/matches/(\d+)/verify$", path)
        if match_verify_match and self.command == 'POST':
            m_id = int(match_verify_match.group(1))
            submitted_detail = (body_json.get('privateDetail') or '').strip()
            if not submitted_detail:
                self.send_json_error("Private detail is required for verification.", status=400)
                return

            with get_db() as conn:
                m = conn.execute("SELECT * FROM findit_matches WHERE id = ?", (m_id,)).fetchone()
                if not m:
                    self.send_json_error("Match not found.", status=404)
                    return

                # Lockout enforcement
                locked_until = m["locked_until"]
                now_utc = datetime.now(timezone.utc)
                if locked_until:
                    try:
                        lock_dt = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
                        if now_utc < lock_dt:
                            mins_left = int((lock_dt - now_utc).total_seconds() / 60) + 1
                            self.send_json({
                                "verified": False,
                                "error": f"Verification is locked due to too many failed attempts. Try again in {mins_left} minutes.",
                                "locked": True,
                                "remainingAttempts": 0
                            }, status=429)
                            return
                        else:
                            conn.execute("UPDATE findit_matches SET attempts_count = 0, locked_until = NULL WHERE id = ?", (m_id,))
                            conn.commit()
                    except Exception:
                        pass

                if m["verified"] == 1:
                    self.send_json({
                        "verified": True,
                        "message": "Ownership already verified. Direct channel is active."
                    })
                    return

                lost_item = conn.execute("SELECT private_detail FROM findit_items WHERE id = ?", (m["lost_item_id"],)).fetchone()
                expected = (lost_item["private_detail"] if lost_item else "") or ""

                def norm(s):
                    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

                expected_norm = norm(expected)
                actual_norm = norm(submitted_detail)

                is_correct = bool(expected_norm) and (
                    secrets.compare_digest(expected_norm, actual_norm) or
                    (len(expected_norm) >= 4 and expected_norm in actual_norm) or
                    (len(actual_norm) >= 4 and actual_norm in expected_norm)
                )

                if is_correct:
                    conn.execute("UPDATE findit_matches SET verified = 1, attempts_count = 0, locked_until = NULL WHERE id = ?", (m_id,))
                    conn.commit()
                    self.send_json({
                        "verified": True,
                        "message": "✓ Verification Successful! Secret detail matches owner report. Direct channel opened."
                    })
                    return
                else:
                    new_attempts = (m["attempts_count"] or 0) + 1
                    if new_attempts >= 5:
                        lock_time = (now_utc + timedelta(hours=24)).isoformat()
                        conn.execute("UPDATE findit_matches SET attempts_count = ?, locked_until = ? WHERE id = ?", (new_attempts, lock_time, m_id))
                        conn.commit()
                        self.send_json({
                            "verified": False,
                            "error": "✕ Incorrect detail. Maximum 5 attempts reached. Verification locked for 24 hours to protect owner property.",
                            "locked": True,
                            "remainingAttempts": 0
                        }, status=429)
                        return
                    else:
                        conn.execute("UPDATE findit_matches SET attempts_count = ? WHERE id = ?", (new_attempts, m_id))
                        conn.commit()
                        remaining = 5 - new_attempts
                        self.send_json({
                            "verified": False,
                            "error": f"✕ That detail does not match the private record. {remaining} attempt{'s' if remaining != 1 else ''} remaining.",
                            "locked": False,
                            "remainingAttempts": remaining
                        }, status=400)
                        return

        match_msg_match = re.match(r"^/api/matches/(\d+)/messages$", path)
        if match_msg_match and self.command == 'GET':
            m_id = int(match_msg_match.group(1))
            with get_db() as conn:
                m = conn.execute("SELECT verified FROM findit_matches WHERE id = ?", (m_id,)).fetchone()
                if not m:
                    self.send_json_error("Match not found.", status=404)
                    return
                if not m["verified"]:
                    self.send_json_error("Verify ownership before accessing this chat channel.", status=403)
                    return

                rows = conn.execute("SELECT * FROM findit_messages WHERE match_id = ? ORDER BY id ASC", (m_id,)).fetchall()
                messages = []
                for r in rows:
                    messages.append({
                        "id": r["id"],
                        "matchId": r["match_id"],
                        "role": r["role"],
                        "senderName": r["sender_name"],
                        "text": r["text"],
                        "sentAt": r["sent_at"]
                    })
                self.send_json(messages)
                return

        if match_msg_match and self.command == 'POST':
            m_id = int(match_msg_match.group(1))
            with get_db() as conn:
                m = conn.execute("SELECT verified FROM findit_matches WHERE id = ?", (m_id,)).fetchone()
                if not m:
                    self.send_json_error("Match not found.", status=404)
                    return
                if not m["verified"]:
                    self.send_json_error("Verify ownership before posting messages.", status=403)
                    return

                role = (body_json.get('role') or 'OWNER').strip().upper()
                sender_name = (body_json.get('senderName') or 'Anonymous User').strip()[:100]
                text = (body_json.get('text') or '').strip()

                if not text:
                    self.send_json_error("Message text cannot be empty.", status=400)
                    return
                if len(text) > 1000:
                    self.send_json_error("Message is too long (max 1000 characters).", status=400)
                    return

                clean_text = html.escape(text)
                clean_sender = html.escape(sender_name)

                c = conn.cursor()
                c.execute("""
                    INSERT INTO findit_messages (match_id, role, sender_name, text)
                    VALUES (?, ?, ?, ?)
                """, (m_id, role, clean_sender, clean_text))
                conn.commit()
                new_msg_id = c.lastrowid
                row = conn.execute("SELECT * FROM findit_messages WHERE id = ?", (new_msg_id,)).fetchone()
                self.send_json({
                    "id": row["id"],
                    "matchId": row["match_id"],
                    "role": row["role"],
                    "senderName": row["sender_name"],
                    "text": row["text"],
                    "sentAt": row["sent_at"]
                }, status=201)
                return

        match_confirm_match = re.match(r"^/api/matches/(\d+)/confirm-return$", path)
        if match_confirm_match and self.command == 'POST':
            m_id = int(match_confirm_match.group(1))
            role = (body_json.get('role') or 'OWNER').strip().upper()
            if role not in ('OWNER', 'FINDER'):
                self.send_json_error("Role must be OWNER or FINDER.", status=400)
                return

            with get_db() as conn:
                m = conn.execute("SELECT * FROM findit_matches WHERE id = ?", (m_id,)).fetchone()
                if not m:
                    self.send_json_error("Match not found.", status=404)
                    return
                if not m["verified"]:
                    self.send_json_error("Cannot confirm return before ownership verification.", status=403)
                    return

                if role == 'OWNER':
                    conn.execute("UPDATE findit_matches SET lost_confirmed = 1 WHERE id = ?", (m_id,))
                else:
                    conn.execute("UPDATE findit_matches SET found_confirmed = 1 WHERE id = ?", (m_id,))
                conn.commit()

                updated = conn.execute("SELECT * FROM findit_matches WHERE id = ?", (m_id,)).fetchone()
                if updated["lost_confirmed"] and updated["found_confirmed"]:
                    conn.execute("UPDATE findit_items SET status = 'RETURNED' WHERE id IN (?, ?)", (updated["lost_item_id"], updated["found_item_id"]))
                    conn.commit()

                self.send_json({
                    "id": updated["id"],
                    "lostItemId": updated["lost_item_id"],
                    "foundItemId": updated["found_item_id"],
                    "verified": bool(updated["verified"]),
                    "lostConfirmed": bool(updated["lost_confirmed"]),
                    "foundConfirmed": bool(updated["found_confirmed"]),
                    "closed": bool(updated["lost_confirmed"] and updated["found_confirmed"])
                })
                return

        # AUTH ROUTES
        if path == '/api/auth/signup' and self.command == 'POST':
            full_name = (body_json.get('fullName') or '').strip()
            email = (body_json.get('email') or '').strip().lower()
            password = body_json.get('password') or ''
            confirm = body_json.get('confirmPassword') or ''

            if not full_name or len(full_name) > 100:
                self.send_json_error("Full name is required (max 100 characters).")
                return

            if not email or len(email) > 120 or not EMAIL_REGEX.match(email):
                self.send_json_error("Please enter a valid email address.")
                return

            if not password or len(password) < 8 or len(password) > 100:
                self.send_json_error("Password must be at least 8 characters long.")
                return

            if not UPPER_REGEX.search(password) or not LOWER_REGEX.search(password) or not DIGIT_REGEX.search(password) or not SPECIAL_REGEX.search(password):
                self.send_json_error("Password must include uppercase, lowercase, number, and special character.")
                return

            if password != confirm:
                self.send_json_error("Passwords do not match.")
                return

            with get_db() as conn:
                c = conn.cursor()
                existing = c.execute("SELECT COUNT(*) FROM findit_users WHERE LOWER(email) = ?", (email,)).fetchone()[0]
                if existing > 0:
                    self.send_json_error("An account with this email address already exists.", status=409)
                    return

                salt = generate_salt()
                pwd_hash = hash_password(password, salt)

                c.execute("""
                    INSERT INTO findit_users (full_name, email, password_hash, salt)
                    VALUES (?, ?, ?, ?)
                """, (html.escape(full_name), email, pwd_hash, salt))
                user_id = c.lastrowid

                token = secrets.token_urlsafe(32)
                expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
                c.execute("INSERT INTO findit_sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires_at))
                conn.commit()

                self.send_json({
                    "id": user_id,
                    "fullName": full_name,
                    "email": email,
                    "token": token
                }, status=201)
                return

        if path == '/api/auth/login' and self.command == 'POST':
            email = (body_json.get('email') or '').strip().lower()
            password = body_json.get('password') or ''

            if not email or not password:
                self.send_json_error("Email and password are required.")
                return

            client_ip = self.client_address[0]
            with get_db() as conn:
                now_utc = datetime.now(timezone.utc)
                # Brute force protection check
                att_row = conn.execute("SELECT attempts, last_attempt FROM findit_auth_attempts WHERE ip = ?", (client_ip,)).fetchone()
                if att_row:
                    try:
                        last_time = datetime.fromisoformat(att_row["last_attempt"].replace('Z', '+00:00'))
                        if (now_utc - last_time).total_seconds() < 900:  # 15 mins window
                            if att_row["attempts"] >= 5:
                                self.send_json_error("Too many failed login attempts. Please wait 15 minutes before trying again.", status=429)
                                return
                        else:
                            conn.execute("DELETE FROM findit_auth_attempts WHERE ip = ?", (client_ip,))
                            conn.commit()
                    except Exception:
                        pass

                user = conn.execute("SELECT * FROM findit_users WHERE LOWER(email) = ?", (email,)).fetchone()
                if not user or not verify_password(password, user["password_hash"], user["salt"]):
                    # Record failed attempt
                    conn.execute("""
                        INSERT INTO findit_auth_attempts (ip, attempts, last_attempt)
                        VALUES (?, 1, ?)
                        ON CONFLICT(ip) DO UPDATE SET attempts = attempts + 1, last_attempt = excluded.last_attempt
                    """, (client_ip, now_utc.isoformat()))
                    conn.commit()
                    self.send_json_error("Invalid email or password.", status=401)
                    return

                # Success: reset failed attempt tracking
                conn.execute("DELETE FROM findit_auth_attempts WHERE ip = ?", (client_ip,))
                token = secrets.token_urlsafe(32)
                expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
                conn.execute("INSERT INTO findit_sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user["id"], expires_at))
                conn.commit()

                self.send_json({
                    "id": user["id"],
                    "fullName": user["full_name"],
                    "email": user["email"],
                    "token": token
                })
                return

        if path == '/api/auth/me' and self.command == 'GET':
            user = self.get_current_user()
            if not user:
                self.send_json_error("Not authenticated or session expired.", status=401)
                return

            self.send_json(user)
            return

        if path == '/api/auth/logout' and self.command == 'POST':
            auth_hdr = self.headers.get('Authorization', '')
            token = auth_hdr[7:].strip() if auth_hdr.lower().startswith('bearer ') else None
            if token:
                with get_db() as conn:
                    conn.execute("DELETE FROM findit_sessions WHERE token = ?", (token,))
                    conn.commit()
            self.send_json({"success": True})
            return

        self.send_json_error("Endpoint not found.", status=404)

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    init_db()
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("  FindIt — Fully Animated Lost & Found Platform")
        print(f"  Live local server running at: {url}")
        print("  Security Hardened SQLite DB, Match Engine & Auth Active")
        print("=" * 60)
        print("Press Ctrl+C to stop the server.")
        if "PORT" not in os.environ:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
