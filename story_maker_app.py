"""
AI Story Maker — Streamlit Frontend
Connects to the existing backend logic (StoryRequest, generate_mock_story, Scene, StoryResult)
Run with: streamlit run story_maker_app.py
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
from dataclasses import dataclass
from typing import List
import random
import textwrap
import io

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
# CUSTOM CSS — Dark editorial aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e0e12;
    color: #e8e4dc;
}

/* Main background */
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a1025 0%, #0e0e12 60%);
}

/* Hide default Streamlit header */
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #13121a !important;
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
    color: #7a7590 !important;
}

/* Hero title */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1.1;
    color: #f0ebe0;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: #9b8fa8;
    margin-bottom: 2rem;
}

/* Cards */
.story-card {
    background: linear-gradient(135deg, #17151f 0%, #1c1828 100%);
    border: 1px solid #2e2a3d;
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
}
.scene-card {
    background: #13121a;
    border-left: 3px solid #7c5cbf;
    border-radius: 0 8px 8px 0;
    padding: 1.5rem;
    margin: 1.2rem 0;
}
.scene-number {
    font-family: 'Playfair Display', serif;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7c5cbf;
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
    color: #a09cb0;
    line-height: 1.7;
    margin-bottom: 1rem;
}
.image-prompt-box {
    background: #0e0e12;
    border: 1px dashed #3d3850;
    border-radius: 6px;
    padding: 0.7rem 1rem;
    font-size: 0.78rem;
    color: #5e5a75;
    font-style: italic;
}

/* Story text */
.story-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0ebe0;
    margin-bottom: 0.5rem;
}
.story-body {
    font-size: 1rem;
    color: #c8c4bc;
    line-height: 1.9;
    white-space: pre-line;
}
.word-count {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4a4760;
    margin-top: 1rem;
}

/* Genre badge */
.genre-badge {
    display: inline-block;
    background: #2a1f42;
    color: #9b7de0;
    border: 1px solid #3d2f5e;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-right: 0.5rem;
    margin-bottom: 1rem;
}

/* Instruction steps */
.step-box {
    background: #17151f;
    border: 1px solid #2e2a3d;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
}
.step-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #7c5cbf;
    min-width: 2rem;
    line-height: 1;
}
.step-content h4 {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #f0ebe0;
    margin: 0 0 0.3rem 0;
}
.step-content p {
    font-size: 0.88rem;
    color: #7a7590;
    margin: 0;
    line-height: 1.5;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #2a2535;
    margin: 2rem 0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #5c3d9e 0%, #7c5cbf 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.8rem !important;
    font-size: 0.92rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #2a2535;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5e5a75 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    padding: 0.7rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: #c8a8f0 !important;
    border-bottom: 2px solid #7c5cbf !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BACKEND MODELS (from your Colab notebook)
# ─────────────────────────────────────────────
class StoryRequest(BaseModel):
    prompt: str
    genre: str = "mystery"
    tone: str = "suspenseful"
    num_scenes: int = 3
    length: int = 300
    character_name: str = "Elara"
    setting: str = "a rain-soaked old city"

@dataclass
class Scene:
    scene_number: int
    title: str
    description: str
    image_prompt: str

@dataclass
class StoryResult:
    title: str
    story: str
    scenes: List[Scene]
    word_count: int

GENRE_DETAILS = {
    "mystery": {
        "hook": "a hidden clue buried inside something ordinary",
        "conflict": "someone else is searching for the same secret",
        "ending": "the truth is uncovered, but not without consequence",
        "visuals": ["foggy streets", "old documents", "flickering lamps", "shadows", "dusty interiors"],
        "emoji": "🔍", "color": "#4a6fa5"
    },
    "fantasy": {
        "hook": "an ancient force awakens in silence",
        "conflict": "a forgotten power begins reshaping fate",
        "ending": "the hero embraces a destiny larger than expected",
        "visuals": ["glowing ruins", "enchanted forests", "moonlit towers", "ancient symbols", "floating embers"],
        "emoji": "✨", "color": "#7c5cbf"
    },
    "sci-fi": {
        "hook": "a strange signal interrupts normal life",
        "conflict": "technology reveals something deeply unsettling",
        "ending": "the future changes in a single irreversible moment",
        "visuals": ["neon skylines", "control panels", "holograms", "cold metal corridors", "digital maps"],
        "emoji": "🚀", "color": "#3a9e8f"
    },
    "thriller": {
        "hook": "a small discovery turns dangerous almost instantly",
        "conflict": "every move draws the protagonist deeper into risk",
        "ending": "survival depends on one final decision",
        "visuals": ["dark alleyways", "surveillance screens", "storm clouds", "tense closeups", "harsh lighting"],
        "emoji": "⚡", "color": "#b05a3a"
    },
    "adventure": {
        "hook": "a map or message points toward the unknown",
        "conflict": "the journey becomes more dangerous with every step",
        "ending": "the destination reveals something far greater than treasure",
        "visuals": ["mountain passes", "ancient ruins", "winding paths", "sunrise horizons", "weathered maps"],
        "emoji": "🗺️", "color": "#7a9e3a"
    }
}

TONE_WORDS = {
    "suspenseful": ["tense", "uncertain", "shadowed", "quietly dangerous"],
    "dramatic":    ["emotional", "high-stakes", "intense", "powerful"],
    "dark":        ["bleak", "ominous", "haunting", "severe"],
    "lighthearted":["warm", "playful", "charming", "bright"],
    "humorous":    ["quirky", "unexpected", "witty", "offbeat"]
}

SCENE_TITLE_BANK = [
    "The Discovery", "The Warning", "The Pursuit", "The Turning Point",
    "The Hidden Chamber", "The Final Choice", "The Revelation", "The Last Door"
]


# ─────────────────────────────────────────────
# BACKEND LOGIC (from your Colab notebook)
# ─────────────────────────────────────────────
def generate_mock_story(req: StoryRequest) -> StoryResult:
    genre_key = req.genre.lower().strip()
    tone_key  = req.tone.lower().strip()

    genre      = GENRE_DETAILS.get(genre_key, GENRE_DETAILS["mystery"])
    tone_words = TONE_WORDS.get(tone_key,   TONE_WORDS["suspenseful"])

    title_nouns = {
        "mystery": "Canvas", "fantasy": "Crown",
        "sci-fi": "Signal", "thriller": "Cipher", "adventure": "Map"
    }
    title = f"The Hidden {title_nouns.get(genre_key, 'Secret')}"

    intro  = (f'In {req.setting}, {req.character_name} is drawn into {genre["hook"]}. '
              f'What begins with the idea of "{req.prompt}" soon becomes a {random.choice(tone_words)} journey.')
    middle = (f"As the mystery deepens, {genre['conflict']}. "
              f"Each clue sharpens the danger, and every choice begins to matter more than the last.")
    end    = (f"In the end, {genre['ending']}. "
              f"{req.character_name} emerges changed, carrying the weight of what was found.")

    story = f"{intro}\n\n{middle}\n\n{end}"

    scenes, used_titles = [], []
    for i in range(1, req.num_scenes + 1):
        available = [t for t in SCENE_TITLE_BANK if t not in used_titles]
        scene_title = available[0] if available else f"Scene {i}"
        used_titles.append(scene_title)

        if i == 1:
            desc = (f'{req.character_name} first encounters the central mystery connected to "{req.prompt}" '
                    f'in {req.setting}. A subtle clue suggests that something hidden is waiting to be uncovered.')
        elif i == req.num_scenes:
            desc = (f'{req.character_name} reaches the final stage of the journey and confronts the truth directly. '
                    f'The story closes on a {random.choice(tone_words)} note as the central secret is revealed.')
        else:
            desc = (f'{req.character_name} follows the trail deeper and realizes {genre["conflict"]}. '
                    f'The atmosphere grows more {random.choice(tone_words)}, and the stakes become impossible to ignore.')

        visual_bits = random.sample(genre["visuals"], k=min(3, len(genre["visuals"])))
        image_prompt = (f'{req.tone} {req.genre} cinematic scene, {req.setting}, featuring {req.character_name}, '
                        f'{scene_title.lower()}, elements of {", ".join(visual_bits)}, highly detailed, storybook style')

        scenes.append(Scene(scene_number=i, title=scene_title, description=desc, image_prompt=image_prompt))

    return StoryResult(title=title, story=story, scenes=scenes, word_count=len(story.split()))


# ─────────────────────────────────────────────
# IMAGE GENERATION (placeholder — swap for
# StableDiffusionXL when your pipeline is ready)
# ─────────────────────────────────────────────
GENRE_PALETTES = {
    "mystery":   [(20, 25, 40), (60, 80, 120), (180, 160, 200)],
    "fantasy":   [(25, 15, 40), (100, 60, 160), (220, 180, 255)],
    "sci-fi":    [(10, 25, 30), (30, 130, 120), (100, 220, 200)],
    "thriller":  [(25, 15, 10), (140, 60, 30), (220, 140, 80)],
    "adventure": [(15, 25, 10), (60, 110, 40), (180, 220, 100)],
}

def create_scene_image(scene: Scene, genre: str, setting: str) -> Image.Image:
    """
    Generates a styled placeholder image per scene.
    Replace this function body with a StableDiffusionXL call
    when your image pipeline is ready — the interface stays the same.
    """
    W, H = 768, 432
    palette = GENRE_PALETTES.get(genre, GENRE_PALETTES["mystery"])
    bg, mid, fg = palette

    img  = Image.new("RGB", (W, H), color=bg)
    draw = ImageDraw.Draw(img)

    # Gradient bands
    for y in range(H):
        r = int(bg[0] + (mid[0] - bg[0]) * y / H)
        g = int(bg[1] + (mid[1] - bg[1]) * y / H)
        b = int(bg[2] + (mid[2] - bg[2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Decorative circles
    for cx, cy, rad, alpha in [(600, 80, 120, 30), (100, 350, 80, 20), (400, 200, 200, 15)]:
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(*fg, alpha))
        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
        draw = ImageDraw.Draw(img)

    # Scene number strip
    draw.rectangle([0, 0, 6, H], fill=fg)

    # Text overlay — scene title
    title_lines = textwrap.wrap(f"Scene {scene.scene_number}: {scene.title}", width=30)
    y_text = 40
    for line in title_lines:
        draw.text((24, y_text), line, fill=fg)
        y_text += 28

    # Setting label
    setting_short = setting[:50] + "…" if len(setting) > 50 else setting
    draw.text((24, H - 50), setting_short, fill=(fg[0], fg[1], fg[2], 160) if False else fg)

    # "Placeholder" watermark — remove when real images are wired
    draw.text((W - 160, H - 24), "[ placeholder image ]", fill=(80, 80, 90))

    return img


def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "req" not in st.session_state:
    st.session_state.req = None
if "page" not in st.session_state:
    st.session_state.page = "home"


# ─────────────────────────────────────────────
# SIDEBAR — Story Controls
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 Story Forge")
    st.markdown("<div style='font-size:0.78rem;color:#4a4760;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:1.5rem;'>Configure your story</div>", unsafe_allow_html=True)

    genre = st.selectbox(
        "Genre",
        options=list(GENRE_DETAILS.keys()),
        format_func=lambda g: f"{GENRE_DETAILS[g]['emoji']}  {g.capitalize()}"
    )

    tone = st.selectbox(
        "Tone",
        options=list(TONE_WORDS.keys()),
        format_func=lambda t: t.capitalize()
    )

    num_scenes = st.slider("Number of scenes", min_value=2, max_value=5, value=3)

    st.markdown("---")

    character_name = st.text_input("Protagonist name", value="Elara")
    setting        = st.text_input("Setting", value="a rain-soaked old city")

    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem;color:#4a4760;line-height:1.6;'>Story length, image model, and audio output controls will be available in a future release.</div>", unsafe_allow_html=True)

    st.markdown("")
    nav_home = st.button("🏠  Home", use_container_width=True)
    nav_gen  = st.button("✍️  Generate Story", use_container_width=True)

    if nav_home: st.session_state.page = "home"
    if nav_gen:  st.session_state.page = "generate"


# ─────────────────────────────────────────────
# PAGE: HOME / INSTRUCTIONS
# ─────────────────────────────────────────────
if st.session_state.page == "home":

    st.markdown('<div class="hero-title">Story Forge</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-powered narrative generation — scenes, imagery, and beyond</div>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_intro, col_badge = st.columns([3, 1])
    with col_intro:
        st.markdown("""
        <div style='font-size:1rem;color:#9b8fa8;line-height:1.8;max-width:640px;'>
        Story Forge turns a single prompt into a fully structured narrative — complete with scenes,
        cinematic image prompts, and (in future releases) generated visuals and audio narration.
        Built for writers, game designers, educators, and anyone who wants to explore
        AI-assisted storytelling.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("### How it works")

    steps = [
        ("1", "Configure your story", "Use the sidebar to choose a genre, tone, number of scenes, your protagonist's name, and the setting."),
        ("2", "Write your prompt", "On the Generate page, describe the core idea or inciting event of your story in one or two sentences."),
        ("3", "Generate", "Click Generate Story. The AI will build a full narrative arc, broken into scenes with descriptions and image prompts."),
        ("4", "Explore your scenes", "Each scene displays its description, a cinematic image prompt, and a placeholder visual. Swap in a real image model when ready."),
        ("5", "Download", "Export your full story as a text file, or copy individual scene image prompts for use in image generation tools like Stable Diffusion."),
    ]

    for num, title, desc in steps:
        st.markdown(f"""
        <div class="step-box">
            <div class="step-num">{num}</div>
            <div class="step-content">
                <h4>{title}</h4>
                <p>{desc}</p>
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
                <div style='font-size:1.8rem;margin-bottom:0.4rem;'>{gval['emoji']}</div>
                <div style='font-family:"Playfair Display",serif;font-size:0.95rem;color:#f0ebe0;font-weight:700;'>{gkey.capitalize()}</div>
                <div style='font-size:0.75rem;color:#4a4760;margin-top:0.3rem;line-height:1.4;'>{gval['hook'][:50]}…</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("✍️  Start generating →", use_container_width=False):
        st.session_state.page = "generate"
        st.rerun()


# ─────────────────────────────────────────────
# PAGE: GENERATE STORY
# ─────────────────────────────────────────────
elif st.session_state.page == "generate":

    st.markdown('<div class="hero-title" style="font-size:2.4rem;">Generate Your Story</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <span class="genre-badge">{GENRE_DETAILS[genre]['emoji']} {genre.capitalize()}</span>
        <span class="genre-badge">🎭 {tone.capitalize()}</span>
        <span class="genre-badge">🎬 {num_scenes} scenes</span>
    </div>
    """, unsafe_allow_html=True)

    # Prompt input
    prompt = st.text_area(
        "Your story prompt",
        placeholder="e.g. A detective discovers a hidden map inside an old painting…",
        height=100,
        help="Describe the inciting event or central idea of your story."
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        generate_clicked = st.button("✨  Generate Story", use_container_width=True)
    with col_info:
        st.markdown(
            "<div style='padding-top:0.6rem;font-size:0.82rem;color:#4a4760;'>"
            f"Protagonist: <strong style='color:#7a7590;'>{character_name}</strong> · "
            f"Setting: <strong style='color:#7a7590;'>{setting}</strong>"
            "</div>",
            unsafe_allow_html=True
        )

    if generate_clicked:
        if not prompt.strip():
            st.warning("Please enter a story prompt before generating.")
        else:
            with st.spinner("Crafting your narrative…"):
                req = StoryRequest(
                    prompt=prompt,
                    genre=genre,
                    tone=tone,
                    num_scenes=num_scenes,
                    length=300,
                    character_name=character_name,
                    setting=setting
                )
                result = generate_mock_story(req)
                st.session_state.result = result
                st.session_state.req    = req

    # ── Display result ──
    if st.session_state.result:
        result: StoryResult = st.session_state.result
        req: StoryRequest   = st.session_state.req

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        tab_story, tab_scenes, tab_export = st.tabs(["📖  Full Story", "🎬  Scenes & Images", "📥  Export"])

        # ── TAB 1: Full story ──
        with tab_story:
            st.markdown(f'<div class="story-title">{result.title}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-bottom:1.5rem;'>
                <span class="genre-badge">{GENRE_DETAILS[req.genre]['emoji']} {req.genre.capitalize()}</span>
                <span class="genre-badge">🎭 {req.tone.capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="story-card"><div class="story-body">{result.story}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="word-count">Word count: {result.word_count}</div>', unsafe_allow_html=True)

        # ── TAB 2: Scenes + Images ──
        with tab_scenes:
            st.markdown(f"<div style='color:#4a4760;font-size:0.82rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.5rem;'>{len(result.scenes)} scenes generated</div>", unsafe_allow_html=True)

            for scene in result.scenes:
                with st.container():
                    img_col, text_col = st.columns([5, 4])

                    with img_col:
                        img = create_scene_image(scene, req.genre, req.setting)
                        st.image(img, use_container_width=True)

                        # Download button for the image
                        st.download_button(
                            label="⬇ Download image",
                            data=pil_to_bytes(img),
                            file_name=f"scene_{scene.scene_number}_{scene.title.replace(' ', '_')}.png",
                            mime="image/png",
                            use_container_width=True
                        )

                    with text_col:
                        st.markdown(f"""
                        <div class="scene-card">
                            <div class="scene-number">Scene {scene.scene_number}</div>
                            <div class="scene-title">{scene.title}</div>
                            <div class="scene-desc">{scene.description}</div>
                            <div class="image-prompt-box">
                                🎨 <strong>Image prompt:</strong><br>{scene.image_prompt}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("")

        # ── TAB 3: Export ──
        with tab_export:
            st.markdown("#### Export your story")

            # Full story text export
            export_text = f"STORY FORGE — GENERATED STORY\n{'='*60}\n\n"
            export_text += f"Title: {result.title}\n"
            export_text += f"Genre: {req.genre.capitalize()} | Tone: {req.tone.capitalize()}\n"
            export_text += f"Protagonist: {req.character_name} | Setting: {req.setting}\n"
            export_text += f"Word count: {result.word_count}\n\n"
            export_text += f"STORY\n{'-'*60}\n{result.story}\n\n"
            export_text += f"SCENES\n{'-'*60}\n"
            for s in result.scenes:
                export_text += f"\nScene {s.scene_number}: {s.title}\n"
                export_text += f"Description: {s.description}\n"
                export_text += f"Image Prompt: {s.image_prompt}\n"

            st.download_button(
                label="📄  Download full story (.txt)",
                data=export_text,
                file_name=f"{result.title.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=False
            )

            st.markdown("")
            st.markdown("#### Scene image prompts")
            st.markdown("<div style='font-size:0.85rem;color:#5e5a75;margin-bottom:1rem;'>Copy these into Stable Diffusion, Midjourney, or DALL·E to generate real scene images.</div>", unsafe_allow_html=True)

            for s in result.scenes:
                with st.expander(f"Scene {s.scene_number}: {s.title}"):
                    st.code(s.image_prompt, language=None)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("""
            <div style='background:#13121a;border:1px solid #2e2a3d;border-radius:10px;padding:1.2rem 1.5rem;'>
                <div style='font-size:0.82rem;color:#4a4760;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>Coming in future releases</div>
                <div style='font-size:0.9rem;color:#7a7590;line-height:1.8;'>
                    🖼 Real image generation via StableDiffusionXL<br>
                    🎬 Video clips via Video Stable Diffusion<br>
                    🔊 Audio narration via text-to-speech models<br>
                    🔗 FastAPI backend for on-demand story generation
                </div>
            </div>
            """, unsafe_allow_html=True)
