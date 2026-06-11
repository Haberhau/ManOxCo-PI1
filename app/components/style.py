import streamlit as st


def inject_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">

    <style>
    /* ── CSS Variables ──────────────────────────────────────────────── */
    :root {
        --bg:        #0B0D13;
        --surface:   #10131C;
        --surface-2: #161923;
        --border:    #1D2235;
        --border-2:  #252A3D;
        --amber:     #F0A500;
        --amber-dim: #C47E00;
        --amber-glow:rgba(240,165,0,0.12);
        --red:       #E53E4D;
        --red-dim:   rgba(229,62,77,0.12);
        --orange:    #F07030;
        --orange-dim:rgba(240,112,48,0.12);
        --yellow:    #E5B830;
        --green:     #10C87A;
        --green-dim: rgba(16,200,122,0.12);
        --teal:      #18A8C8;
        --text-1:    #E8EDF8;
        --text-2:    #8A94A8;
        --text-3:    #50586A;
        --font-display: 'Syne', sans-serif;
        --font-mono:    'IBM Plex Mono', monospace;
        --font-body:    'DM Sans', sans-serif;
    }

    /* ── Global reset ───────────────────────────────────────────────── */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main, .block-container {
        background-color: var(--bg) !important;
        color: var(--text-1) !important;
        font-family: var(--font-body) !important;
    }

    .block-container {
        padding: 0.5rem 2.5rem 2rem 2.5rem !important;
        max-width: 1500px !important;
    }

    /* ── Sidebar ────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #10131C !important;
        border-right: 1px solid #1D2235 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        color: #64748B !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        color: #F0A500 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #50586A !important;
    }

    /* ── Headings ───────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5 {
        font-family: var(--font-display) !important;
        color: var(--text-1) !important;
        font-weight: 700 !important;
    }

    /* ── Metric cards ───────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 1.1rem 1.3rem !important;
    }
    [data-testid="metric-container"] label {
        font-family: var(--font-mono) !important;
        color: var(--text-3) !important;
        font-size: 0.68rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        color: var(--amber) !important;
        font-size: 2.1rem !important;
        font-weight: 600 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
    }

    /* ── Data table ─────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }
    [data-testid="stDataFrame"] * {
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        color: var(--text-2) !important;
        background: transparent !important;
    }

    /* ── Select / input ─────────────────────────────────────────────── */
    [data-testid="stSelectbox"] > div > div,
    [data-baseweb="select"] > div {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 5px !important;
        color: var(--text-1) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.82rem !important;
    }

    /* ── Chat input ─────────────────────────────────────────────────── */
    [data-testid="stChatInput"] textarea {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 6px !important;
        color: var(--text-1) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 2px var(--amber-glow) !important;
    }

    /* ── Nav column: dark background, full height ───────────────────── */
    section[data-testid="stMain"] > div > div > div[data-testid="stHorizontalBlock"] > div:first-child,
    [data-testid="column"]:first-child {
        background: #10131C;
        border-right: 1px solid #1D2235;
        min-height: 100vh;
    }

    /* ── Nav buttons: invisible, overlap the styled div above ────────── */
    [data-testid="column"]:first-child [data-testid="stButton"] {
        margin-top: -2.05rem !important;
        position: relative !important;
        z-index: 10 !important;
    }
    [data-testid="column"]:first-child [data-testid="stButton"] button {
        opacity: 0 !important;
        height: 2rem !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }

    /* ── Buttons in main content area ───────────────────────────────── */
    [data-testid="column"]:not(:first-child) [data-testid="stButton"] button {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-2) !important;
        color: var(--text-2) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        border-radius: 4px !important;
    }
    [data-testid="column"]:not(:first-child) [data-testid="stButton"] button:hover {
        border-color: var(--amber) !important;
        color: var(--amber) !important;
    }

    /* ── Info/warning banners ───────────────────────────────────────── */
    [data-testid="stAlert"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: var(--text-2) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.82rem !important;
    }

    /* ── Divider ────────────────────────────────────────────────────── */
    hr {
        border-color: var(--border) !important;
        margin: 1.2rem 0 !important;
    }

    /* ── Custom components ──────────────────────────────────────────── */

    /* Stat block — large amber number with label */
    .m-stat {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
    }
    .m-stat-label {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--text-3);
        margin-bottom: 0.4rem;
    }
    .m-stat-value {
        font-family: var(--font-mono);
        font-size: 2.4rem;
        font-weight: 600;
        color: var(--amber);
        line-height: 1;
    }
    .m-stat-sub {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--text-3);
        margin-top: 0.3rem;
    }
    .m-stat.danger  { border-color: var(--red);    background: var(--surface); }
    .m-stat.danger .m-stat-value { color: var(--red); }
    .m-stat.warning { border-color: var(--orange); }
    .m-stat.warning .m-stat-value { color: var(--orange); }
    .m-stat.safe    { border-color: var(--green); }
    .m-stat.safe .m-stat-value { color: var(--green); }

    /* Alert rows */
    .m-alert {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.5rem;
    }
    .m-alert.crit { border-left: 3px solid var(--red); }
    .m-alert.high { border-left: 3px solid var(--orange); }
    .m-alert.safe { border-left: 3px solid var(--green); }
    .m-alert-dot  { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
    .m-alert.crit .m-alert-dot { background: var(--red); box-shadow: 0 0 6px var(--red); }
    .m-alert.high .m-alert-dot { background: var(--orange); }
    .m-alert.safe .m-alert-dot { background: var(--green); }
    .m-alert-body {}
    .m-alert-name {
        font-family: var(--font-display);
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-1);
    }
    .m-alert-detail {
        font-family: var(--font-mono);
        font-size: 0.73rem;
        color: var(--text-3);
        margin-top: 0.2rem;
    }
    .m-alert-detail strong { color: var(--text-2); }

    /* Risk badge */
    .m-badge {
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.2rem 0.55rem;
        border-radius: 3px;
    }
    .m-badge.crit    { background: var(--red-dim);    color: var(--red);    border: 1px solid var(--red); }
    .m-badge.high    { background: var(--orange-dim); color: var(--orange); border: 1px solid var(--orange); }
    .m-badge.medium  { background: rgba(229,184,48,0.1); color: var(--yellow); border: 1px solid var(--yellow); }
    .m-badge.low     { background: var(--green-dim);  color: var(--green);  border: 1px solid var(--green); }

    /* Plant card */
    .m-plant-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .m-plant-card:hover { border-color: var(--border-2); }
    .m-plant-name {
        font-family: var(--font-display);
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-2);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .m-plant-value {
        font-family: var(--font-mono);
        font-size: 1.7rem;
        font-weight: 600;
        line-height: 1;
        margin-bottom: 0.2rem;
    }
    .m-plant-unit {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        color: var(--text-3);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .m-plant-util {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-3);
        margin-top: 0.5rem;
    }

    /* Section heading */
    .m-section {
        font-family: var(--font-mono);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-3);
        padding-bottom: 0.6rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid var(--border);
    }

    /* Chat bubbles */
    .m-chat-user {
        background: var(--amber-glow);
        border: 1px solid var(--amber-dim);
        border-radius: 8px 8px 2px 8px;
        padding: 0.85rem 1.1rem;
        margin: 0.7rem 0 0.7rem 20%;
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--text-1);
        line-height: 1.55;
    }
    .m-chat-ai {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px 8px 8px 2px;
        padding: 0.85rem 1.1rem;
        margin: 0.7rem 20% 0.7rem 0;
        font-family: var(--font-body);
        font-size: 0.88rem;
        color: var(--text-2);
        line-height: 1.65;
    }
    .m-chat-ai strong { color: var(--text-1); }
    .m-chat-label {
        font-family: var(--font-mono);
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-3);
        margin-bottom: 0.4rem;
    }

    /* Starter question chip */
    .m-starter {
        background: var(--surface-2);
        border: 1px solid var(--border-2);
        border-radius: 5px;
        padding: 0.55rem 0.85rem;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-2);
        cursor: pointer;
        transition: all 0.15s;
        margin-bottom: 0.4rem;
    }
    .m-starter:hover { border-color: var(--amber); color: var(--amber); }

    /* Table row overrides */
    [data-testid="stDataFrame"] th {
        background: var(--surface-2) !important;
        color: var(--text-3) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border-bottom: 1px solid var(--border) !important;
    }
    [data-testid="stDataFrame"] td {
        color: var(--text-2) !important;
        border-bottom: 1px solid var(--border) !important;
    }

    /* ── Remove top blank: header must be display:none not hidden ───── */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu, footer {
        display: none !important;
    }

    /* ── Sidebar always open: hide only the CLOSE arrow inside sidebar  */
    /* NOT the open arrow (collapsedControl) — that must stay visible    */
    [data-testid="stSidebar"] [data-testid="stBaseButton-header"] {
        display: none !important;
    }

    .stSpinner > div { border-top-color: var(--amber) !important; }
    </style>
    """, unsafe_allow_html=True)


# ── Component helpers ─────────────────────────────────────────────────────────

def page_header(label: str, title: str, sub: str = ""):
    st.markdown(
        f"<div style='margin-bottom:1.6rem'>"
        f"<div style='font-family:var(--font-mono);font-size:0.65rem;"
        f"letter-spacing:0.2em;text-transform:uppercase;color:var(--text-3);"
        f"margin-bottom:0.4rem'>{label}</div>"
        f"<div style='font-family:var(--font-display);font-size:2rem;"
        f"font-weight:800;color:var(--text-1);line-height:1.1'>{title}</div>"
        + (f"<div style='font-family:var(--font-mono);font-size:0.78rem;"
           f"color:var(--text-3);margin-top:0.4rem'>{sub}</div>" if sub else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def section_heading(text: str):
    st.markdown(
        f"<div class='m-section'>{text}</div>",
        unsafe_allow_html=True,
    )


def stat_block(label: str, value: str, sub: str = "", variant: str = ""):
    st.markdown(
        f"<div class='m-stat {variant}'>"
        f"<div class='m-stat-label'>{label}</div>"
        f"<div class='m-stat-value'>{value}</div>"
        + (f"<div class='m-stat-sub'>{sub}</div>" if sub else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.sidebar.markdown("""
    <div style='padding:1.4rem 0.5rem 1.8rem 0.5rem'>
        <div style='font-family:"Syne",sans-serif;font-size:1.35rem;
                    font-weight:800;color:#F0A500;letter-spacing:0.04em;
                    text-transform:uppercase'>
            Momentum
        </div>
        <div style='font-family:"IBM Plex Mono",monospace;font-size:0.65rem;
                    color:#50586A;margin-top:0.2rem;letter-spacing:0.1em'>
            Data Intelligence Platform
        </div>
        <div style='border-top:1px solid #1D2235;margin-top:1.1rem'></div>
    </div>
    """, unsafe_allow_html=True)
