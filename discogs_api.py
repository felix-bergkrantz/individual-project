import os, time, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCOGS_TOKEN", "")
BASE = "https://api.discogs.com"
UA = {"User-Agent": "DiscogsInsightsApp/1.0"}

def _headers(auth: bool = False):
    h = dict(UA)
    if auth and TOKEN:
        h["Authorization"] = f"Discogs token={TOKEN}"
    return h

def _get(url: str, auth: bool = False, params=None, retries: int = 3):
    params = params or {}
    r = None
    for _ in range(retries):
        r = requests.get(url, headers=_headers(auth), params=params, timeout=20)
        if r.status_code == 429:  # rate limited
            time.sleep(int(r.headers.get("Retry-After", "3"))); continue
        r.raise_for_status()
        # soft throttle when near budget
        rem = r.headers.get("X-Discogs-Ratelimit-Remaining")
        if rem and rem.isdigit() and int(rem) < 3:
            time.sleep(1.2)
        return r.json()
    raise RuntimeError(f"Discogs request failed after {retries} retries (last status={getattr(r, 'status_code', None)})")

# -------- Public release lookup --------
def get_release(release_id: str | int):
    return _get(f"{BASE}/releases/{release_id}", auth=False)

def primary_image(data: dict) -> str | None:
    imgs = data.get("images") or []
    for im in imgs:
        if im.get("type") == "primary":
            return im.get("uri")
    return imgs[0].get("uri") if imgs else None

# -------- Authenticated wantlist (paged) --------
def get_user_wantlist_page(username: str, page: int = 1, per_page: int = 100):
    return _get(f"{BASE}/users/{username}/wants", auth=True, params={"per_page": per_page, "page": page})

       






