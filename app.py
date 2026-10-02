"""
AutoElite — Main Entry Point
Run with:  streamlit run app.py

Routing is done via ?page= query parameter.
All pages are lazy-imported so only the active page loads its dependencies.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title   = "AutoElite — Drive Your Ambition",
    page_icon    = "🚘",
    layout       = "wide",
    initial_sidebar_state = "collapsed",
)

# ── Bootstrap DB and styles ───────────────────────────────────────────────────
from utils.database import init_db
from components.styles import get_css
from components.ui import render_navbar, _html

init_db()
st.markdown(get_css(), unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
for _k, _v in {
    "user_id":    0,
    "user_name":  "",
    "user_role":  "",
    "user_email": "",
    "favourites": [],     # list of vehicle IDs
    "compare_ids":[],     # list of vehicle IDs (max 3)
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Read active page from query params ────────────────────────────────────────
_RAW_PAGE = st.query_params.get("page", "home").lower().strip()

# Map URL slugs → internal keys
_PAGE_MAP = {
    "home":      "home",
    "cars":      "cars",
    "detail":    "detail",
    "compare":   "compare",
    "financing": "financing",
    "services":  "services",
    "about":     "about",
    "favorites":  "favorites",
    "favourites": "favorites",
    "dashboard": "dashboard",
    "admin":     "admin",
}
_PAGE = _PAGE_MAP.get(_RAW_PAGE, "home")

# ── Nav bar ───────────────────────────────────────────────────────────────────
_NAV_LABELS = {
    "home":      "Home",
    "cars":      "Cars",
    "compare":   "Compare",
    "financing": "Financing",
    "services":  "Services",
    "about":     "About",
}
_active_nav = _NAV_LABELS.get(_PAGE, "Home")
_fav_count  = len(st.session_state.get("favourites", []))

# Don't show nav on admin page (it has its own bar)
if _PAGE != "admin":
    render_navbar(active=_active_nav, fav_count=_fav_count)

# ── Handle favourite/compare quick-actions from listing pages ─────────────────
_action = st.query_params.get("action", "")
_vid    = st.query_params.get("vid", "0")
try:
    _vid_int = int(_vid)
except ValueError:
    _vid_int = 0

if _action == "fav" and _vid_int and _PAGE != "detail":
    # Toggled from grid (not detail page — detail handles it inline)
    if st.session_state["user_id"]:
        from utils.database import toggle_favourite
        added = toggle_favourite(st.session_state["user_id"], _vid_int)
        favs  = st.session_state["favourites"]
        if added and _vid_int not in favs:
            favs.append(_vid_int)
        elif not added and _vid_int in favs:
            favs.remove(_vid_int)
        st.session_state["favourites"] = favs
    st.query_params["action"] = ""
    st.rerun()

if _action == "compare" and _vid_int and _PAGE != "detail":
    ids = st.session_state["compare_ids"]
    if _vid_int in ids:
        ids.remove(_vid_int)
    elif len(ids) < 3:
        ids.append(_vid_int)
    st.session_state["compare_ids"] = ids
    st.query_params["action"] = ""
    st.rerun()

# ── Route to page ─────────────────────────────────────────────────────────────
if _PAGE == "home":
    from pages.home import render_home
    render_home()

elif _PAGE == "cars":
    from pages.cars import render_cars_page
    render_cars_page()

elif _PAGE == "detail":
    from pages.cars import render_detail_page
    render_detail_page(_vid_int)

elif _PAGE == "compare":
    from pages.other_pages import render_compare_page
    render_compare_page()

elif _PAGE == "financing":
    from pages.other_pages import render_financing_page
    render_financing_page()

elif _PAGE == "services":
    from pages.other_pages import render_services_page
    render_services_page()

elif _PAGE == "about":
    from pages.other_pages import render_about_page
    render_about_page()

elif _PAGE == "favorites":
    from pages.dashboard import render_favourites_page
    render_favourites_page()

elif _PAGE == "dashboard":
    from pages.dashboard import render_dashboard_page
    render_dashboard_page()

elif _PAGE == "admin":
    from pages.admin import render_admin_page
    render_admin_page()

else:
    # 404
    _html("""
    <div style="min-height:80vh;display:flex;align-items:center;
                justify-content:center;text-align:center;padding:40px">
      <div>
        <div style="font-family:'Playfair Display',serif;font-size:80px;
                    font-weight:700;color:var(--mid);margin-bottom:12px">404</div>
        <h2 style="font-size:24px;font-weight:600;color:var(--white);margin-bottom:8px">
          Page not found
        </h2>
        <p style="font-size:14px;color:var(--gray);margin-bottom:24px">
          The page you're looking for doesn't exist.
        </p>
        <a href="?page=home"
           style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;
                  background:var(--accent);color:var(--black);border-radius:8px;
                  font-weight:600;text-decoration:none">
          Go Home
        </a>
      </div>
    </div>""")
