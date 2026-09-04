"""CSS styles + inject_css(). Gọi một lần khi app khởi động."""
import streamlit as st

STYLES_CSS = """
<style>
:root {
    --bg-main: #F8FAFC; --card-bg: #FFFFFF; --card-border: #E2E8F0;
    --text-primary: #0F172A; --text-secondary: #475569;
    --kpi-label: #64748B; --kpi-border: #E2E8F0;
    --accent: #2563eb; --svg-stroke: #2563eb;
    --r-sm: 8px; --r-md: 12px; --r-full: 999px;
    --sp1:.25rem; --sp2:.5rem; --sp3:.75rem; --sp4:1rem; --sp5:1.25rem; --sp6:1.5rem;
}
@media(prefers-color-scheme:dark),(data-theme=dark){
    :root{--bg-main:#0F172A;--card-bg:#1E293B;--card-border:#334155;
          --text-primary:#F8FAFC;--text-secondary:#94A3B8;--kpi-label:#94A3B8;
          --kpi-border:#334155;--accent:#3B82F6;--svg-stroke:#60A5FA}
    .badge-tone{background:#1e3a5f;color:#93c5fd}
    .error-banner--yellow{background:#422006;border-color:#a16207;color:#fef08a}
    .error-banner--orange{background:#431407;border-color:#c2410c;color:#fed7aa}
    .error-banner--red{background:#450a0a;border-color:#b91c1c;color:#fca5a5}
    .error-banner--gray{background:#1e293b;border-color:#475569;color:#94a3b8}
    .focus-card.selected{background:#1e3a5f}
}
.main-title{font-size:2.2rem;font-weight:800;color:var(--text-primary);letter-spacing:-.02em;margin-bottom:.25rem}
.subtitle{font-size:1.05rem;color:var(--text-secondary);margin-bottom:1.75rem}
.prod-card{background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--r-md);padding:var(--sp6);margin-bottom:var(--sp5);box-shadow:0 1px 3px 0 rgba(0,0,0,.05)}
.prod-card-title{font-size:1.1rem;font-weight:700;color:var(--text-primary);margin-bottom:var(--sp3);display:flex;align-items:center;gap:8px}
.kpi-container{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--sp4);margin-bottom:var(--sp6)}
.kpi-box{background:var(--card-bg);border:1px solid var(--kpi-border);border-radius:10px;padding:var(--sp4) var(--sp5);box-shadow:0 1px 2px 0 rgba(0,0,0,.03)}
.kpi-box-label{font-size:.75rem;font-weight:600;color:var(--kpi-label);text-transform:uppercase;letter-spacing:.05em;margin-bottom:var(--sp1)}
.kpi-box-value{font-size:1.15rem;font-weight:700;color:var(--text-primary)}
.stButton>button{background-color:var(--accent)!important;color:white!important;font-weight:700!important;font-size:1.05rem!important;padding:.75rem 2rem!important;border-radius:var(--r-sm)!important;border:none!important;box-shadow:0 4px 6px -1px rgba(37,99,235,.2)!important;transition:all .2s ease!important}
.stButton>button:hover{opacity:.9!important;box-shadow:0 6px 12px -2px rgba(37,99,235,.3)!important}
.step-indicator{display:flex;align-items:center;gap:0;margin-bottom:var(--sp6);font-family:inherit}
.step-item{display:flex;align-items:center;gap:8px;padding:6px 16px;border-radius:var(--r-full);font-size:.875rem;font-weight:500;color:var(--text-secondary);background:var(--card-bg);border:1px solid var(--card-border);transition:all .2s}
.step-item--active{color:var(--accent);border-color:var(--accent);font-weight:700}
.step-item--done{color:#16a34a;border-color:#16a34a}
.step-item--locked{color:var(--kpi-label);opacity:.6}
.step-sep{width:24px;height:2px;background:var(--card-border);flex-shrink:0}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3rem 1.5rem;text-align:center;color:var(--text-secondary)}
.empty-state-icon{font-size:3rem;margin-bottom:1rem;opacity:.5}
.empty-state-title{font-size:1.1rem;font-weight:700;color:var(--text-primary);margin-bottom:.5rem}
.badge-tone{display:inline-block;padding:2px 10px;border-radius:var(--r-full);font-size:.75rem;font-weight:600;background:#dbeafe;color:#1d4ed8}
.error-banner{padding:.75rem 1rem;border-radius:var(--r-sm);margin-bottom:1rem;display:flex;align-items:center;gap:.5rem;font-size:.9rem}
.error-banner--yellow{background:#fef9c3;border:1px solid #eab308;color:#713f12}
.error-banner--orange{background:#ffedd5;border:1px solid #f97316;color:#7c2d12}
.error-banner--red{background:#fee2e2;border:1px solid #ef4444;color:#7f1d1d}
.error-banner--gray{background:#f1f5f9;border:1px solid #94a3b8;color:#475569}
.action-row{display:grid;grid-template-columns:2fr 1fr 1fr;gap:1rem;padding:.75rem 1rem;background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--r-sm);margin-bottom:.5rem;font-size:.9rem}
.action-row-task{font-weight:600;color:var(--text-primary)}
.action-row-assignee,.action-row-deadline{color:var(--text-secondary)}
.action-row-deadline{font-style:italic}
.focus-card{background:var(--card-bg);border:2px solid var(--card-border);border-radius:var(--r-md);padding:1.25rem;cursor:pointer;transition:all .2s;text-align:center}
.focus-card:hover{border-color:var(--accent)}
.focus-card.selected{border-color:var(--accent);background:#eff6ff}
.dropzone{border:2px dashed var(--card-border);border-radius:var(--r-md);padding:2.5rem;text-align:center;transition:all .2s;background:var(--card-bg)}
.dropzone:hover{border-color:var(--accent)}
*:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style>"""


def inject_css():
    """Inject all CSS styles (gọi một lần lúc app startup)."""
    st.markdown(STYLES_CSS, unsafe_allow_html=True)
