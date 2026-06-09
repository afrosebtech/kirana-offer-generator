import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import json
import io
import textwrap

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Offer Generator",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Baloo 2', sans-serif; }

.stApp {
    background: #0a0a0a;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(34,197,94,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(251,191,36,0.08) 0%, transparent 60%);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 1rem 3rem; max-width: 680px; margin: auto; }

.app-header {
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    border-radius: 20px;
    padding: 1.4rem 1.5rem 1.1rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(22,163,74,0.4);
    text-align: center;
}
.app-header h1 { font-size: 1.8rem; font-weight: 800; color: white; margin: 0; }
.app-header p  { color: rgba(255,255,255,0.8); font-size: 0.88rem; margin: 0.2rem 0 0; font-weight: 600; }
.wa-icon { font-size: 2.2rem; display: block; margin-bottom: 0.3rem; }

.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1.1rem;
}
.card-title {
    font-size: 0.85rem; font-weight: 800; color: #22c55e;
    margin-bottom: 0.9rem; text-transform: uppercase; letter-spacing: 1px;
    display: flex; align-items: center; gap: 0.4rem;
}
.step-dot {
    width: 20px; height: 20px; background: #22c55e; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800; color: #0a0a0a; flex-shrink: 0;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.12) !important;
    border: 1.5px solid rgba(34,197,94,0.5) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #22c55e !important;
    font-size: 1rem !important;
    font-family: 'Baloo 2', sans-serif !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(255,255,255,0.35) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.35) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #22c55e !important;
    background: rgba(255,255,255,0.14) !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.18) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stRadio label, .stMultiSelect label {
    color: #94a3b8 !important; font-weight: 700 !important; font-size: 0.85rem !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: white !important;
}
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}
div[role="radiogroup"] label { color: #e2e8f0 !important; font-weight: 600 !important; }

/* Force visible text in all inputs */
input[type="text"], textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #22c55e !important;
}

.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #16a34a, #22c55e) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 0.75rem !important;
    font-size: 1.1rem !important; font-weight: 800 !important;
    font-family: 'Baloo 2', sans-serif !important;
    min-height: 54px !important;
    box-shadow: 0 4px 20px rgba(34,197,94,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 28px rgba(34,197,94,0.45) !important;
}
.stDownloadButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #d97706, #fbbf24) !important;
    color: #0a0a0a !important; border: none !important;
    border-radius: 12px !important; padding: 0.75rem !important;
    font-size: 1rem !important; font-weight: 800 !important;
    font-family: 'Baloo 2', sans-serif !important;
    min-height: 50px !important;
    box-shadow: 0 4px 20px rgba(251,191,36,0.3) !important;
}

.msg-box {
    background: #1a2e1a; border: 1.5px solid #22c55e;
    border-radius: 14px; padding: 1.1rem 1.2rem;
    color: #d1fae5; font-size: 0.95rem; line-height: 1.7;
    white-space: pre-wrap; font-family: 'Space Mono', monospace;
    margin-bottom: 0.8rem;
}
.lang-badge {
    display: inline-block; background: #22c55e; color: #0a0a0a;
    font-size: 0.7rem; font-weight: 800; padding: 2px 8px;
    border-radius: 6px; margin-bottom: 0.6rem;
    text-transform: uppercase; letter-spacing: 0.5px;
}

.info-box    { background: rgba(59,130,246,0.1);  border-left: 3px solid #3b82f6; border-radius: 0 10px 10px 0; padding: 0.65rem 1rem; color: #93c5fd; font-size: 0.88rem; font-weight: 600; margin-bottom: 0.8rem; }
.warn-box    { background: rgba(234,179,8,0.1);   border-left: 3px solid #eab308; border-radius: 0 10px 10px 0; padding: 0.65rem 1rem; color: #fde047; font-size: 0.88rem; font-weight: 600; margin-bottom: 0.8rem; }
.success-box { background: rgba(34,197,94,0.1);   border-left: 3px solid #22c55e; border-radius: 0 10px 10px 0; padding: 0.65rem 1rem; color: #86efac; font-size: 0.88rem; font-weight: 600; margin-bottom: 0.8rem; }
.error-box   { background: rgba(239,68,68,0.1);   border-left: 3px solid #ef4444; border-radius: 0 10px 10px 0; padding: 0.65rem 1rem; color: #fca5a5; font-size: 0.88rem; font-weight: 600; margin-bottom: 0.8rem; }

.divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
LANGUAGES = ["English", "Tamil", "Kannada"]
LANG_FLAGS = {"English": "🇬🇧", "Tamil": "🇮🇳 Tamil", "Kannada": "🇮🇳 Kannada"}

OFFER_TYPES = [
    "Discount % (e.g. 20% OFF)",
    "Buy 1 Get 1 Free",
    "Flat Price Drop (e.g. ₹10 off)",
    "Combo Deal (e.g. 3 for ₹100)",
    "Clearance Sale",
    "Festival Special",
]

POSTER_THEMES = {
    "🟢 Green Fresh":  {"bg": [(20,40,20),  (10,60,30)],  "accent": (34,197,94),  "dark": (10,30,10)},
    "🔴 Red Hot Deal": {"bg": [(40,10,10),  (80,20,20)],  "accent": (239,68,68),  "dark": (30,5,5)},
    "🟡 Festival Gold":{"bg": [(40,30,5),   (60,45,0)],   "accent": (251,191,36), "dark": (30,20,0)},
    "🔵 Cool Blue":    {"bg": [(10,20,50),  (15,30,80)],  "accent": (59,130,246), "dark": (5,10,40)},
}

# ─── OpenCode Zen Client ──────────────────────────────────────────────────────
def get_client():
    try:
        api_key = st.secrets["OPENCODE_API_KEY"]
    except Exception:
        st.markdown('<div class="error-box">❌ <b>OPENCODE_API_KEY</b> not found in Streamlit secrets! Neeche setup guide dekho.</div>', unsafe_allow_html=True)
        st.stop()
    return OpenAI(
        api_key=api_key,
        base_url="https://opencode.ai/zen/v1"
    )

# ─── Generate Messages ────────────────────────────────────────────────────────
def generate_messages(shop_name, product, offer_type, offer_detail, validity, tone, languages):
    client = get_client()
    lang_list = ", ".join(languages)

    prompt = f"""You are a WhatsApp marketing expert for Indian kirana (grocery) shops.

Generate attractive WhatsApp offer messages for:
Shop Name: {shop_name}
Product: {product}
Offer Type: {offer_type}
Offer Detail: {offer_detail}
Valid Until: {validity}
Tone: {tone}
Languages needed: {lang_list}

Rules:
- Use relevant emojis (max 6-8 per message)
- Keep messages short — max 8-10 lines each
- Add urgency where suitable
- End each message with shop name
- For Tamil: use proper Tamil script
- For Kannada: use proper Kannada script
- For English: simple clear Indian English
- Make it feel personal and local, not corporate

Return ONLY a valid JSON object (no markdown, no extra text):
{{"English": "message", "Tamil": "message", "Kannada": "message"}}

Only include keys for languages requested: {lang_list}"""

    response = client.chat.completions.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ─── Poster Generator ─────────────────────────────────────────────────────────
def draw_gradient(draw, x1, y1, x2, y2, c1, c2, steps=50):
    for i in range(steps):
        t = i / steps
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        y  = y1 + int((y2-y1)*i/steps)
        yn = y1 + int((y2-y1)*(i+1)/steps)
        draw.rectangle([x1,y,x2,yn], fill=(r,g,b))

def generate_poster(shop_name, product, offer_detail, validity, theme_name, lang_messages):
    theme  = POSTER_THEMES[theme_name]
    W, H   = 800, 800
    img    = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(img)

    draw_gradient(draw, 0, 0, W, H, theme["bg"][0], theme["bg"][1])

    accent = theme["accent"]
    dark   = theme["dark"]

    # Decorative circles
    for (cx,cy,cr,al) in [(660,90,200,25),(80,710,160,18),(760,660,110,15)]:
        ov = Image.new("RGBA",(W,H),(0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=(*accent,al))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Top & bottom bars
    draw.rectangle([0,0,W,10], fill=accent)
    draw.rectangle([0,H-10,W,H], fill=accent)

    # Font loading
    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
        fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 21)
    except:
        fb = fm = fs = ft = ImageFont.load_default()

    # Shop name pill
    sn = shop_name.upper()
    bb = draw.textbbox((0,0), sn, font=fm)
    tw = bb[2]-bb[0]
    draw.rectangle([W//2-tw//2-24, 22, W//2+tw//2+24, 70], fill=accent)
    draw.text((W//2-tw//2, 26), sn, font=fm, fill=dark)

    # "SPECIAL OFFER" label
    label = "✨  SPECIAL OFFER  ✨"
    bb2 = draw.textbbox((0,0), label, font=fs)
    tw2 = bb2[2]-bb2[0]
    draw.text((W//2-tw2//2, 92), label, font=fs, fill=accent)

    # Thin separator
    draw.rectangle([60,132,W-60,135], fill=accent)

    # Product name
    prod = product[:28]
    bb3  = draw.textbbox((0,0), prod, font=fb)
    tw3  = bb3[2]-bb3[0]
    draw.text((W//2-tw3//2+2, 152), prod, font=fb, fill=(0,0,0))   # shadow
    draw.text((W//2-tw3//2,   150), prod, font=fb, fill=(255,255,255))

    # Offer detail box
    draw.rectangle([50,240,W-50,390], fill=accent)
    draw.rectangle([54,244,W-54,386], fill=dark)
    lines = textwrap.wrap(offer_detail, width=26)
    yy = 258
    for ln in lines[:3]:
        bb4 = draw.textbbox((0,0), ln, font=fm)
        tw4 = bb4[2]-bb4[0]
        draw.text((W//2-tw4//2, yy), ln, font=fm, fill=accent)
        yy += 42

    # Separator
    draw.rectangle([80,408,W-80,411], fill=accent)

    # Validity
    val_txt = f"⏰  Valid Till: {validity}"
    bb5 = draw.textbbox((0,0), val_txt, font=fs)
    tw5 = bb5[2]-bb5[0]
    draw.text((W//2-tw5//2, 425), val_txt, font=fs, fill=(200,230,200))

    # Message preview (first language, first 3 lines)
    draw.rectangle([30,475,W-30,477], fill=(*accent,))
    if lang_messages:
        fl   = list(lang_messages.keys())[0]
        fmsg = lang_messages[fl]
        preview = [l for l in fmsg.split("\n") if l.strip()][:3]
        yp = 490
        for pl in preview:
            pl_short = pl[:46]+("…" if len(pl)>46 else "")
            draw.text((W//2-220, yp), pl_short, font=ft, fill=(160,210,160))
            yp += 28

    # Footer bar
    draw.rectangle([0,H-75,W,H-10], fill=accent)
    foot = f"📍 {shop_name}  ·  Share karo & Save karo!"
    bb6  = draw.textbbox((0,0), foot, font=fs)
    tw6  = bb6[2]-bb6[0]
    draw.text((W//2-tw6//2, H-58), foot, font=fs, fill=dark)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

# ═══════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <span class="wa-icon">🛒</span>
    <h1>WhatsApp Offer Generator</h1>
    <p>Kirana Shop ke liye — English · Tamil · Kannada</p>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Shop Details ──────────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-dot">1</span> Shop Ki Details</div>', unsafe_allow_html=True)

shop_name    = st.text_input("🏪 Shop ka naam", placeholder="e.g. Sri Murugan Stores")
product      = st.text_input("📦 Product / Item", placeholder="e.g. Sunflower Oil 1L, Rice 5kg")
col1, col2   = st.columns(2)
with col1:
    offer_type = st.selectbox("🏷️ Offer Type", OFFER_TYPES)
with col2:
    validity   = st.text_input("📅 Valid Till", placeholder="e.g. 15 June 2026")
offer_detail = st.text_input("💰 Offer Detail", placeholder="e.g. ₹120 only! (Was ₹150)")
st.markdown('</div>', unsafe_allow_html=True)

# ── Step 2: Message Settings ──────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-dot">2</span> Message Settings</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    tone = st.selectbox("🎯 Tone", ["Friendly & Warm","Urgent & Exciting","Simple & Clear","Festival Mood"])
with col4:
    selected_langs = st.multiselect("🌐 Languages", LANGUAGES, default=LANGUAGES)
st.markdown('</div>', unsafe_allow_html=True)

# ── Step 3: Poster Theme ──────────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-dot">3</span> Poster Theme</div>', unsafe_allow_html=True)
poster_theme = st.radio("Color theme:", list(POSTER_THEMES.keys()), horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Validation ────────────────────────────────────────
all_filled = all([shop_name, product, offer_detail, validity])
if not all_filled:
    st.markdown('<div class="warn-box">⚠️ Saari details bharo — phir Generate karo.</div>', unsafe_allow_html=True)

generate = st.button("✨ Generate Messages + Poster")

# ── Generate ──────────────────────────────────────────
if generate:
    if not all_filled:
        st.markdown('<div class="warn-box">⚠️ Pehle saari fields bharo!</div>', unsafe_allow_html=True)
        st.stop()
    if not selected_langs:
        st.markdown('<div class="warn-box">⚠️ Kam se kam ek language select karo.</div>', unsafe_allow_html=True)
        st.stop()

    with st.spinner("🤖 AI messages likh raha hai..."):
        try:
            msgs = generate_messages(shop_name, product, offer_type, offer_detail, validity, tone, selected_langs)
            st.session_state["messages"] = msgs
            st.session_state["generated"] = True
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Message error: {e}</div>', unsafe_allow_html=True)
            st.stop()

    with st.spinner("🎨 Poster ban raha hai..."):
        try:
            poster = generate_poster(shop_name, product, offer_detail, validity, poster_theme, msgs)
            st.session_state["poster"] = poster
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Poster error: {e}</div>', unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────
if st.session_state.get("generated"):
    msgs = st.session_state.get("messages", {})
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Messages
    st.markdown('<div class="card"><div class="card-title">💬 WhatsApp Messages</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">👇 Text box mein select all (Ctrl+A) → Copy → WhatsApp pe paste karo!</div>', unsafe_allow_html=True)

    for lang in selected_langs:
        if lang in msgs:
            flag = LANG_FLAGS.get(lang, lang)
            st.markdown(f'<div class="lang-badge">{flag}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-box">{msgs[lang]}</div>', unsafe_allow_html=True)
            st.text_area("Copy karo:", value=msgs[lang], height=170, key=f"ta_{lang}", label_visibility="collapsed")
            st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Poster
    if st.session_state.get("poster"):
        st.markdown('<div class="card"><div class="card-title">🎨 Offer Poster</div>', unsafe_allow_html=True)
        st.image(st.session_state["poster"], use_container_width=True, caption="WhatsApp Status / Story ready!")
        st.markdown('<div class="success-box">✅ Poster ready! Download karo → WhatsApp Status pe lagao.</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Poster Download Karo (PNG)",
            data=st.session_state["poster"],
            file_name=f"offer_{shop_name.replace(' ','_')}.png",
            mime="image/png",
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align:center;margin-top:2rem;color:rgba(255,255,255,0.15);font-size:0.75rem;font-weight:700;'>
    OFFER GENERATOR · Powered by OpenCode Zen AI · Made for Kirana Shops
</div>
""", unsafe_allow_html=True)
