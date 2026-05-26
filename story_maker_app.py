"""
AI Story Maker — Story Forge v3
- Groq (free) + OpenAI (optional) story generation
- Relevant images via Unsplash
- New features: Story history, regenerate, reading mode, story rating
- Added features: Groq model selector, prompt enhancer, narrator style, plot twist mode, character card, soundtrack mood, and Markdown export

"""

import streamlit as st
import requests
import textwrap
import io
import json
import time
from datetime import datetime
from PIL import Image, ImageDraw
from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import List, Optional

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Story Forge — AI Story Maker",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e0e12;
    color: #e8e4dc;
}
.stApp { background: radial-gradient(ellipse at 20% 0%, #1a1025 0%, #0e0e12 60%); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #13121a !important; border-right: 1px solid #2a2535; }
[data-testid="stSidebar"] * { color: #c8c4bc !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label {
    font-size: 0.78rem !important; letter-spacing: 0.08em;
    text-transform: uppercase; color: #7a7590 !important;
}
.hero-title { font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 700;
    line-height: 1.1; color: #f0ebe0; letter-spacing: -0.02em; margin-bottom: 0.2rem; }
.hero-subtitle { font-family: 'Playfair Display', serif; font-style: italic;
    font-size: 1.2rem; color: #9b8fa8; margin-bottom: 2rem; }
.story-card { background: linear-gradient(135deg, #17151f 0%, #1c1828 100%);
    border: 1px solid #2e2a3d; border-radius: 12px; padding: 2rem; margin: 1rem 0; }
.scene-card { background: #13121a; border-left: 3px solid #7c5cbf;
    border-radius: 0 8px 8px 0; padding: 1.5rem; margin: 1.2rem 0; }
.scene-number { font-family: 'Playfair Display', serif; font-size: 0.75rem;
    letter-spacing: 0.2em; text-transform: uppercase; color: #7c5cbf; margin-bottom: 0.3rem; }
.scene-title { font-family: 'Playfair Display', serif; font-size: 1.4rem;
    font-weight: 700; color: #f0ebe0; margin-bottom: 0.8rem; }
.scene-desc { font-size: 0.95rem; color: #a09cb0; line-height: 1.7; margin-bottom: 1rem; }
.image-prompt-box { background: #0e0e12; border: 1px dashed #3d3850; border-radius: 6px;
    padding: 0.7rem 1rem; font-size: 0.78rem; color: #5e5a75; font-style: italic; }
.story-title { font-family: 'Playfair Display', serif; font-size: 2.2rem;
    font-weight: 700; color: #f0ebe0; margin-bottom: 0.5rem; }
.story-body { font-size: 1rem; color: #c8c4bc; line-height: 1.9; white-space: pre-line; }
.reading-mode { font-family: 'Playfair Display', serif; font-size: 1.15rem;
    color: #e8e4dc; line-height: 2.1; white-space: pre-line; max-width: 680px; margin: 0 auto; }
.word-count { font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: #4a4760; margin-top: 1rem; }
.genre-badge { display: inline-block; background: #2a1f42; color: #9b7de0;
    border: 1px solid #3d2f5e; border-radius: 20px; padding: 0.2rem 0.8rem;
    font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase;
    margin-right: 0.5rem; margin-bottom: 1rem; }
.step-box { background: #17151f; border: 1px solid #2e2a3d; border-radius: 10px;
    padding: 1.2rem 1.5rem; margin-bottom: 1rem; display:flex; gap:1rem; align-items:flex-start; }
.section-divider { border: none; border-top: 1px solid #2a2535; margin: 2rem 0; }
.history-card { background: #17151f; border: 1px solid #2e2a3d; border-radius: 10px;
    padding: 1rem 1.4rem; margin-bottom: 0.8rem; cursor: pointer; }
.history-title { font-family: 'Playfair Display', serif; font-size: 1rem;
    color: #f0ebe0; font-weight: 700; margin-bottom: 0.2rem; }
.history-meta { font-size: 0.75rem; color: #4a4760; letter-spacing: 0.05em; }
.provider-badge-groq { background: #0f2a20; color: #3ecf8e; border: 1px solid #1a4a35;
    border-radius: 20px; padding: 0.2rem 0.8rem; font-size: 0.72rem; letter-spacing: 0.1em;
    text-transform: uppercase; margin-right: 0.4rem; }
.provider-badge-openai { background: #0f1e2a; color: #3e8ecf; border: 1px solid #1a3545;
    border-radius: 20px; padding: 0.2rem 0.8rem; font-size: 0.72rem; letter-spacing: 0.1em;
    text-transform: uppercase; margin-right: 0.4rem; }
.stat-box { background: #17151f; border: 1px solid #2e2a3d; border-radius: 10px;
    padding: 1rem; text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700;
    color: #7c5cbf; line-height: 1; }
.stat-label { font-size: 0.72rem; color: #4a4760; text-transform: uppercase;
    letter-spacing: 0.1em; margin-top: 0.3rem; }
.feature-chip { display:inline-block; background:#17151f; border:1px solid #2e2a3d; border-radius:999px;
    padding:0.35rem 0.8rem; margin:0.25rem 0.35rem 0.25rem 0; color:#a09cb0; font-size:0.78rem; }
.character-card { background:#111018; border:1px solid #2e2a3d; border-radius:12px; padding:1rem 1.2rem;
    margin:1rem 0; color:#a09cb0; line-height:1.7; }
.stButton > button { background: linear-gradient(135deg, #5c3d9e 0%, #7c5cbf 100%) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    letter-spacing: 0.05em !important; padding: 0.6rem 1.8rem !important;
    font-size: 0.92rem !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.88 !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #2a2535; gap: 0; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #5e5a75 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    border-radius: 0 !important; padding: 0.7rem 1.5rem !important; }
.stTabs [aria-selected="true"] { color: #c8a8f0 !important; border-bottom: 2px solid #7c5cbf !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────
class StoryRequest(BaseModel):
    prompt: str
    genre: str = "mystery"
    tone: str = "suspenseful"
    num_scenes: int = 3
    length: int = 400
    character_name: str = "Elara"
    setting: str = "a rain-soaked old city"
    provider: str = "groq"
    model: str = "llama3-8b-8192"
    narrator_style: str = "cinematic"
    plot_twist: bool = True

@dataclass
class Scene:
    scene_number: int
    title: str
    description: str
    image_prompt: str
    image_url: Optional[str] = None

@dataclass
class StoryResult:
    title: str
    story: str
    scenes: List[Scene]
    word_count: int
    provider: str = "groq"
    generated_at: str = ""
    character_card: str = ""
    soundtrack_mood: str = ""

GENRE_DETAILS = {
    "mystery":   {"emoji": "🔍", "color": "#4a6fa5", "vibe": "dark, foggy, suspenseful"},
    "fantasy":   {"emoji": "✨", "color": "#7c5cbf", "vibe": "magical, ethereal, wondrous"},
    "sci-fi":    {"emoji": "🚀", "color": "#3a9e8f", "vibe": "futuristic, neon, technological"},
    "thriller":  {"emoji": "⚡", "color": "#b05a3a", "vibe": "tense, high-stakes, urgent"},
    "adventure": {"emoji": "🗺️", "color": "#7a9e3a", "vibe": "bold, sweeping, epic"},
    "romance":   {"emoji": "🌹", "color": "#a03a6a", "vibe": "tender, emotional, evocative"},
    "horror":    {"emoji": "🕷️", "color": "#6a3a3a", "vibe": "eerie, dark, unsettling"},
}

TONE_WORDS = {
    "suspenseful": "suspenseful",
    "dramatic":    "dramatic",
    "dark":        "dark and ominous",
    "lighthearted":"lighthearted and warm",
    "humorous":    "humorous and witty",
    "emotional":   "deeply emotional",
    "action-packed":"fast-paced and action-packed",
}

NARRATOR_STYLES = {
    "cinematic": "cinematic and visually rich",
    "first-person": "first-person, intimate, and reflective",
    "storybook": "storybook-like, warm, and imaginative",
    "noir": "noir-inspired, moody, and sharp",
    "young-adult": "young-adult style, clear, emotional, and fast-moving",
}

GROQ_MODELS = {
    "Llama 3 8B — fast/free": "llama3-8b-8192",
    "Llama 3 70B — stronger writing": "llama3-70b-8192",
    "Mixtral 8x7B — creative alternative": "mixtral-8x7b-32768",
}


# ─────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────
def build_prompt(req: StoryRequest) -> str:
    scene_blocks = "\n".join([
        f"""SCENE {i}
Title: [scene {i} title]
Description: [2-3 sentences — specific to what happens in this scene]
Image Prompt: [vivid visual description for image generation — include lighting, mood, key visual elements]"""
        for i in range(1, req.num_scenes + 1)
    ])
    twist_instruction = "Include a satisfying final plot twist that still feels earned." if req.plot_twist else "Do not force a twist ending; focus on a clean resolution."
    narrator = NARRATOR_STYLES.get(req.narrator_style, req.narrator_style)
    return f"""You are a creative fiction writer. Write a {TONE_WORDS.get(req.tone, req.tone)} {req.genre} story in a {narrator} narration style.

Protagonist: {req.character_name}
Setting: {req.setting}
Story prompt: {req.prompt}
Special instruction: {twist_instruction}

IMPORTANT: Write a completely original story based on this exact prompt. Do not use generic templates or placeholder text. Every sentence should feel specific to what the user described.

Structure your response EXACTLY like this:

TITLE: [a compelling title that fits this specific story]

CHARACTER CARD:
[3-4 short lines describing the protagonist's role, motivation, fear, and hidden strength]

SOUNDTRACK MOOD:
[5-8 words describing the music or atmosphere that would fit this story]

STORY:
[Write a complete, vivid story of approximately {req.length} words. Be specific, creative, and original. Every detail should connect to the prompt given.]

{scene_blocks}

Write only the structured output above. Make every element feel unique and tied directly to the prompt."""


# ─────────────────────────────────────────────
# STORY PARSER
# ─────────────────────────────────────────────
def parse_story(raw: str, req: StoryRequest, provider: str) -> StoryResult:
    import re

    title_match = re.search(r'TITLE:\s*(.+)', raw)
    title = title_match.group(1).strip() if title_match else "Untitled"

    character_match = re.search(r'CHARACTER CARD:\s*(.+?)(?=SOUNDTRACK MOOD:|STORY:)', raw, re.DOTALL)
    character_card = character_match.group(1).strip() if character_match else f"{req.character_name} is the central character, shaped by the setting and conflict."

    soundtrack_match = re.search(r'SOUNDTRACK MOOD:\s*(.+?)(?=STORY:)', raw, re.DOTALL)
    soundtrack_mood = soundtrack_match.group(1).strip() if soundtrack_match else f"{req.tone}, {req.genre}, cinematic atmosphere"

    story_match = re.search(r'STORY:\s*(.+?)(?=SCENE\s*1)', raw, re.DOTALL)
    story = story_match.group(1).strip() if story_match else raw[:800]

    scenes = []
    scene_blocks = re.findall(
        r'SCENE\s*(\d+)\s*Title:\s*(.+?)\s*Description:\s*(.+?)\s*Image Prompt:\s*(.+?)(?=SCENE\s*\d+|$)',
        raw, re.DOTALL
    )
    for num, sc_title, desc, img_prompt in scene_blocks:
        scenes.append(Scene(
            scene_number=int(num),
            title=sc_title.strip(),
            description=desc.strip(),
            image_prompt=img_prompt.strip()
        ))

    if not scenes:
        for i in range(1, req.num_scenes + 1):
            scenes.append(Scene(
                scene_number=i,
                title=f"Scene {i}",
                description="Scene description unavailable — try regenerating.",
                image_prompt=f"{req.tone} {req.genre} cinematic scene, {req.setting}"
            ))

    return StoryResult(
        title=title,
        story=story,
        scenes=scenes[:req.num_scenes],
        word_count=len(story.split()),
        provider=provider,
        generated_at=datetime.now().strftime("%d %b %Y, %H:%M"),
        character_card=character_card,
        soundtrack_mood=soundtrack_mood
    )


# ─────────────────────────────────────────────
# GROQ STORY GENERATION (free)
# ─────────────────────────────────────────────
def generate_story_groq(req: StoryRequest, api_key: str) -> StoryResult:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": "You are a skilled creative fiction writer. You write vivid, original stories tailored precisely to the user's prompt. Always follow the exact structure requested."},
            {"role": "user", "content": build_prompt(req)}
        ],
        "max_tokens": 1800,
        "temperature": 0.9
    }
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=payload, timeout=60
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    return parse_story(raw, req, "groq")


# ─────────────────────────────────────────────
# OPENAI STORY GENERATION (optional)
# ─────────────────────────────────────────────
def generate_story_openai(req: StoryRequest, api_key: str) -> StoryResult:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a skilled creative fiction writer. Write vivid, original stories tailored precisely to the prompt."},
            {"role": "user", "content": build_prompt(req)}
        ],
        "max_tokens": 1800,
        "temperature": 0.9
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers, json=payload, timeout=60
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    return parse_story(raw, req, "openai")


def generate_story(req: StoryRequest, groq_key: str = "", openai_key: str = "") -> StoryResult:
    if req.provider == "groq" and groq_key:
        return generate_story_groq(req, groq_key)
    elif req.provider == "openai" and openai_key:
        return generate_story_openai(req, openai_key)
    else:
        raise ValueError("No valid API key provided for the selected provider.")


# ─────────────────────────────────────────────
# IMAGES — Unsplash (no key needed)
# ─────────────────────────────────────────────
GENRE_IMAGE_KEYWORDS = {
    "mystery":   "mystery dark fog night",
    "fantasy":   "fantasy magical forest glowing",
    "sci-fi":    "futuristic neon city technology",
    "thriller":  "suspense dramatic shadows cinematic",
    "adventure": "adventure landscape journey epic",
    "romance":   "romance sunset tender emotional",
    "horror":    "horror dark eerie abandoned",
}

def build_image_query(scene: Scene, req: StoryRequest) -> str:
    genre_kw = GENRE_IMAGE_KEYWORDS.get(req.genre, req.genre)
    setting_words = " ".join(req.setting.replace("a ", "").replace("an ", "").split()[:3])
    return f"{setting_words} {genre_kw}"

def fetch_scene_image(scene: Scene, req: StoryRequest) -> Optional[str]:
    query = build_image_query(scene, req).replace(" ", ",")
    return f"https://source.unsplash.com/800x450/?{query}"

def load_image_from_url(url: str) -> Optional[Image.Image]:
    try:
        resp = requests.get(url, timeout=12, allow_redirects=True)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception:
        return None

GENRE_PALETTES = {
    "mystery":   [(20, 25, 40), (60, 80, 120), (180, 160, 200)],
    "fantasy":   [(25, 15, 40), (100, 60, 160), (220, 180, 255)],
    "sci-fi":    [(10, 25, 30), (30, 130, 120), (100, 220, 200)],
    "thriller":  [(25, 15, 10), (140, 60, 30), (220, 140, 80)],
    "adventure": [(15, 25, 10), (60, 110, 40), (180, 220, 100)],
    "romance":   [(40, 15, 25), (160, 60, 100), (220, 160, 180)],
    "horror":    [(15, 10, 10), (80, 30, 30), (160, 80, 80)],
}

def create_fallback_image(scene: Scene, genre: str, setting: str) -> Image.Image:
    W, H = 768, 432
    palette = GENRE_PALETTES.get(genre, GENRE_PALETTES["mystery"])
    bg, mid, fg = palette
    img = Image.new("RGB", (W, H), color=bg)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(bg[0] + (mid[0]-bg[0])*y/H)
        g = int(bg[1] + (mid[1]-bg[1])*y/H)
        b = int(bg[2] + (mid[2]-bg[2])*y/H)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    draw.rectangle([0, 0, 6, H], fill=fg)
    for i, line in enumerate(textwrap.wrap(f"Scene {scene.scene_number}: {scene.title}", width=32)):
        draw.text((24, 40 + i*28), line, fill=fg)
    draw.text((24, H-40), setting[:60], fill=fg)
    draw.text((W-200, H-24), "[ image unavailable ]", fill=(80,80,90))
    return img

def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "result": None, "req": None, "page": "home",
    "images": {}, "history": [], "reading_mode": False,
    "rating": None, "regenerate_count": 0, "last_prompt": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 Story Forge")

    st.markdown("<div style='font-size:0.78rem;color:#4a4760;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>AI Provider</div>", unsafe_allow_html=True)

    provider = st.selectbox(
        "Provider",
        options=["groq", "openai"],
        format_func=lambda p: "🟢  Groq — Free (Llama 3)" if p == "groq" else "🔵  OpenAI — GPT-3.5",
        label_visibility="collapsed"
    )

    if provider == "groq":
        groq_key = st.text_input("Groq API Key (free)", type="password",
            placeholder="gsk_…",
            help="Get a free key at console.groq.com — no card needed")
        selected_groq_model_label = st.selectbox("Groq Model", options=list(GROQ_MODELS.keys()))
        groq_model = GROQ_MODELS[selected_groq_model_label]
        openai_key = ""
        st.markdown("<div style='font-size:0.75rem;color:#3ecf8e;margin-top:0.3rem;'>✓ Free — no credit card required</div>", unsafe_allow_html=True)
    else:
        groq_model = "gpt-3.5-turbo"
        openai_key = st.text_input("OpenAI API Key", type="password",
            placeholder="sk-…",
            help="Get a key at platform.openai.com")
        groq_key = ""
        st.markdown("<div style='font-size:0.75rem;color:#3e8ecf;margin-top:0.3rem;'>~$0.002 per story — set a $5 cap to be safe</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.78rem;color:#4a4760;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>Story Settings</div>", unsafe_allow_html=True)

    genre = st.selectbox("Genre", options=list(GENRE_DETAILS.keys()),
        format_func=lambda g: f"{GENRE_DETAILS[g]['emoji']}  {g.capitalize()}")
    tone = st.selectbox("Tone", options=list(TONE_WORDS.keys()),
        format_func=lambda t: t.capitalize())
    num_scenes = st.slider("Scenes", min_value=2, max_value=5, value=3)
    story_length = st.slider("Word count", min_value=150, max_value=600, value=350, step=50)
    narrator_style = st.selectbox("Narrator style", options=list(NARRATOR_STYLES.keys()),
        format_func=lambda n: n.replace("-", " ").title())
    plot_twist = st.toggle("Add plot twist ending", value=True)

    st.markdown("---")
    character_name = st.text_input("Protagonist", value="Elara")
    setting = st.text_input("Setting", value="a rain-soaked old city")

    st.markdown("---")
    st.markdown("<div style='font-size:0.78rem;color:#4a4760;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.8rem;'>Navigate</div>", unsafe_allow_html=True)
    for label, pg in [("🏠  Home", "home"), ("✍️  Generate", "generate"),
                       ("📚  History", "history"), ("📊  Stats", "stats")]:
        if st.button(label, use_container_width=True):
            st.session_state.page = pg
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown('<div class="hero-title">Story Forge</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-powered narrative generation — unique stories for every prompt</div>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:1rem;color:#9b8fa8;line-height:1.8;max-width:660px;margin-bottom:2rem;'>
    Story Forge uses AI to write a completely original story for every prompt you enter.
    Choose between <strong style='color:#3ecf8e;'>Groq (free)</strong> or
    <strong style='color:#3e8ecf;'>OpenAI</strong>, pick your genre and tone,
    and get a fully structured narrative complete with scenes and matched imagery —
    all in seconds.
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    st.markdown("### What you get")
    fc1, fc2, fc3 = st.columns(3)
    fc4, fc5, fc6 = st.columns(3)
    for col, icon, title, desc in [
        (fc1, "⚡", "Groq generation", "Use free Groq-powered Llama models for fast story generation, or switch to OpenAI if preferred."),
        (fc2, "✨", "Prompt enhancer", "Turn a simple idea into a richer prompt before generating the story."),
        (fc3, "🎭", "Narrator styles", "Choose cinematic, first-person, storybook, noir, or young-adult narration."),
        (fc4, "🌀", "Plot twist mode", "Optionally add an earned twist ending to make stories more memorable."),
        (fc5, "🎬", "Scene breakdown", "Your story is split into vivid scenes with image prompts and matched photos."),
        (fc6, "📥", "Markdown export", "Download the story in clean Markdown format for reports, portfolios, or future editing."),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box" style='text-align:left;padding:1.2rem;'>
                <div style='font-size:1.6rem;margin-bottom:0.5rem;'>{icon}</div>
                <div style='font-family:"Playfair Display",serif;font-size:0.95rem;color:#f0ebe0;font-weight:700;margin-bottom:0.3rem;'>{title}</div>
                <div style='font-size:0.78rem;color:#5e5a75;line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # How it works
    st.markdown("### How it works")
    for num, title, desc in [
        ("1", "Get a free Groq API key",
         "Go to console.groq.com, sign up for free (no card needed), and create an API key. Paste it in the sidebar under Groq API Key. Alternatively use an OpenAI key if you prefer GPT."),
        ("2", "Configure your story",
         "Choose your genre, tone, number of scenes, protagonist name, setting, Groq model, narrator style, and whether to include a plot twist ending."),
        ("3", "Write or enhance your prompt",
         "Head to the Generate page and describe the core idea of your story. Use Enhance Prompt if you want the app to make your idea more detailed before generation."),
        ("4", "Generate and explore",
         "Click Generate Story. The AI writes a fully original narrative broken into scenes. Each scene comes with a description, an image prompt for Stable Diffusion, and a real matched photo."),
        ("5", "Regenerate if you want",
         "Not happy with the result? Hit Regenerate to get a completely different version of the same prompt — the AI never produces the same story twice."),
        ("6", "Rate and save",
         "Rate your story out of 5 stars. All generated stories are saved in the History tab so you can revisit, compare, and export any of them."),
        ("7", "Export your story",
         "Download the full story as a text file or Markdown file, and copy individual image prompts to use in Stable Diffusion, Midjourney, or DALL·E."),
    ]:
        st.markdown(f"""
        <div class="step-box">
            <div style='font-family:"Playfair Display",serif;font-size:1.8rem;font-weight:700;color:#7c5cbf;min-width:2.2rem;line-height:1;'>{num}</div>
            <div>
                <div style='font-family:"Playfair Display",serif;font-size:1rem;color:#f0ebe0;margin-bottom:0.3rem;font-weight:700;'>{title}</div>
                <div style='font-size:0.88rem;color:#7a7590;line-height:1.6;'>{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Provider comparison
    st.markdown("### Groq vs OpenAI — which should I use?")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("""
        <div style='background:#0f2a20;border:1px solid #1a4a35;border-radius:10px;padding:1.4rem;'>
            <div style='font-size:1rem;font-weight:700;color:#3ecf8e;margin-bottom:0.8rem;'>🟢 Groq — Llama 3 (Recommended)</div>
            <div style='font-size:0.85rem;color:#a0c8b8;line-height:1.8;'>
                ✓ Completely free — no card needed<br>
                ✓ Fast responses<br>
                ✓ Good story quality for most use cases<br>
                ✓ Great for testing and development<br>
                ✗ Slightly less consistent structure<br>
                ✗ Less creative on complex prompts
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cc2:
        st.markdown("""
        <div style='background:#0f1e2a;border:1px solid #1a3545;border-radius:10px;padding:1.4rem;'>
            <div style='font-size:1rem;font-weight:700;color:#3e8ecf;margin-bottom:0.8rem;'>🔵 OpenAI — GPT-3.5</div>
            <div style='font-size:0.85rem;color:#a0b8c8;line-height:1.8;'>
                ✓ Higher story quality and creativity<br>
                ✓ More reliable scene structure<br>
                ✓ ~$0.002 per story (very cheap)<br>
                ✓ Industry standard — good experience<br>
                ✗ Requires a credit card for billing<br>
                ✗ Set a $5 monthly cap to be safe
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("### Available genres")
    gcols = st.columns(len(GENRE_DETAILS))
    for col, (gkey, gval) in zip(gcols, GENRE_DETAILS.items()):
        with col:
            st.markdown(f"""
            <div style='background:#17151f;border:1px solid #2e2a3d;border-radius:10px;padding:1rem;text-align:center;'>
                <div style='font-size:1.6rem;margin-bottom:0.3rem;'>{gval['emoji']}</div>
                <div style='font-family:"Playfair Display",serif;font-size:0.85rem;color:#f0ebe0;font-weight:700;'>{gkey.capitalize()}</div>
                <div style='font-size:0.7rem;color:#4a4760;margin-top:0.2rem;'>{gval['vibe']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("✍️  Start generating →"):
        st.session_state.page = "generate"
        st.rerun()


# ─────────────────────────────────────────────
# PAGE: GENERATE
# ─────────────────────────────────────────────
elif st.session_state.page == "generate":

    st.markdown('<div class="hero-title" style="font-size:2.4rem;">Generate Your Story</div>', unsafe_allow_html=True)

    provider_badge = f'<span class="provider-badge-groq">🟢 Groq</span>' if provider == "groq" else f'<span class="provider-badge-openai">🔵 OpenAI</span>'
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        {provider_badge}
        <span class="genre-badge">{GENRE_DETAILS[genre]['emoji']} {genre.capitalize()}</span>
        <span class="genre-badge">🎭 {tone.capitalize()}</span>
        <span class="genre-badge">🎬 {num_scenes} scenes</span>
    </div>
    """, unsafe_allow_html=True)

    prompt = st.text_area(
        "Your story prompt",
        value=st.session_state.last_prompt,
        placeholder="e.g. Max, in a crowded city alleyway, stumbles upon a glowing magical gate that wasn't there yesterday…",
        height=110,
        help="The more specific your prompt, the more unique your story. Include character names, locations and the key event."
    )

    enh_col1, enh_col2 = st.columns([1, 4])
    with enh_col1:
        enhance_clicked = st.button("🪄 Enhance Prompt", use_container_width=True)
    with enh_col2:
        if enhance_clicked:
            base = prompt.strip() or f"{character_name} faces an unexpected conflict in {setting}"
            st.session_state.last_prompt = (
                f"{base}. Add a clear central conflict, one surprising discovery, emotional stakes for {character_name}, "
                f"and a vivid final moment that fits the {genre} genre and {tone} tone."
            )
            st.rerun()

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        generate_clicked = st.button("✨  Generate", use_container_width=True)
    with col2:
        regen_clicked = st.button("🔄  Regenerate", use_container_width=True,
            disabled=st.session_state.result is None)
    with col3:
        reading_mode = st.toggle("📖 Reading mode", value=st.session_state.reading_mode)
        st.session_state.reading_mode = reading_mode

    def run_generation(prompt_text):
        api_key = groq_key if provider == "groq" else openai_key
        if not api_key.strip():
            provider_name = "Groq (console.groq.com)" if provider == "groq" else "OpenAI (platform.openai.com)"
            st.error(f"Please add your {provider_name} API key in the sidebar.")
            return
        if not prompt_text.strip():
            st.warning("Please enter a story prompt.")
            return

        with st.spinner(f"Writing your story with {'Groq (Llama 3)' if provider == 'groq' else 'OpenAI GPT-3.5'}…"):
            try:
                req = StoryRequest(
                    prompt=prompt_text, genre=genre, tone=tone,
                    num_scenes=num_scenes, length=story_length,
                    character_name=character_name, setting=setting,
                    provider=provider, model=groq_model,
                    narrator_style=narrator_style, plot_twist=plot_twist
                )
                result = generate_story(req, groq_key=groq_key, openai_key=openai_key)
                st.session_state.result = result
                st.session_state.req    = req
                st.session_state.rating = None
                st.session_state.regenerate_count += 1

                # Fetch scene images
                images = {}
                with st.spinner("Fetching scene images…"):
                    for scene in result.scenes:
                        url = fetch_scene_image(scene, req)
                        img = load_image_from_url(url)
                        images[scene.scene_number] = img if img else create_fallback_image(scene, req.genre, req.setting)
                st.session_state.images = images

                # Save to history
                st.session_state.history.append({
                    "title": result.title,
                    "prompt": prompt_text,
                    "genre": genre,
                    "tone": tone,
                    "provider": provider,
                    "generated_at": result.generated_at,
                    "word_count": result.word_count,
                    "result": result,
                    "req": req,
                    "images": images
                })

            except requests.exceptions.HTTPError as e:
                st.error(f"API error: {e}. Check your API key and usage limits.")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    if generate_clicked and prompt.strip():
        run_generation(prompt)
    elif regen_clicked and st.session_state.req:
        run_generation(st.session_state.req.prompt)

    # ── Display results ──
    if st.session_state.result:
        result: StoryResult = st.session_state.result
        req: StoryRequest   = st.session_state.req
        images              = st.session_state.images

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Story rating
        st.markdown("**Rate this story:**")
        rating_cols = st.columns(6)
        for i, col in enumerate(rating_cols[:5], 1):
            with col:
                star = "⭐" if (st.session_state.rating and i <= st.session_state.rating) else "☆"
                if st.button(f"{star} {i}", key=f"rate_{i}"):
                    st.session_state.rating = i
                    st.rerun()
        if st.session_state.rating:
            st.markdown(f"<div style='font-size:0.82rem;color:#7c5cbf;margin-top:0.3rem;'>Rated {st.session_state.rating}/5 ⭐</div>", unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        tab_story, tab_scenes, tab_export = st.tabs(["📖  Full Story", "🎬  Scenes & Images", "📥  Export"])

        with tab_story:
            provider_badge_sm = f'<span class="provider-badge-groq">Groq</span>' if result.provider == "groq" else f'<span class="provider-badge-openai">OpenAI</span>'
            st.markdown(f'<div class="story-title">{result.title}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-bottom:1.5rem;'>
                {provider_badge_sm}
                <span class="genre-badge">{GENRE_DETAILS[req.genre]['emoji']} {req.genre.capitalize()}</span>
                <span class="genre-badge">🎭 {req.tone.capitalize()}</span>
                <span style='font-size:0.75rem;color:#4a4760;'>Generated {result.generated_at}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="character-card">
                <strong>Character card</strong><br>{result.character_card}<br><br>
                <strong>Soundtrack mood</strong><br>{result.soundtrack_mood}
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.reading_mode:
                st.markdown(f'<div class="reading-mode">{result.story}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="story-card"><div class="story-body">{result.story}</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="word-count">Word count: {result.word_count}</div>', unsafe_allow_html=True)

        with tab_scenes:
            st.markdown(f"<div style='color:#4a4760;font-size:0.82rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.5rem;'>{len(result.scenes)} scenes generated</div>", unsafe_allow_html=True)
            for scene in result.scenes:
                img_col, text_col = st.columns([5, 4])
                with img_col:
                    img = images.get(scene.scene_number)
                    if img:
                        query = build_image_query(scene, req)
                        st.image(img, use_container_width=True, caption=f"Matched to: {query}")
                        st.download_button(
                            label="⬇ Download image",
                            data=pil_to_bytes(img),
                            file_name=f"scene_{scene.scene_number}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"dl_img_{scene.scene_number}"
                        )
                with text_col:
                    st.markdown(f"""
                    <div class="scene-card">
                        <div class="scene-number">Scene {scene.scene_number}</div>
                        <div class="scene-title">{scene.title}</div>
                        <div class="scene-desc">{scene.description}</div>
                        <div class="image-prompt-box">🎨 <strong>Image prompt:</strong><br>{scene.image_prompt}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("")

        with tab_export:
            export_text = f"STORY FORGE\n{'='*60}\nTitle: {result.title}\nGenre: {req.genre} | Tone: {req.tone}\n"
            export_text += f"Protagonist: {req.character_name} | Setting: {req.setting}\n"
            export_text += f"Provider: {result.provider} | Model: {req.model} | Generated: {result.generated_at}\n"
            export_text += f"Narrator: {req.narrator_style} | Plot twist: {req.plot_twist}\n"
            export_text += f"Words: {result.word_count}\n\nCHARACTER CARD\n{'-'*60}\n{result.character_card}\n\nSOUNDTRACK MOOD\n{'-'*60}\n{result.soundtrack_mood}\n\nSTORY\n{'-'*60}\n{result.story}\n\nSCENES\n{'-'*60}\n"
            for s in result.scenes:
                export_text += f"\nScene {s.scene_number}: {s.title}\n{s.description}\nImage Prompt: {s.image_prompt}\n"

            st.download_button("📄  Download story (.txt)", data=export_text,
                file_name=f"{result.title.replace(' ','_')}.txt", mime="text/plain")

            markdown_text = f"# {result.title}\n\n**Genre:** {req.genre}  \n**Tone:** {req.tone}  \n**Provider:** {result.provider}  \n**Model:** {req.model}  \n**Generated:** {result.generated_at}\n\n## Character Card\n{result.character_card}\n\n## Soundtrack Mood\n{result.soundtrack_mood}\n\n## Story\n{result.story}\n\n## Scenes\n"
            for s in result.scenes:
                markdown_text += f"\n### Scene {s.scene_number}: {s.title}\n{s.description}\n\n**Image prompt:** {s.image_prompt}\n"
            st.download_button("📝  Download story (.md)", data=markdown_text,
                file_name=f"{result.title.replace(' ','_')}.md", mime="text/markdown")

            st.markdown("#### Scene image prompts")
            st.markdown("<div style='font-size:0.82rem;color:#5e5a75;margin-bottom:1rem;'>Paste into Stable Diffusion, Midjourney or DALL·E for real AI images.</div>", unsafe_allow_html=True)
            for s in result.scenes:
                with st.expander(f"Scene {s.scene_number}: {s.title}"):
                    st.code(s.image_prompt, language=None)


# ─────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────
elif st.session_state.page == "history":
    st.markdown('<div class="hero-title" style="font-size:2.4rem;">Story History</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Every story generated this session</div>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("<div style='color:#4a4760;font-size:1rem;'>No stories generated yet. Head to Generate to create your first story.</div>", unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            badge = f'<span class="provider-badge-groq">Groq</span>' if item["provider"] == "groq" else f'<span class="provider-badge-openai">OpenAI</span>'
            st.markdown(f"""
            <div class="history-card">
                <div class="history-title">{item['title']}</div>
                <div style='margin:0.3rem 0;'>{badge}
                    <span class="genre-badge">{GENRE_DETAILS[item['genre']]['emoji']} {item['genre'].capitalize()}</span>
                </div>
                <div class="history-meta">"{item['prompt'][:80]}{'…' if len(item['prompt'])>80 else ''}"</div>
                <div class="history-meta" style='margin-top:0.3rem;'>{item['word_count']} words · {item['generated_at']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Load this story", key=f"load_{i}"):
                st.session_state.result = item["result"]
                st.session_state.req    = item["req"]
                st.session_state.images = item["images"]
                st.session_state.page   = "generate"
                st.rerun()


# ─────────────────────────────────────────────
# PAGE: STATS
# ─────────────────────────────────────────────
elif st.session_state.page == "stats":
    st.markdown('<div class="hero-title" style="font-size:2.4rem;">Session Stats</div>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    history = st.session_state.history
    total = len(history)
    total_words = sum(h["word_count"] for h in history)
    groq_count  = sum(1 for h in history if h["provider"] == "groq")
    openai_count = total - groq_count
    genres_used = list(set(h["genre"] for h in history))

    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, total, "Stories generated"),
        (s2, total_words, "Total words written"),
        (s3, groq_count, "Via Groq"),
        (s4, openai_count, "Via OpenAI"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-num">{num}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    if history:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("#### Genres explored")
        st.markdown(" ".join([f'<span class="genre-badge">{GENRE_DETAILS[g]["emoji"]} {g.capitalize()}</span>' for g in genres_used]), unsafe_allow_html=True)

        st.markdown("#### Most recent story")
        last = history[-1]
        st.markdown(f"**{last['title']}** — _{last['prompt'][:100]}_")
