"""
app.py - File System Recovery & Optimization Tool
ELITE EDITION — Boot Screen | Live Terminal | Heatmap | Forensics | Defrag | Benchmark
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="FS Recovery & Optimizer",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&family=Orbitron:wght@700;900&family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #060912; color: #c8d8e8; }

section[data-testid="stSidebar"] {
    background: #080d1a !important;
    border-right: 1px solid #0d2040;
}

/* ── Boot screen ── */
.boot-overlay {
    position:fixed; top:0; left:0; right:0; bottom:0;
    background:#000; z-index:9999;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
}
.boot-logo {
    font-family:'Orbitron',monospace; font-size:42px; font-weight:900;
    color:#00d4ff; letter-spacing:6px;
    text-shadow: 0 0 30px #00d4ff88;
}
.boot-line {
    font-family:'JetBrains Mono',monospace; font-size:13px;
    color:#00ff88; margin:4px 0;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg,#080d1a,#0d1a30);
    border:1px solid #0d2a4a; border-radius:10px;
    padding:18px 16px; text-align:center; position:relative; overflow:hidden;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00d4ff,#0055ff,#00d4ff);
    background-size:200% 100%; animation:shimmer 2s infinite linear;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.kpi-title { font-size:10px; font-weight:600; letter-spacing:2.5px;
             color:#2a5a7a; text-transform:uppercase; margin-bottom:6px; }
.kpi-value { font-family:'Orbitron',monospace; font-size:28px; font-weight:700;
             color:#00d4ff; line-height:1; }
.kpi-sub { font-size:10px; color:#1a3a5a; margin-top:4px; }
.kpi-green .kpi-value { color:#00ff88; }
.kpi-red   .kpi-value { color:#ff4444; }
.kpi-amber .kpi-value { color:#ffaa00; }

/* ── Section title ── */
.sec { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700;
       letter-spacing:3px; color:#1a3a5a; text-transform:uppercase;
       border-bottom:1px solid #0d2040; padding-bottom:6px; margin-bottom:14px; }

/* ── CRASH banner ── */
.crash-banner {
    background:linear-gradient(90deg,#200505,#150303);
    border:2px solid #ff2020; border-radius:8px; padding:14px;
    text-align:center;
    animation:flashRed 0.7s infinite;
}
@keyframes flashRed { 0%,100%{border-color:#ff2020;box-shadow:0 0 20px #ff202044}
                      50%{border-color:#ff6666;box-shadow:0 0 40px #ff666644} }
.crash-title { font-family:'Orbitron',monospace; font-size:20px; font-weight:900;
               color:#ff3333; letter-spacing:4px; }

/* ── Terminal ── */
.terminal {
    background:#020408; border:1px solid #0a2030;
    border-radius:6px; padding:12px 14px;
    font-family:'JetBrains Mono',monospace; font-size:11px;
    height:320px; overflow-y:auto; position:relative;
}
.terminal::before {
    content:'● ● ●'; position:sticky; top:0; display:block;
    color:#333; font-size:14px; margin-bottom:8px;
    background:#020408; padding-bottom:6px;
    border-bottom:1px solid #0a1a20;
}
.t-ok     { color:#00ff88; }
.t-err    { color:#ff4444; }
.t-warn   { color:#ffaa00; }
.t-info   { color:#4a9abf; }
.t-write  { color:#8866ff; }
.t-cache  { color:#00d4ff; }
.t-crash  { color:#ff2020; font-weight:700; }
.t-defrag { color:#ff8800; }
.t-recov  { color:#00ffcc; }
.t-alloc  { color:#ddaa00; }

/* ── Block heatmap ── */
.heatmap { display:flex; flex-wrap:wrap; gap:2px;
           padding:14px; background:#030609;
           border:1px solid #0a1a30; border-radius:8px; }
.blk { width:20px; height:20px; border-radius:2px;
       display:inline-flex; align-items:center; justify-content:center;
       font-size:7px; font-family:'JetBrains Mono',monospace;
       font-weight:700; cursor:default; transition:transform 0.1s; }
.blk:hover { transform:scale(1.4); z-index:10; }
.blk-sys    { background:#1a1000; border:1px solid #3a2800; color:#aa6600; }
.blk-free   { background:#030e06; border:1px solid #071508; color:#0d2010; }
.blk-used   { background:#001830; border:1px solid #003060; color:#0080cc; }
.blk-cached { background:#001a20; border:1px solid #004050; color:#00c0e0; }
.blk-recent { background:#100030; border:1px solid #300080; color:#9944ff; }
.blk-frag   { background:#1a1000; border:1px solid #404000; color:#aaaa00; }
.blk-corrupt{ background:#300000; border:1px solid #600000; color:#ff3333;
              animation:blinkRed 0.8s infinite; }
@keyframes blinkRed { 0%,100%{opacity:1} 50%{opacity:0.35} }

/* ── Badges ── */
.badge-ok   { background:#051a0d; border:1px solid #00cc66; color:#00cc66;
              padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-err  { background:#1a0505; border:1px solid #ff3333; color:#ff3333;
              padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-warn { background:#1a1005; border:1px solid #ffaa00; color:#ffaa00;
              padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }

/* ── Forensic severity ── */
.sev-critical { color:#ff3333; font-weight:700; }
.sev-warning  { color:#ffaa00; }
.sev-ok       { color:#00ff88; }

/* ── Recovery mode overlay ── */
.recovery-mode {
    background:linear-gradient(135deg,#0a0000,#020005);
    border:1px solid #660000; border-radius:10px; padding:20px;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    font-family:'JetBrains Mono',monospace !important;
    font-size:11px !important; font-weight:700 !important; letter-spacing:1px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#030609; }
::-webkit-scrollbar-thumb { background:#0a2030; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# BOOT SCREEN (first load only)
# ═══════════════════════════════════════════════════════════════
if "booted" not in st.session_state:
    boot_placeholder = st.empty()
    boot_lines = [
        ("INFO",    "Kernel loading filesystem module..."),
        ("OK",      "Disk controller initialized — 64 blocks x 512B"),
        ("OK",      "Bitmap allocator ready"),
        ("OK",      "Inode table mounted — 32 slots"),
        ("OK",      "Journal (WAL) loaded — 0 pending entries"),
        ("OK",      "LRU cache initialized — 8 slots"),
        ("OK",      "Directory tree constructed"),
        ("OK",      "Fragmentation analyzer online"),
        ("OK",      "Forensic scanner ready"),
        ("READY",   ">>> FILE SYSTEM ONLINE <<<"),
    ]
    colors = {"INFO":"#4a9abf","OK":"#00ff88","READY":"#00d4ff"}

    displayed = []
    for level, msg in boot_lines:
        displayed.append((level, msg))
        lines_html = "".join(
            f'<div style="color:{colors.get(l,"#aaa")};font-family:JetBrains Mono,monospace;font-size:13px;margin:3px 0;">'
            f'[ {l:5s} ]  {m}</div>'
            for l, m in displayed
        )
        boot_placeholder.markdown(f"""
        <div style="background:#000;padding:60px 80px;border-radius:12px;min-height:360px;">
          <div style="font-family:Orbitron,monospace;font-size:38px;font-weight:900;
                      color:#00d4ff;letter-spacing:6px;text-shadow:0 0 30px #00d4ff88;
                      margin-bottom:24px;">FSYS-OS</div>
          <div style="font-family:JetBrains Mono,monospace;font-size:11px;
                      color:#2a4a6a;letter-spacing:2px;margin-bottom:20px;">
               FILE SYSTEM RECOVERY &amp; OPTIMIZATION TOOL v2.0</div>
          {lines_html}
        </div>""", unsafe_allow_html=True)
        time.sleep(0.22)

    time.sleep(0.5)
    boot_placeholder.empty()
    st.session_state.booted = True

# ═══════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════
if "fs" not in st.session_state:
    from filesystem import FileSystem
    st.session_state.fs = FileSystem()
    st.session_state.activity_log = []

fs = st.session_state.fs


def log(msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.activity_log.append(f"[{ts}] {msg}")
    if len(st.session_state.activity_log) > 150:
        st.session_state.activity_log.pop(0)


summary = fs.get_summary()
disk    = summary["disk"]

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="font-family:Orbitron,monospace;font-size:16px;
        font-weight:900;color:#00d4ff;letter-spacing:3px;margin-bottom:4px;">FSYS-OS</div>
        <div style="font-size:10px;color:#1a3a5a;letter-spacing:2px;margin-bottom:12px;">
        RECOVERY &amp; OPTIMIZER</div>""", unsafe_allow_html=True)

    if summary["crashed"]:
        st.markdown('<span class="badge-err">⚠ CRASH DETECTED</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-ok">● SYSTEM ONLINE</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:12px;color:#4a6a8a;font-family:JetBrains Mono,monospace;">'
                f'Files: <b style="color:#c8d8e8">{summary["total_files"]}</b> &nbsp;|&nbsp; '
                f'Dirs: <b style="color:#c8d8e8">{summary["total_dirs"]}</b><br>'
                f'Blocks: <b style="color:#00d4ff">{disk["used_blocks"]}/{disk["total_blocks"]}</b><br>'
                f'Cache: <b style="color:#00ff88">{summary["cache"]["hit_rate_%"]}%</b> hits<br>'
                f'IOPS: <b style="color:#ffaa00">{summary["iops"]}</b><br>'
                f'Throughput: <b style="color:#8866ff">{summary["throughput_kb"]} KB</b>'
                f'</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### ⚡ Allocation Strategy")
    from filesystem import STRATEGY_FIRST_FIT, STRATEGY_BEST_FIT, STRATEGY_CONTIGUOUS
    strat = st.selectbox("Strategy", [STRATEGY_CONTIGUOUS, STRATEGY_BEST_FIT, STRATEGY_FIRST_FIT],
                         index=[STRATEGY_CONTIGUOUS, STRATEGY_BEST_FIT, STRATEGY_FIRST_FIT].index(
                             fs.allocation_strategy), label_visibility="collapsed")
    if strat != fs.allocation_strategy:
        fs.allocation_strategy = strat
        log(f"Strategy changed to {strat}")
        st.rerun()

    st.markdown("---")
    st.markdown("##### 🔥 Danger Zone")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💥 CRASH", use_container_width=True, type="primary"):
            cb = fs.simulate_crash()
            log(f"💥 CRASH — corrupted: {cb}")
            st.rerun()
    with c2:
        if st.button("🔄 RECOVER", use_container_width=True):
            res = fs.recover()
            log(f"🔄 Recovered {len(res)} ops")
            st.rerun()

    st.markdown("---")
    st.markdown("##### 🔧 Tools")
    if st.button("🧹 Defragment Disk", use_container_width=True):
        report = fs.defragment()
        log(f"🧹 Defrag: {len(report)} files relocated")
        st.success(f"Defrag complete — {len(report)} files")
        st.rerun()
    if st.button("🔍 Run Forensic Scan", use_container_width=True):
        issues = fs.forensic_analysis()
        log(f"🔍 Forensic: {len(issues)} issues found")
        st.info(f"Found {len(issues)} issues — see Forensics tab")
    if st.button("📊 Run Benchmark", use_container_width=True):
        st.session_state.benchmark_results = fs.benchmark_strategies()
        log("📊 Benchmark complete")
        st.rerun()

    st.markdown("---")
    if st.button("🗑 Reset FileSystem", use_container_width=True):
        from filesystem import FileSystem
        st.session_state.fs = FileSystem()
        st.session_state.activity_log = []
        if "benchmark_results" in st.session_state:
            del st.session_state["benchmark_results"]
        log("System reset")
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding:20px 0 10px 0;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              letter-spacing:4px;color:#1a3a5a;text-transform:uppercase;">
       Operating Systems — Project</div>
  <div style="font-family:'Orbitron',monospace;font-size:32px;font-weight:900;
              color:#e2e8f0;line-height:1.1;">File System Recovery</div>
  <div style="font-family:'Orbitron',monospace;font-size:32px;font-weight:900;
              color:#00d4ff;line-height:1.1;">&amp; Optimization Tool</div>
  <div style="margin-top:8px;font-size:12px;color:#2a4a6a;font-family:'JetBrains Mono',monospace;">
       Bitmap Allocation · Inode Table · WAL Journaling · LRU Cache · Defragmentation · Forensic Analysis
  </div>
</div>
""", unsafe_allow_html=True)

# Crash banner
if summary["crashed"]:
    st.markdown("""
    <div class="crash-banner">
      <div class="crash-title">⚠ CRITICAL — DISK CRASH DETECTED ⚠</div>
      <div style="color:#cc4444;font-size:12px;margin-top:6px;font-family:JetBrains Mono,monospace;">
           DATA AT RISK — Journal replay required to restore consistency</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("")

# ─── KPI Row ─────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
kpis = [
    (c1, "DISK BLOCKS",    f"{disk['used_blocks']}/{disk['total_blocks']}", f"{disk['free_blocks']} free",  ""),
    (c2, "TOTAL FILES",    summary["total_files"],                          f"{summary['total_dirs']} dirs", ""),
    (c3, "CACHE HIT %",    f"{summary['cache']['hit_rate_%']}%",            f"{summary['cache']['hits']} hits","kpi-green"),
    (c4, "FRAGMENTATION",  f"{summary['fragmentation_score']}%",            "lower is better",              "kpi-amber" if summary["fragmentation_score"] > 30 else ""),
    (c5, "IOPS",           summary["iops"],                                 "total operations",             ""),
    (c6, "THROUGHPUT",     f"{summary['throughput_kb']}KB",                 "transferred",                  ""),
]
for col, title, val, sub, extra in kpis:
    with col:
        st.markdown(f'<div class="kpi-card {extra}"><div class="kpi-title">{title}</div>'
                    f'<div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📂  FILE MANAGER",
    "🖴  DISK HEATMAP",
    "⚡  LIVE TERMINAL",
    "📋  JOURNAL & RECOVERY",
    "📊  PERFORMANCE",
    "🔍  FORENSICS",
    "🗂  DIRECTORY TREE",
])
tab_files, tab_disk, tab_term, tab_journal, tab_perf, tab_forensic, tab_tree = tabs


# ══════════════════════════════════════════════════════
# TAB 1 — FILE MANAGER
# ══════════════════════════════════════════════════════
with tab_files:
    left, right = st.columns([1,1])

    with left:
        st.markdown('<div class="sec">Create / Write File</div>', unsafe_allow_html=True)
        fname   = st.text_input("File Name", placeholder="notes.txt", key="fn")
        dirs    = ["/"] + [e.name for e in fs.list_files("/") if e.entry_type == "dir"]
        fpath   = st.selectbox("Directory", dirs, key="fp")
        fcontent= st.text_area("Content", placeholder="Enter file content here...",
                               height=100, key="fc")
        ca, cb  = st.columns(2)
        with ca:
            if st.button("✅ Create", use_container_width=True):
                if fname.strip():
                    try:
                        inode = fs.create_file(fname.strip(), fcontent, fpath)
                        log(f"✅ Created '{fname}' inode #{inode.inode_id}")
                        st.success(f"Created '{fname}'")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("Enter a file name")
        with cb:
            if st.button("📝 Write/Update", use_container_width=True):
                if fname.strip():
                    try:
                        inode = fs.write_file(fname.strip(), fcontent, fpath)
                        log(f"📝 Wrote '{fname}'")
                        st.success(f"Updated '{fname}'")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        st.markdown("")
        st.markdown('<div class="sec">Create Directory</div>', unsafe_allow_html=True)
        dname = st.text_input("Dir Name", placeholder="documents", key="dn")
        if st.button("📁 Make Directory", use_container_width=True):
            if dname.strip():
                try:
                    fs.make_dir(dname.strip())
                    log(f"📁 mkdir '/{dname}'")
                    st.success(f"Directory '/{dname}' created")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with right:
        st.markdown('<div class="sec">File Browser</div>', unsafe_allow_html=True)
        all_files = fs.get_all_files()
        if all_files:
            df = pd.DataFrame(all_files)
            df["created"]  = pd.to_datetime(df["created"], unit="s").dt.strftime("%H:%M:%S")
            df["modified"] = pd.to_datetime(df["modified"], unit="s").dt.strftime("%H:%M:%S")
            df["blocks"]   = df["blocks"].apply(str)
            st.dataframe(df[["name","path","size","blocks","created"]], use_container_width=True, height=180)

            st.markdown('<div class="sec">Read / Delete</div>', unsafe_allow_html=True)
            file_options = {
                f"{f['path']}": (f["name"], "/" + "/".join(f["path"].split("/")[:-1]).strip("/"))
                for f in all_files
            }

            sel = st.selectbox("Select file", list(file_options.keys()), key="sel")

            selected_name, selected_path = file_options[sel]
            cr, cd = st.columns(2)
            with cr:
                if st.button("👁 Read", use_container_width=True):
                    try:
                        content = fs.read_file(selected_name, selected_path)
                        log(f"👁 Read '{sel}'")
                        st.code(content or "(empty)", language=None)
                    except Exception as e:
                        st.error(str(e))
            with cd:
                if st.button("🗑 Delete", use_container_width=True):
                    try:
                        fs.delete_file(selected_name, selected_path)
                        log(f"🗑 Deleted '{sel}'")
                        st.success(f"Deleted '{sel}'")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("No files yet — create one on the left")


# ══════════════════════════════════════════════════════
# TAB 2 — DISK HEATMAP
# ══════════════════════════════════════════════════════
with tab_disk:
    st.markdown('<div class="sec">Advanced Disk Block Heatmap — 64 Blocks × 512 Bytes</div>',
                unsafe_allow_html=True)

    block_map       = fs.disk.get_block_map()
    recently        = summary.get("recently_accessed", [])
    cached_blocks   = set(fs.cache.cache.keys())
    _, frag_data_raw= fs.get_fragmentation()
    frag_blocks     = set()
    for item in fs.get_fragmentation()[0]:
        if item["fragmented"]:
            for b in item["blocks"]:
                frag_blocks.add(b)

    # Legend
    lc = st.columns(6)
    legends = [
        ("#aa6600","System"),("#0080cc","Used"),("#00c0e0","Cached"),
        ("#9944ff","Recent"),("#aaaa00","Fragmented"),("#ff3333","Corrupted"),
    ]
    for col, (color, label) in zip(lc, legends):
        with col:
            st.markdown(f'<span style="color:{color}">■</span> <small>{label}</small>',
                        unsafe_allow_html=True)

    st.markdown("")
    grid_html = '<div class="heatmap">'
    for i, state in enumerate(block_map):
        if i < 4:
            cls, lbl = "blk blk-sys", "SYS"
        elif state == "corrupted":
            cls, lbl = "blk blk-corrupt", "✕"
        elif i in recently:
            cls, lbl = "blk blk-recent", str(i)
        elif i in cached_blocks:
            cls, lbl = "blk blk-cached", str(i)
        elif i in frag_blocks:
            cls, lbl = "blk blk-frag", str(i)
        elif state == "used":
            cls, lbl = "blk blk-used", str(i)
        else:
            cls, lbl = "blk blk-free", "·"
        grid_html += f'<div class="{cls}" title="Block {i}: {state}">{lbl}</div>'
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)

    with dc1:
        st.markdown('<div class="sec">Disk Usage</div>', unsafe_allow_html=True)
        used = disk["used_blocks"]; free = disk["free_blocks"]; corrupt = disk["corrupted_blocks"]
        fig = go.Figure(go.Pie(
            labels=["Used","Free","Corrupted"],
            values=[used, free, corrupt],
            hole=0.65,
            marker_colors=["#0080cc","#051a0d","#ff3333"],
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#7aafcf",
            legend=dict(font=dict(color="#7aafcf")),
            annotations=[dict(text=f"<b>{used}</b><br>used", x=0.5, y=0.5,
                              font_size=14, font_color="#00d4ff", showarrow=False)],
            margin=dict(t=10,b=10,l=0,r=0), height=260,
        )
        st.plotly_chart(fig, use_container_width=True)

    with dc2:
        st.markdown('<div class="sec">Fragmentation Analysis</div>', unsafe_allow_html=True)
        frag_data, frag_score = fs.get_fragmentation()
        if frag_data:
            fdf = pd.DataFrame(frag_data)
            fig_f = px.bar(fdf, x="file", y="fragments",
                           color="fragmented",
                           color_discrete_map={True:"#ff4444", False:"#00ff88"})
            fig_f.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(3,6,9,0.9)",
                font_color="#7aafcf",
                xaxis=dict(gridcolor="#0a1a30"),
                yaxis=dict(gridcolor="#0a1a30"),
                showlegend=False, height=260,
                margin=dict(t=10,b=10),
            )
            st.plotly_chart(fig_f, use_container_width=True)

            st.markdown(f'<div class="sec">Score: <span style="color:#ffaa00">{frag_score}%</span></div>',
                        unsafe_allow_html=True)
            if st.button("🧹 Defragment Now", use_container_width=True):
                rep = fs.defragment()
                log(f"🧹 Defrag: {len(rep)} files")
                st.success(f"Done — {len(rep)} files moved")
                st.rerun()
        else:
            st.info("Create files to see fragmentation")


# ══════════════════════════════════════════════════════
# TAB 3 — LIVE TERMINAL
# ══════════════════════════════════════════════════════
with tab_term:
    st.markdown('<div class="sec">Live System Terminal — Real-time FS Operations Log</div>',
                unsafe_allow_html=True)

    # Color rules for terminal
    def term_color(line):
        l = line.upper()
        if "[OK]"     in l: return "t-ok"
        if "[ERR]"    in l: return "t-err"
        if "[CRASH]"  in l: return "t-crash"
        if "[WRITE]"  in l: return "t-write"
        if "[CACHE HIT]" in l: return "t-cache"
        if "[DISK READ]" in l: return "t-cache"
        if "[ALLOC]"  in l: return "t-alloc"
        if "[DEFRAG]" in l: return "t-defrag"
        if "[RECOVERY]"in l: return "t-recov"
        if "[INFO]"   in l: return "t-info"
        if "[FORENSIC]"in l: return "t-warn"
        return "t-info"

    term_html = '<div class="terminal">'
    logs = fs.terminal_log[-60:] if fs.terminal_log else ["[INFO] System ready. Perform operations to see live logs."]
    for line in reversed(logs):
        cls = term_color(line)
        term_html += f'<div class="{cls}">{line}</div>'
    term_html += "</div>"
    st.markdown(term_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # File access flow diagram
    st.markdown('<div class="sec">File Read Access Flow Diagram</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#030609;border:1px solid #0a1a30;border-radius:8px;padding:20px;
                font-family:JetBrains Mono,monospace;font-size:12px;text-align:center;">
      <span style="color:#00d4ff;font-size:14px;font-weight:700;">USER REQUEST</span><br>
      <span style="color:#1a3a5a;">│</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#8866ff;">RESOLVE PATH → DIRECTORY ENTRY</span><br>
      <span style="color:#1a3a5a;">│</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#ddaa00;">FETCH INODE (metadata + block list)</span><br>
      <span style="color:#1a3a5a;">│</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#00c0e0;">CHECK LRU CACHE</span>
      <span style="color:#1a3a5a;"> ──→ </span>
      <span style="color:#00ff88;">CACHE HIT → RETURN DATA ✓</span><br>
      <span style="color:#1a3a5a;">│ (miss)</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#0080cc;">DISK BLOCK FETCH</span>
      <span style="color:#1a3a5a;"> ──→ </span>
      <span style="color:#ff3333;">CORRUPTED? → RAISE IOError</span><br>
      <span style="color:#1a3a5a;">│</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#00c0e0;">UPDATE CACHE</span><br>
      <span style="color:#1a3a5a;">│</span><br>
      <span style="color:#8866ff;">▼</span><br>
      <span style="color:#00ff88;font-size:14px;font-weight:700;">FILE DATA RETURNED ✓</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Terminal", use_container_width=True):
        st.rerun()


# ══════════════════════════════════════════════════════
# TAB 4 — JOURNAL & RECOVERY
# ══════════════════════════════════════════════════════
with tab_journal:
    if summary["crashed"]:
        st.markdown("""
        <div class="recovery-mode">
          <div style="font-family:Orbitron,monospace;font-size:18px;font-weight:900;
                      color:#ff3333;letter-spacing:3px;text-align:center;
                      animation:flashRed 0.7s infinite;">
               ⚠ EMERGENCY RECOVERY MODE ACTIVE ⚠</div>
          <div style="color:#cc3333;font-size:12px;text-align:center;margin-top:8px;
                      font-family:JetBrains Mono,monospace;">
               Disk crash detected — journal scanning in progress...</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("")

    jl, jr = st.columns([1,1])

    with jl:
        st.markdown('<div class="sec">WAL Journal Log</div>', unsafe_allow_html=True)
        jlog = fs.journal.get_log()
        jhtml = '<div class="terminal" style="height:280px;">'
        for line in reversed(jlog[-40:]):
            if "COMMIT" in line or "OK" in line:    cls = "t-ok"
            elif "ABORT" in line or "ERR" in line:  cls = "t-err"
            elif "CRASH" in line:                   cls = "t-crash"
            elif "Recovery" in line or "RECOVERY" in line: cls = "t-recov"
            else:                                   cls = "t-info"
            jhtml += f'<div class="{cls}">{line}</div>'
        jhtml += "</div>"
        st.markdown(jhtml, unsafe_allow_html=True)

    with jr:
        st.markdown('<div class="sec">Journal Entry Table</div>', unsafe_allow_html=True)
        entries = fs.journal.entries
        if entries:
            edf = pd.DataFrame([{
                "op": e.op_type, "state": e.state,
                "file": e.details.get("name","—"),
                "time": time.strftime("%H:%M:%S", time.localtime(e.timestamp)),
            } for e in entries])
            st.dataframe(edf, use_container_width=True, height=220)
        else:
            st.info("No journal entries yet")

        st.markdown('<div class="sec">Recovery Controls</div>', unsafe_allow_html=True)
        if summary["crashed"]:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("🔄 Run WAL Recovery", use_container_width=True, type="primary"):
                    res = fs.recover()
                    log(f"🔄 Recovery: {len(res)} ops replayed")
                    st.success(f"Recovery done — {len(res)} ops")
                    st.rerun()
            with col_r2:
                crash_type = st.selectbox("Crash Type", ["random","power loss","partial write","metadata"], key="ct")
        else:
            st.markdown('<span class="badge-ok">● Journal Consistent</span>', unsafe_allow_html=True)
            st.markdown('<span style="color:#2a4a6a;font-size:12px;font-family:JetBrains Mono,monospace;">'
                        '<br>No pending recovery needed.<br>All entries checkpointed.</span>',
                        unsafe_allow_html=True)

    # Activity log
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Activity Log</div>', unsafe_allow_html=True)
    act_html = '<div class="terminal" style="height:180px;">' + "".join(
        f'<div class="t-info">{l}</div>' for l in reversed(st.session_state.activity_log[-30:])
    ) + "</div>"
    st.markdown(act_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# TAB 5 — PERFORMANCE
# ══════════════════════════════════════════════════════
with tab_perf:
    cache = summary["cache"]
    perf  = summary["perf"]

    # KPI row
    pk = st.columns(5)
    pkpis = [
        (pk[0], "CACHE HITS",   cache["hits"],           "kpi-green"),
        (pk[1], "CACHE MISSES", cache["misses"],          "kpi-red"),
        (pk[2], "HIT RATE",     f"{cache['hit_rate_%']}%",""),
        (pk[3], "AVG READ ms",  disk["avg_read_ms"],      ""),
        (pk[4], "AVG WRITE ms", disk["avg_write_ms"],     "kpi-amber"),
    ]
    for col, title, val, cls in pkpis:
        with col:
            st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-title">{title}</div>'
                        f'<div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    pp1, pp2 = st.columns(2)

    with pp1:
        st.markdown('<div class="sec">Cache Hit Rate Gauge</div>', unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cache["hit_rate_%"],
            number={"suffix":"%","font":{"color":"#00d4ff","size":34}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#1a3a5a"},
                "bar":{"color":"#00d4ff","thickness":0.25},
                "bgcolor":"#030609","bordercolor":"#0a1a30",
                "steps":[{"range":[0,40],"color":"#1a0505"},
                         {"range":[40,70],"color":"#1a1005"},
                         {"range":[70,100],"color":"#051a0d"}],
                "threshold":{"line":{"color":"#00ff88","width":3},"value":70},
            },
            title={"text":"LRU Cache Efficiency","font":{"color":"#2a5a7a","size":12}},
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#7aafcf",
                            height=260,margin=dict(t=30,b=0))
        st.plotly_chart(fig_g, use_container_width=True)

    with pp2:
        st.markdown('<div class="sec">Read vs Write Latency Timeline</div>', unsafe_allow_html=True)
        rt = fs.perf.read_times[-20:]  or [0]
        wt = fs.perf.write_times[-20:] or [0]
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=list(range(len(rt))), y=rt, name="Read",
                                   mode="lines+markers", fill="tozeroy",
                                   fillcolor="rgba(0,212,255,0.08)",
                                   line=dict(color="#00d4ff",width=2)))
        fig_l.add_trace(go.Scatter(x=list(range(len(wt))), y=wt, name="Write",
                                   mode="lines+markers", fill="tozeroy",
                                   fillcolor="rgba(255,100,50,0.08)",
                                   line=dict(color="#ff6644",width=2)))
        fig_l.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(3,6,9,0.95)",
            font_color="#7aafcf",
            xaxis=dict(gridcolor="#0a1a30",title="Op #"),
            yaxis=dict(gridcolor="#0a1a30",title="ms"),
            legend=dict(font=dict(color="#7aafcf")),
            height=260, margin=dict(t=10,b=10,l=0,r=0),
        )
        st.plotly_chart(fig_l, use_container_width=True)

    # Benchmark
    st.markdown('<div class="sec">Allocation Strategy Benchmark</div>', unsafe_allow_html=True)
    if "benchmark_results" in st.session_state:
        bres = st.session_state.benchmark_results
        bdf  = pd.DataFrame(list(bres.values()))
        bc1, bc2 = st.columns(2)
        with bc1:
            fig_b = px.bar(bdf, x="strategy", y="fragmentation",
                           color="strategy",
                           color_discrete_sequence=["#00d4ff","#ff6644","#00ff88"],
                           title="Fragmentation by Strategy")
            fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(3,6,9,0.9)",
                                font_color="#7aafcf", showlegend=False,
                                height=260,margin=dict(t=30,b=10))
            st.plotly_chart(fig_b, use_container_width=True)
        with bc2:
            fig_b2 = px.bar(bdf, x="strategy", y="alloc_time_ms",
                            color="strategy",
                            color_discrete_sequence=["#00d4ff","#ff6644","#00ff88"],
                            title="Allocation Time (ms)")
            fig_b2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                 plot_bgcolor="rgba(3,6,9,0.9)",
                                 font_color="#7aafcf", showlegend=False,
                                 height=260,margin=dict(t=30,b=10))
            st.plotly_chart(fig_b2, use_container_width=True)
        st.dataframe(bdf, use_container_width=True)
    else:
        st.markdown('<div style="background:#030609;border:1px solid #0a1a30;border-radius:8px;'
                    'padding:40px;text-align:center;color:#1a3a5a;font-family:JetBrains Mono,monospace;">'
                    'Click "Run Benchmark" in the sidebar to compare<br>'
                    'First Fit vs Best Fit vs Contiguous allocation strategies</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# TAB 6 — FORENSICS
# ══════════════════════════════════════════════════════
with tab_forensic:
    st.markdown('<div class="sec">Forensic Disk Analysis — Deep System Inspection</div>',
                unsafe_allow_html=True)

    issues = fs.forensic_analysis()

    if not issues:
        st.markdown("""
        <div style="background:#030e06;border:1px solid #004422;border-radius:8px;
                    padding:40px;text-align:center;">
          <div style="font-family:Orbitron,monospace;font-size:22px;color:#00ff88;">
               ✓ SYSTEM CLEAN</div>
          <div style="color:#00aa44;font-size:12px;font-family:JetBrains Mono,monospace;
                      margin-top:8px;">
               No orphan inodes, no leaked blocks, no corrupted blocks, no inconsistencies detected.</div>
        </div>""", unsafe_allow_html=True)
    else:
        criticals = [i for i in issues if i["severity"] == "CRITICAL"]
        warnings  = [i for i in issues if i["severity"] == "WARNING"]
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f'<div class="kpi-card kpi-red"><div class="kpi-title">CRITICAL</div>'
                        f'<div class="kpi-value">{len(criticals)}</div></div>', unsafe_allow_html=True)
        with fc2:
            st.markdown(f'<div class="kpi-card kpi-amber"><div class="kpi-title">WARNINGS</div>'
                        f'<div class="kpi-value">{len(warnings)}</div></div>', unsafe_allow_html=True)
        with fc3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">TOTAL</div>'
                        f'<div class="kpi-value">{len(issues)}</div></div>', unsafe_allow_html=True)
        st.markdown("")
        idf = pd.DataFrame(issues)
        st.dataframe(idf, use_container_width=True, height=300)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Block Ownership Map</div>', unsafe_allow_html=True)
    owned = {}
    for inode in fs.inode_table.all_inodes():
        for b in inode.blocks:
            owned[b] = inode.name

    own_html = '<div class="heatmap">'
    for i in range(fs.disk.total_blocks):
        if i < 4:
            cls, tip = "blk blk-sys", "SYSTEM"
        elif i in fs.disk.corrupted_blocks:
            cls, tip = "blk blk-corrupt", "CORRUPTED"
        elif i in owned:
            cls, tip = "blk blk-used", owned[i][:3]
        else:
            cls, tip = "blk blk-free", "free"
        own_html += f'<div class="{cls}" title="Block {i}: {tip}">{tip[:3] if i >= 4 and cls != "blk blk-free" else "·"}</div>'
    own_html += "</div>"
    st.markdown(own_html, unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 Re-run Forensic Scan", use_container_width=True):
        log("🔍 Forensic scan executed")
        st.rerun()


# ══════════════════════════════════════════════════════
# TAB 7 — DIRECTORY TREE
# ══════════════════════════════════════════════════════
with tab_tree:
    tc1, tc2 = st.columns([1,1])

    with tc1:
        st.markdown('<div class="sec">Directory Tree</div>', unsafe_allow_html=True)
        tree = fs.get_tree()
        tree_html = '<div class="terminal" style="height:340px;color:#a0c0e0;font-size:13px;">'
        for line in tree:
            tree_html += f"<div>{line}</div>"
        tree_html += "</div>"
        st.markdown(tree_html, unsafe_allow_html=True)

    with tc2:
        st.markdown('<div class="sec">Inode Table</div>', unsafe_allow_html=True)
        inodes = fs.inode_table.all_inodes()
        if inodes:
            idf = pd.DataFrame([i.to_dict() for i in inodes])
            idf["created_at"]  = pd.to_datetime(idf["created_at"],  unit="s").dt.strftime("%H:%M:%S")
            idf["modified_at"] = pd.to_datetime(idf["modified_at"], unit="s").dt.strftime("%H:%M:%S")
            idf["blocks"] = idf["blocks"].apply(str)
            st.dataframe(
                idf[["inode_id","name","file_type","size","blocks","permissions","created_at"]],
                use_container_width=True, height=340,
            )
        else:
            st.info("No inodes yet")

    # Architecture diagram
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">System Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#030609;border:1px solid #0a1a30;border-radius:8px;
                padding:20px;font-family:JetBrains Mono,monospace;font-size:11px;
                display:flex;gap:0;flex-wrap:wrap;">
      <div style="flex:1;min-width:140px;text-align:center;padding:8px;">
        <div style="color:#00d4ff;font-size:13px;font-weight:700;
                    border:1px solid #00d4ff44;border-radius:6px;padding:10px;">
             USER / STREAMLIT UI</div>
        <div style="color:#1a3a5a;">↓</div>
        <div style="color:#8866ff;border:1px solid #88448844;border-radius:6px;padding:8px;">
             FileSystem.py<br><span style="color:#444;font-size:10px;">core controller</span></div>
      </div>
      <div style="flex:1;min-width:120px;text-align:center;padding:8px;">
        <div style="color:#00ff88;border:1px solid #00aa4444;border-radius:6px;padding:8px;margin-bottom:6px;">
             Journal (WAL)<br><span style="color:#444;font-size:10px;">crash recovery</span></div>
        <div style="color:#ddaa00;border:1px solid #aa880044;border-radius:6px;padding:8px;">
             Inode Table<br><span style="color:#444;font-size:10px;">metadata</span></div>
      </div>
      <div style="flex:1;min-width:120px;text-align:center;padding:8px;">
        <div style="color:#00c0e0;border:1px solid #008890;border-radius:6px;padding:8px;margin-bottom:6px;">
             LRU Cache<br><span style="color:#444;font-size:10px;">block cache</span></div>
        <div style="color:#aa6600;border:1px solid #664400;border-radius:6px;padding:8px;">
             Bitmap<br><span style="color:#444;font-size:10px;">free space mgmt</span></div>
      </div>
      <div style="flex:1;min-width:120px;text-align:center;padding:8px;">
        <div style="color:#ff6644;border:1px solid #ff440044;border-radius:6px;padding:8px;margin-bottom:6px;">
             Directory Tree<br><span style="color:#444;font-size:10px;">path resolution</span></div>
        <div style="color:#0080cc;border:1px solid #004488;border-radius:6px;padding:8px;">
             Disk (64 blocks)<br><span style="color:#444;font-size:10px;">block storage</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)