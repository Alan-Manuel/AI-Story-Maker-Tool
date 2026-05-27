"""
AI Story Maker — Story Forge Kaggle Edition
- No Groq
- No OpenAI
- Story generation through a Kaggle Gradio endpoint
- Prompt-based scene images through Pollinations AI
- Story history, regenerate, reading mode, rating, character card, soundtrack mood, Markdown export

Run with:
    streamlit run story_maker_app.py
"""

import streamlit as st
import requests
import textwrap
import io
import urllib.parse
import time
from datetime import datetime
from PIL import Image, ImageDraw
from pydantic import BaseModel
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from gradio_client import Client
import random


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Story Forge — Kaggle AI Story Maker",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e0e12;
    color: #e8e4dc;
}
.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, #241336 0%, transparent 38%),
        radial-gradient(ellipse at 85% 20%, #112a3a 0%, transparent 28%),
        linear-gradient(135deg, #0e0e12 0%, #13111c 100%);
}
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(19,18,26,0.96) !important;
    border-right: 1px solid #2a2535;
}
[data-testid="stSidebar"] * { color: #c8c4bc !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label {
    font-size: 0.78rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8f86a8 !important;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 4.2rem;
    font-weight: 700;
    line-height: 1.05;
    color: #f7f1e8;
    letter-spacing: -0.03em;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: #b3a4c5;
    margin-bottom: 2rem;
}
.story-card {
    background: linear-gradient(135deg, rgba(23,21,31,0.95) 0%, rgba(28,24,40,0.95) 100%);
    border: 1px solid #332d45;
    border-radius: 18px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 18px 55px rgba(0,0,0,0.25);
}
.scene-card {
    background: rgba(19,18,26,0.96);
    border-left: 3px solid #9b7de0;
    border-radius: 0 14px 14px 0;
    padding: 1.5rem;
    margin: 1.2rem 0;
}
.scene-number {
    font-family: 'Playfair Display', serif;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #9b7de0;
    margin-bottom: 0.3rem;
}
.scene-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f0ebe0;
    margin-bottom: 0.8rem;
}
.scene-desc {
    font-size: 0.95rem;
    color: #aaa3bb;
    line-height: 1.7;
    margin-bottom: 1rem;
}
.image-prompt-box {
    background: #0e0e12;
    border: 1px dashed #4a4161;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.78rem;
    color: #817995;
    font-style: italic;
}
.story-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #f7f1e8;
    margin-bottom: 0.5rem;
}
.story-body {
    font-size: 1rem;
    color: #d2cdc3;
    line-height: 1.95;
    white-space: pre-line;
}
.reading-mode {
    font-family: 'Playfair Display', serif;
    font-size: 1.18rem;
    color: #eee7dd;
    line-height: 2.15;
    white-space: pre-line;
    max-width: 720px;
    margin: 0 auto;
}
.word-count {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5d5771;
    margin-top: 1rem;
}
.genre-badge {
    display: inline-block;
    background: #2a1f42;
    color: #bba3ff;
    border: 1px solid #48356d;
    border-radius: 999px;
    padding: 0.25rem 0.8rem;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-right: 0.5rem;
    margin-bottom: 1rem;
}
.step-box {
    background: rgba(23,21,31,0.9);
    border: 1px solid #302a42;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    display:flex;
    gap:1rem;
    align-items:flex-start;
}
.section-divider {
    border: none;
    border-top: 1px solid #2a2535;
    margin: 2rem 0;
}
.history-card {
    background: rgba(23,21,31,0.95);
    border: 1px solid #2e2a3d;
    border-radius: 14px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.8rem;
}
.history-title {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #f0ebe0;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.history-meta {
    font-size: 0.75rem;
    color: #6f6880;
    letter-spacing: 0.05em;
}
.provider-badge-kaggle {
    background: #10233f;
    color: #73a7ff;
    border: 1px solid #244a85;
    border-radius: 999px;
    padding: 0.25rem 0.8rem;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-right: 0.4rem;
}
.stat-box {
    background: rgba(23,21,31,0.95);
    border: 1px solid #2e2a3d;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #9b7de0;
    line-height: 1;
}
.stat-label {
    font-size: 0.72rem;
    color: #6f6880;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
}
.character-card {
    background:#111018;
    border:1px solid #2e2a3d;
    border-radius:14px;
    padding:1rem 1.2rem;
    margin:1rem 0;
    color:#aaa3bb;
    line-height:1.7;
}
.stButton > button {
    background: linear-gradient(135deg, #6d48bb 0%, #9b7de0 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 1.8rem !important;
    font-size: 0.92rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px);
}
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #2a2535;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6f6880 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    padding: 0.7rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: #c8a8f0 !important;
    border-bottom: 2px solid #9b7de0 !important;
}
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
    narrator_style: str = "cinematic"
    plot_twist: bool = True
    art_style: str = "cinematic concept art"


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
    provider: str = "kaggle-gradio"
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
    "dramatic": "dramatic",
    "dark": "dark and ominous",
    "lighthearted": "lighthearted and warm",
    "humorous": "humorous and witty",
    "emotional": "deeply emotional",
    "action-packed": "fast-paced and action-packed",
}

NARRATOR_STYLES = {
    "cinematic": "cinematic and visually rich",
    "first-person": "first-person, intimate, and reflective",
    "storybook": "storybook-like, warm, and imaginative",
    "noir": "noir-inspired, moody, and sharp",
    "young-adult": "young-adult style, clear, emotional, and fast-moving",
}

ART_STYLES = [
    "cinematic concept art",
    "storybook illustration",
    "dark fantasy digital painting",
    "watercolor illustration",
    "noir film still",
    "anime-inspired key visual",
    "retro sci-fi poster",
]


# ─────────────────────────────────────────────
# KAGGLE / GRADIO STORY GENERATION
# ─────────────────────────────────────────────
def normalize_gradio_url(url: str) -> str:
    return url.strip().rstrip("/")


def call_kaggle_gradio_endpoint(
    gradio_url: str,
    req: StoryRequest,
) -> Dict[str, Any]:
    """
    Calls the Kaggle Gradio endpoint created in the notebook.

    IMPORTANT:
    The Kaggle notebook uses btn.click(..., api_name="generate_story"),
    so the Streamlit app must call api_name="/generate_story" through
    gradio_client. Calling /api/predict directly can produce a 404.
    """
    url = normalize_gradio_url(gradio_url)

    try:
        client = Client(url)

        data = client.predict(
            req.prompt,
            req.genre,
            req.tone,
            req.character_name,
            req.setting,
            req.num_scenes,
            req.narrator_style,
            req.plot_twist,
            req.art_style,
            api_name="/generate_story",
        )
    except Exception as e:
        raise RuntimeError(
            "Could not call the Kaggle Gradio endpoint. Make sure the Kaggle notebook "
            "is still running, use the public https://xxxxx.gradio.live URL, and confirm "
            "the notebook endpoint uses api_name='generate_story'. Original error: "
            f"{e}"
        )

    # Gradio can return either a dict directly or a JSON string.
    if isinstance(data, str):
        import json
        data = json.loads(data)

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected response from Kaggle Gradio endpoint: {type(data)}")

    return data


def make_unique_title(raw_title: str, req: StoryRequest) -> str:
    """
    Prevent repetitive or generic story titles from the Kaggle model.
    If the model returns a repeated title like "The Hidden Path of Adrian",
    the app replaces it with a genre-aware cinematic title.
    """
    generic_titles = [
        "",
        "Untitled Story",
        "The Hidden Path",
        f"The Hidden Path of {req.character_name}",
    ]

    title_pool = {
        "romance": [
            "Letters Beneath the Moonlight",
            "The Violinist at Midnight",
            "A Promise Beyond the Sea",
            "When the Clock Tower Sang",
            "The Last Letter Before Sunrise",
            "Beneath the Lantern Sky",
        ],
        "sci-fi": [
            "Echoes Beneath the Flood",
            "Signal From the Drowned World",
            "Fragments of Tomorrow",
            "The Last Orbit",
            "The Machine That Remembered",
        ],
        "mystery": [
            "The Vanishing Hour",
            "Whispers in Hollow Street",
            "The Door No One Opened",
            "Beneath the Fog",
        ],
        "fantasy": [
            "The Moonlit Crown",
            "The Sleeping Forest",
            "Ashes of the Forgotten Realm",
            "The Kingdom Beyond the Gate",
        ],
        "thriller": [
            "Shadow Protocol",
            "The Final Pursuit",
            "Before the Signal Ends",
            "The Midnight Chase",
        ],
        "adventure": [
            "Beyond the Crimson Horizon",
            "The Lost Expedition",
            "Into the Forgotten Wilds",
            "The Path Across Storm Seas",
        ],
        "horror": [
            "The Hollow Below",
            "The Last Candle",
            "The House Beneath the Lake",
            "When the Walls Whispered",
        ],
    }

    cleaned = str(raw_title).strip()

    if cleaned and cleaned not in generic_titles and "Hidden Path" not in cleaned and len(cleaned) > 6:
        return cleaned

    options = title_pool.get(
        req.genre,
        [
            f"The Secret of {req.character_name}",
            "A Story Beneath the Storm",
            f"The Last Light of {req.setting.title()}",
        ],
    )

    return random.choice(options)


def parse_story_data(data: Dict[str, Any], req: StoryRequest) -> StoryResult:
    scenes = []

    raw_scenes = data.get("scenes", [])
    if not isinstance(raw_scenes, list):
        raw_scenes = []

    for i, scene in enumerate(raw_scenes[:req.num_scenes], start=1):
        scenes.append(Scene(
            scene_number=int(scene.get("scene_number", i)),
            title=str(scene.get("title", f"Scene {i}")),
            description=str(scene.get("description", "Scene description unavailable.")),
            image_prompt=str(scene.get(
                "image_prompt",
                f"{req.art_style}, "
                f"{req.genre} scene, "
                f"{req.character_name} in {req.setting}, "
                f"inspired by: {req.prompt}, "
                f"{req.tone} mood, "
                f"cinematic lighting, highly detailed, dramatic composition, volumetric lighting"
            )),
        ))

    if not scenes:
        for i in range(1, req.num_scenes + 1):
            scenes.append(Scene(
                scene_number=i,
                title=f"Scene {i}",
                description=f"{req.character_name} moves through {req.setting}, following the conflict from the prompt.",
                image_prompt=(
                    f"{req.art_style}, "
                    f"{req.genre} cinematic scene, "
                    f"{req.character_name} in {req.setting}, "
                    f"inspired by: {req.prompt}, "
                    f"{req.tone} atmosphere, "
                    f"high detail, dramatic composition, movie still, volumetric lighting"
                ),
            ))

    story = str(data.get("story", "Story text unavailable. Try regenerating."))

    return StoryResult(
        title=make_unique_title(
            data.get("title", ""),
            req,
        ),
        story=story,
        scenes=scenes,
        word_count=len(story.split()),
        provider="kaggle-gradio",
        generated_at=datetime.now().strftime("%d %b %Y, %H:%M"),
        character_card=str(data.get(
            "character_card",
            f"{req.character_name} is the central character, shaped by the setting and conflict."
        )),
        soundtrack_mood=str(data.get(
            "soundtrack_mood",
            f"{req.tone}, {req.genre}, cinematic atmosphere"
        )),
    )


def generate_story_kaggle(req: StoryRequest, gradio_url: str) -> StoryResult:
    data = call_kaggle_gradio_endpoint(gradio_url, req)
    return parse_story_data(data, req)


# ─────────────────────────────────────────────
# IMAGE GENERATION
# ─────────────────────────────────────────────
GENRE_PALETTES = {
    "mystery":   [(20, 25, 40), (60, 80, 120), (180, 160, 200)],
    "fantasy":   [(25, 15, 40), (100, 60, 160), (220, 180, 255)],
    "sci-fi":    [(10, 25, 30), (30, 130, 120), (100, 220, 200)],
    "thriller":  [(25, 15, 10), (140, 60, 30), (220, 140, 80)],
    "adventure": [(15, 25, 10), (60, 110, 40), (180, 220, 100)],
    "romance":   [(40, 15, 25), (160, 60, 100), (220, 160, 180)],
    "horror":    [(15, 10, 10), (80, 30, 30), (160, 80, 80)],
}


def build_pollinations_url(prompt: str, width: int = 768, height: int = 432, seed: int = 42) -> str:
    encoded_prompt = urllib.parse.quote(prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&enhance=true"
    )


def generate_image_from_prompt(
    prompt: str,
    seed: int = 42,
    retries: int = 3
) -> Optional[Image.Image]:
    """
    Generate an image from a scene image prompt using Pollinations AI.
    Uses smaller image size + retries to reduce failures for multiple scenes.
    """
    for attempt in range(retries):
        try:
            url = build_pollinations_url(
                prompt,
                width=768,
                height=432,
                seed=seed + attempt
            )

            resp = requests.get(
                url,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "image" not in content_type:
                time.sleep(2)
                continue

            return Image.open(io.BytesIO(resp.content)).convert("RGB")

        except Exception:
            time.sleep(3)

    return None


def create_fallback_image(scene: Scene, genre: str, setting: str) -> Image.Image:
    """Fallback image if the image endpoint is unavailable."""
    W, H = 1024, 576
    palette = GENRE_PALETTES.get(genre, GENRE_PALETTES["mystery"])
    bg, mid, fg = palette
    img = Image.new("RGB", (W, H), color=bg)
    draw = ImageDraw.Draw(img)

    for y in range(H):
        r = int(bg[0] + (mid[0] - bg[0]) * y / H)
        g = int(bg[1] + (mid[1] - bg[1]) * y / H)
        b = int(bg[2] + (mid[2] - bg[2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    for i in range(12):
        x = 80 + i * 80
        draw.ellipse([x, 80, x + 180, 260], outline=fg, width=2)

    draw.rectangle([0, 0, 8, H], fill=fg)

    title = f"Scene {scene.scene_number}: {scene.title}"
    for i, line in enumerate(textwrap.wrap(title, width=42)):
        draw.text((36, 44 + i * 30), line, fill=fg)

    for i, line in enumerate(textwrap.wrap(setting, width=54)[:3]):
        draw.text((36, H - 110 + i * 26), line, fill=fg)

    draw.text((W - 260, H - 32), "[ fallback image ]", fill=(90, 90, 105))
    return img


def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def safe_filename(text: str) -> str:
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch in (" ", "_", "-")).strip()
    return cleaned.replace(" ", "_")[:80] or "story"


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "result": None,
    "req": None,
    "page": "home",
    "images": {},
    "history": [],
    "reading_mode": False,
    "rating": None,
    "regenerate_count": 0,
    "last_prompt": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 Story Forge")
    st.markdown(
        "<div style='font-size:0.78rem;color:#6f6880;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>Kaggle Story Endpoint</div>",
        unsafe_allow_html=True,
    )

    gradio_url = st.text_input(
        "Kaggle Gradio URL",
        placeholder="https://xxxxx.gradio.live",
        help="Paste the public gradio.live URL from your Kaggle notebook.",
    )

    st.markdown("<div style='font-size:0.75rem;color:#73a7ff;margin-top:0.3rem;'>✓ Kaggle + Hugging Face endpoint — no Groq/OpenAI</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem;color:#6f6880;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>Story Settings</div>",
        unsafe_allow_html=True,
    )

    genre = st.selectbox(
        "Genre",
        options=list(GENRE_DETAILS.keys()),
        format_func=lambda g: f"{GENRE_DETAILS[g]['emoji']}  {g.capitalize()}",
    )
    tone = st.selectbox(
        "Tone",
        options=list(TONE_WORDS.keys()),
        format_func=lambda t: t.capitalize(),
    )
    num_scenes = st.slider("Scenes", min_value=2, max_value=5, value=3)
    story_length = st.slider("Word count", min_value=150, max_value=700, value=400, step=50)
    narrator_style = st.selectbox(
        "Narrator style",
        options=list(NARRATOR_STYLES.keys()),
        format_func=lambda n: n.replace("-", " ").title(),
    )
    plot_twist = st.toggle("Add plot twist ending", value=True)
    art_style = st.selectbox("Image style", options=ART_STYLES)

    st.markdown("---")
    character_name = st.text_input("Protagonist", value="Elara")
    setting = st.text_input("Setting", value="a rain-soaked old city")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem;color:#6f6880;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.8rem;'>Navigate</div>",
        unsafe_allow_html=True,
    )

    for label, pg in [
        ("🏠  Home", "home"),
        ("✍️  Generate", "generate"),
        ("📚  History", "history"),
        ("📊  Stats", "stats"),
    ]:
        if st.button(label, use_container_width=True):
            st.session_state.page = pg
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown('<div class="hero-title">Story Forge</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Kaggle-powered stories with prompt-based AI scene images</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:1rem;color:#b3a4c5;line-height:1.8;max-width:800px;margin-bottom:2rem;'>
    Story Forge turns a single prompt into a structured short story with scenes, character notes,
    soundtrack mood, and matching generated images. This version removes Groq and OpenAI, then uses
    a <strong style='color:#73a7ff;'>Kaggle Gradio endpoint</strong> for story generation and
    Pollinations AI for scene visuals.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What you get")
    fc1, fc2, fc3 = st.columns(3)
    fc4, fc5, fc6 = st.columns(3)

    for col, icon, title, desc in [
        (fc1, "🧪", "Kaggle experiment pipeline", "Run a small Hugging Face model in Kaggle and expose it through Gradio."),
        (fc2, "🖼️", "Working image generation", "Each scene image prompt is sent to Pollinations AI to create matching visuals."),
        (fc3, "🎭", "Narrator styles", "Choose cinematic, first-person, storybook, noir, or young-adult narration."),
        (fc4, "🌀", "Plot twist mode", "Optionally add an earned twist ending to make stories more memorable."),
        (fc5, "🎬", "Scene breakdown", "Every story is split into vivid scenes with descriptions and image prompts."),
        (fc6, "📥", "Markdown export", "Download the story in TXT or Markdown format for a portfolio or report."),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box" style='text-align:left;padding:1.2rem;margin-bottom:1rem;'>
                <div style='font-size:1.6rem;margin-bottom:0.5rem;'>{icon}</div>
                <div style='font-family:"Playfair Display",serif;font-size:0.95rem;color:#f0ebe0;font-weight:700;margin-bottom:0.3rem;'>{title}</div>
                <div style='font-size:0.78rem;color:#817995;line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("### How it works")
    for num, title, desc in [
        ("1", "Run the Kaggle notebook", "Start the Hugging Face + Gradio notebook in Kaggle and copy the public gradio.live URL."),
        ("2", "Paste the endpoint URL", "Paste the URL into the Streamlit sidebar under Kaggle Gradio URL."),
        ("3", "Configure the story", "Choose genre, tone, scene count, narrator style, image style, protagonist, and setting."),
        ("4", "Generate story and images", "The app calls Kaggle for structured story JSON, then creates images from each scene prompt."),
        ("5", "Save and export", "Review scenes, download images, export TXT/Markdown, and revisit stories in the History tab."),
    ]:
        st.markdown(f"""
        <div class="step-box">
            <div style='font-family:"Playfair Display",serif;font-size:1.8rem;font-weight:700;color:#9b7de0;min-width:2.2rem;line-height:1;'>{num}</div>
            <div>
                <div style='font-family:"Playfair Display",serif;font-size:1rem;color:#f0ebe0;margin-bottom:0.3rem;font-weight:700;'>{title}</div>
                <div style='font-size:0.88rem;color:#8f86a8;line-height:1.6;'>{desc}</div>
            </div>
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

    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <span class="provider-badge-kaggle">🧪 Kaggle</span>
        <span class="genre-badge">{GENRE_DETAILS[genre]['emoji']} {genre.capitalize()}</span>
        <span class="genre-badge">🎭 {tone.capitalize()}</span>
        <span class="genre-badge">🎬 {num_scenes} scenes</span>
        <span class="genre-badge">🖼️ {art_style}</span>
    </div>
    """, unsafe_allow_html=True)

    prompt = st.text_area(
        "Your story prompt",
        value=st.session_state.last_prompt,
        placeholder="e.g. Max, in a crowded city alleyway, stumbles upon a glowing magical gate that wasn't there yesterday…",
        height=120,
        help="The more specific your prompt, the more unique your story and generated images will be.",
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
        regen_clicked = st.button("🔄  Regenerate", use_container_width=True, disabled=st.session_state.result is None)
    with col3:
        reading_mode = st.toggle("📖 Reading mode", value=st.session_state.reading_mode)
        st.session_state.reading_mode = reading_mode

    def run_generation(prompt_text: str):
        if not gradio_url.strip():
            st.error("Please paste your Kaggle Gradio URL in the sidebar.")
            return
        if not prompt_text.strip():
            st.warning("Please enter a story prompt.")
            return

        with st.spinner("Writing your story through the Kaggle Gradio endpoint…"):
            try:
                req = StoryRequest(
                    prompt=prompt_text,
                    genre=genre,
                    tone=tone,
                    num_scenes=num_scenes,
                    length=story_length,
                    character_name=character_name,
                    setting=setting,
                    narrator_style=narrator_style,
                    plot_twist=plot_twist,
                    art_style=art_style,
                )

                result = generate_story_kaggle(req, gradio_url)

                st.session_state.result = result
                st.session_state.req = req
                st.session_state.rating = None
                st.session_state.regenerate_count += 1
                st.session_state.last_prompt = prompt_text

                images = {}
                with st.spinner("Generating matching scene images…"):
                    for scene in result.scenes:
                        image_prompt = (
                            f"{art_style}. "
                            f"{genre} {tone} scene. "
                            f"Scene {scene.scene_number}: {scene.title}. "
                            f"{scene.description[:250]}. "
                            f"Main idea: {prompt_text[:180]}. "
                            f"Character: {character_name}. "
                            f"Setting: {setting}. "
                            f"Cinematic lighting, high detail, no text, no watermark."
                        )

                        unique_seed = abs(
                            hash(
                                f"{prompt_text}-{scene.scene_number}-{scene.title}-{scene.description}"
                            )
                        ) % 100000

                        img = generate_image_from_prompt(
                            image_prompt,
                            seed=unique_seed
                        )

                        # Longer delay helps avoid rapid-fire image endpoint failures/rate limits.
                        time.sleep(4)

                        if img:
                            images[scene.scene_number] = img
                        else:
                            st.warning(
                                f"Scene {scene.scene_number} image generation failed — using fallback image."
                            )
                            images[scene.scene_number] = create_fallback_image(
                                scene,
                                req.genre,
                                req.setting
                            )

                st.session_state.images = images

                st.session_state.history.append({
                    "title": result.title,
                    "prompt": prompt_text,
                    "genre": genre,
                    "tone": tone,
                    "provider": "kaggle-gradio",
                    "generated_at": result.generated_at,
                    "word_count": result.word_count,
                    "result": result,
                    "req": req,
                    "images": images,
                })

            except requests.exceptions.HTTPError as e:
                st.error(f"Kaggle Gradio endpoint error: {e}. Check that your Kaggle notebook is still running and the URL is correct.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    if generate_clicked and prompt.strip():
        run_generation(prompt)
    elif regen_clicked and st.session_state.req:
        run_generation(st.session_state.req.prompt)

    if st.session_state.result:
        result: StoryResult = st.session_state.result
        req: StoryRequest = st.session_state.req
        images = st.session_state.images

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        st.markdown("**Rate this story:**")
        rating_cols = st.columns(6)
        for i, col in enumerate(rating_cols[:5], 1):
            with col:
                star = "⭐" if (st.session_state.rating and i <= st.session_state.rating) else "☆"
                if st.button(f"{star} {i}", key=f"rate_{i}"):
                    st.session_state.rating = i
                    st.rerun()
        if st.session_state.rating:
            st.markdown(f"<div style='font-size:0.82rem;color:#9b7de0;margin-top:0.3rem;'>Rated {st.session_state.rating}/5 ⭐</div>", unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        tab_story, tab_scenes, tab_export = st.tabs(["📖  Full Story", "🎬  Scenes & Images", "📥  Export"])

        with tab_story:
            st.markdown(f'<div class="story-title">{result.title}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-bottom:1.5rem;'>
                <span class="provider-badge-kaggle">Kaggle</span>
                <span class="genre-badge">{GENRE_DETAILS[req.genre]['emoji']} {req.genre.capitalize()}</span>
                <span class="genre-badge">🎭 {req.tone.capitalize()}</span>
                <span style='font-size:0.75rem;color:#6f6880;'>Generated {result.generated_at}</span>
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
            st.markdown(f"<div style='color:#6f6880;font-size:0.82rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.5rem;'>{len(result.scenes)} scenes generated</div>", unsafe_allow_html=True)

            for scene in result.scenes:
                img_col, text_col = st.columns([5, 4])
                with img_col:
                    img = images.get(scene.scene_number)
                    if img:
                        st.image(img, use_container_width=True, caption="Generated from scene prompt")
                        st.download_button(
                            label="⬇ Download image",
                            data=pil_to_bytes(img),
                            file_name=f"scene_{scene.scene_number}_{safe_filename(scene.title)}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"dl_img_{scene.scene_number}",
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
            export_text += f"Provider: Kaggle Gradio | Generated: {result.generated_at}\n"
            export_text += f"Narrator: {req.narrator_style} | Plot twist: {req.plot_twist} | Image style: {req.art_style}\n"
            export_text += f"Words: {result.word_count}\n\nCHARACTER CARD\n{'-'*60}\n{result.character_card}\n\nSOUNDTRACK MOOD\n{'-'*60}\n{result.soundtrack_mood}\n\nSTORY\n{'-'*60}\n{result.story}\n\nSCENES\n{'-'*60}\n"

            for s in result.scenes:
                export_text += f"\nScene {s.scene_number}: {s.title}\n{s.description}\nImage Prompt: {s.image_prompt}\n"

            st.download_button(
                "📄  Download story (.txt)",
                data=export_text,
                file_name=f"{safe_filename(result.title)}.txt",
                mime="text/plain",
            )

            markdown_text = f"# {result.title}\n\n**Genre:** {req.genre}  \n**Tone:** {req.tone}  \n**Provider:** Kaggle Gradio  \n**Generated:** {result.generated_at}  \n**Image Style:** {req.art_style}\n\n## Character Card\n{result.character_card}\n\n## Soundtrack Mood\n{result.soundtrack_mood}\n\n## Story\n{result.story}\n\n## Scenes\n"

            for s in result.scenes:
                markdown_text += f"\n### Scene {s.scene_number}: {s.title}\n{s.description}\n\n**Image prompt:** {s.image_prompt}\n"

            st.download_button(
                "📝  Download story (.md)",
                data=markdown_text,
                file_name=f"{safe_filename(result.title)}.md",
                mime="text/markdown",
            )

            st.markdown("#### Scene image prompts")
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
        st.markdown("<div style='color:#6f6880;font-size:1rem;'>No stories generated yet. Head to Generate to create your first story.</div>", unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div class="history-card">
                <div class="history-title">{item['title']}</div>
                <div style='margin:0.3rem 0;'>
                    <span class="provider-badge-kaggle">Kaggle</span>
                    <span class="genre-badge">{GENRE_DETAILS[item['genre']]['emoji']} {item['genre'].capitalize()}</span>
                </div>
                <div class="history-meta">"{item['prompt'][:80]}{'…' if len(item['prompt']) > 80 else ''}"</div>
                <div class="history-meta" style='margin-top:0.3rem;'>{item['word_count']} words · {item['generated_at']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Load this story", key=f"load_{i}"):
                st.session_state.result = item["result"]
                st.session_state.req = item["req"]
                st.session_state.images = item["images"]
                st.session_state.page = "generate"
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
    genres_used = list(set(h["genre"] for h in history))

    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, total, "Stories generated"),
        (s2, total_words, "Total words written"),
        (s3, total, "Via Kaggle"),
        (s4, st.session_state.regenerate_count, "Generations"),
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
        st.markdown(
            " ".join([
                f'<span class="genre-badge">{GENRE_DETAILS[g]["emoji"]} {g.capitalize()}</span>'
                for g in genres_used
            ]),
            unsafe_allow_html=True,
        )

        st.markdown("#### Most recent story")
        last = history[-1]
        st.markdown(f"**{last['title']}** — _{last['prompt'][:100]}_")
