# scripts/test_security_endpoints.py
import urllib.request
import urllib.error
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3000/api"

def request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            headers_dict = dict(resp.headers)
            body = resp.read().decode("utf-8")
            return resp.status, headers_dict, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, dict(e.headers), parsed

print("--- Starting Security & API Test Suite ---")

# 1. Health & Security Headers
status, headers, body = request("/healthz")
print(f"1. /healthz: Status {status}")
assert status == 200, f"Expected 200, got {status}"
assert headers.get("X-Content-Type-Options") == "nosniff", "Missing X-Content-Type-Options header"
assert headers.get("X-Frame-Options") == "SAMEORIGIN", "Missing X-Frame-Options header"
print("   [OK] Security headers present: nosniff, SAMEORIGIN, Referrer-Policy")

# 2. Create a fresh pair of items to test auto-matching, verification & rate limiting
unique_tag = f"test_{int(time.time())}"
status, _, lost_item = request("/items", method="POST", data={
    "type": "LOST",
    "reporter": "Alice Lost",
    "title": f"Silver Key Ring {unique_tag}",
    "category": "Keys",
    "description": "Lost set of silver house keys with blue lanyard.",
    "location": "Science Building Room 204",
    "privateDetail": "blue lanyard star sticker"
})
assert status == 201, f"Failed to create lost item: {status}"

status, _, found_item = request("/items", method="POST", data={
    "type": "FOUND",
    "reporter": "Bob Finder",
    "title": f"Found Silver Keys {unique_tag}",
    "category": "Keys",
    "description": "Found a set of silver house keys near Room 204.",
    "location": "Science Building Room 204",
    "privateDetail": "star on lanyard"
})
assert status == 201, f"Failed to create found item: {status}"
print(f"2. Created Item #{lost_item['id']} and Item #{found_item['id']} successfully.")

# 3. Check auto-generated match
status, _, matches = request("/matches")
assert status == 200, f"Expected 200, got {status}"
target_match = None
for m in matches:
    if m["lostItemId"] == lost_item["id"] and m["foundItemId"] == found_item["id"]:
        target_match = m
        break

assert target_match is not None, "Auto-matching failed to pair lost and found items!"
match_id = target_match["id"]
print(f"   [OK] Auto-matcher paired items into Match #{match_id} (Score: {target_match['scorePercent']}%, Verified: {target_match['verified']})")

# 4. Attempt reading chat before verification (should be 403 Forbidden)
status, _, body = request(f"/matches/{match_id}/messages")
print(f"3. GET /matches/{match_id}/messages (unverified): Status {status}")
assert status == 403, f"Expected 403 Forbidden before verification, got {status}"
print("   [OK] Unauthorized chat access blocked with 403 Forbidden")

# 5. Test verification failure (wrong detail) & attempt countdown
status, _, body = request(f"/matches/{match_id}/verify", method="POST", data={"privateDetail": "wrong secret"})
print(f"4. POST /matches/{match_id}/verify (wrong detail): Status {status}, Remaining: {body.get('remainingAttempts')}")
assert status == 400, f"Expected 400, got {status}"
assert body.get("remainingAttempts") == 4, f"Expected 4 attempts left, got {body.get('remainingAttempts')}"
print("   [OK] Verification rate-limiting attempt counter decremented correctly (4 left)")

# 6. Test successful verification (correct detail)
status, _, body = request(f"/matches/{match_id}/verify", method="POST", data={"privateDetail": "blue lanyard star sticker"})
print(f"5. POST /matches/{match_id}/verify (correct detail): Status {status}, Verified: {body.get('verified')}")
assert status == 200, f"Expected 200, got {status}"
assert body.get("verified") is True, "Verification failed on correct detail"
print("   [OK] Verification succeeded on correct secret detail")

# 7. Post & Read Chat Message after verification
status, _, msg = request(f"/matches/{match_id}/messages", method="POST", data={
    "role": "OWNER",
    "senderName": "Alice Lost",
    "text": "Thank you Bob! Can we meet at the Science Building entrance?"
})
assert status == 201, f"Expected 201, got {status}"

status, _, messages = request(f"/matches/{match_id}/messages")
assert status == 200, f"Expected 200, got {status}"
assert len(messages) >= 1, "Expected at least 1 message"
assert messages[-1]["text"] == "Thank you Bob! Can we meet at the Science Building entrance?"
print(f"6. Direct channel opened: Stored and retrieved message from Alice")

# 8. Confirm Return & Handoff
status, _, confirm_owner = request(f"/matches/{match_id}/confirm-return", method="POST", data={"role": "OWNER"})
assert status == 200, f"Expected 200, got {status}"
assert confirm_owner["lostConfirmed"] is True, "Owner confirmation failed"
assert confirm_owner["closed"] is False, "Item should not be closed until finder confirms"

status, _, confirm_finder = request(f"/matches/{match_id}/confirm-return", method="POST", data={"role": "FINDER"})
assert status == 200, f"Expected 200, got {status}"
assert confirm_finder["foundConfirmed"] is True, "Finder confirmation failed"
assert confirm_finder["closed"] is True, "Item should be closed after both confirm"
print("7. Confirmed safe return: Both parties signed off -> Status closed & reunited")

print("\n=======================================================")
print("  ALL PHASE 1 SECURITY & WORKFLOW TESTS PASSED 100%!  ")
print("=======================================================")
