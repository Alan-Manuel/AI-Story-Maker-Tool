import streamlit as st
import random
import textwrap
import io
from datetime import datetime
from dataclasses import dataclass
from typing import List
from PIL import Image, ImageDraw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Story Forge ML",
    page_icon="📖",
    layout="wide"
)

# ---------------------------------------------------
# AESTHETIC UI
# ---------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0b0d14;
    color: #f1f1f1;
}

.stApp {
    background:
    radial-gradient(circle at top left, #1b1f36 0%, #0b0d14 45%);
}

.hero {
    text-align:center;
    padding: 2rem 0;
}

.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 5rem;
    color: #ffffff;
}

.hero p {
    color: #9ba4d0;
    font-size: 1.1rem;
}

.story-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 2rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(14px);
}

.scene-card {
    background: #121626;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.genre-chip {
    display:inline-block;
    background:#242a45;
    color:#c6d0ff;
    padding:0.35rem 0.8rem;
    border-radius:999px;
    margin-right:0.4rem;
    font-size:0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------
@dataclass
class Scene:
    number: int
    title: str
    description: str

@dataclass
class StoryResult:
    title: str
    story: str
    scenes: List[Scene]

# ---------------------------------------------------
# ML-LIKE STORY ENGINE
# ---------------------------------------------------
story_patterns = [
    "a mysterious glowing door appears in the city",
    "an astronaut discovers an abandoned signal",
    "a detective uncovers a hidden society",
    "a magical forest begins whispering secrets",
    "an explorer finds an ancient underground kingdom",
]

genres = {
    "Fantasy": ["magic", "kingdom", "ancient", "dragon"],
    "Sci-Fi": ["spaceship", "AI", "future", "signal"],
    "Mystery": ["clue", "shadow", "detective", "secret"],
    "Adventure": ["journey", "map", "ruins", "expedition"]
}

vectorizer = TfidfVectorizer()

all_patterns = story_patterns + [word for g in genres.values() for word in g]
X = vectorizer.fit_transform(all_patterns)

def detect_theme(prompt):
    prompt_vec = vectorizer.transform([prompt])
    similarity = cosine_similarity(prompt_vec, X)
    best_match = similarity.argmax()

    if best_match < len(story_patterns):
        return story_patterns[best_match]

    return random.choice(story_patterns)

# ---------------------------------------------------
# STORY GENERATOR
# ---------------------------------------------------
def generate_story(prompt, genre, protagonist, setting):

    detected = detect_theme(prompt)

    title_words = [
        "Echo",
        "Shadow",
        "Chronicle",
        "Signal",
        "Kingdom",
        "Gate"
    ]

    title = f"The {random.choice(title_words)} of {protagonist}"

    intro = (
        f"In {setting}, {protagonist} discovers that {detected}. "
        f"What begins as curiosity quickly becomes something far more dangerous."
    )

    middle = (
        f"As events unfold, hidden truths emerge from the shadows. "
        f"The deeper {protagonist} goes, the more reality begins to fracture."
    )

    ending = (
        f"In the final confrontation, everything changes forever. "
        f"{protagonist} must decide whether to embrace the unknown or destroy it."
    )

    full_story = f"{intro}\n\n{middle}\n\n{ending}"

    scenes = [
        Scene(1, "The Discovery", intro),
        Scene(2, "The Descent", middle),
        Scene(3, "The Final Choice", ending),
    ]

    return StoryResult(
        title=title,
        story=full_story,
        scenes=scenes
    )

# ---------------------------------------------------
# IMAGE GENERATION
# ---------------------------------------------------
def generate_scene_image(scene_title, genre):
    W, H = 768, 432

    palettes = {
        "Fantasy": ((80,40,140), (180,120,255)),
        "Sci-Fi": ((20,120,180), (120,255,255)),
        "Mystery": ((40,40,60), (180,180,220)),
        "Adventure": ((80,100,40), (220,220,120))
    }

    bg, fg = palettes.get(genre, ((50,50,70),(200,200,255)))

    img = Image.new("RGB", (W,H), bg)
    draw = ImageDraw.Draw(img)

    for i in range(120):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        x2 = x1 + random.randint(10,120)
        y2 = y1 + random.randint(10,120)

        draw.ellipse([x1,y1,x2,y2], outline=fg)

    draw.text((40,40), scene_title, fill=fg)

    return img

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Story Forge ML</h1>
    <p>Local AI-inspired storytelling using procedural generation + ML similarity matching</p>
</div>
""", unsafe_allow_html=True)

genre = st.selectbox(
    "Genre",
    ["Fantasy", "Sci-Fi", "Mystery", "Adventure"]
)

protagonist = st.text_input(
    "Protagonist",
    "Elara"
)

setting = st.text_input(
    "Setting",
    "a neon-lit forgotten city"
)

prompt = st.text_area(
    "Story Prompt",
    "A strange portal opens beneath the city..."
)

if st.button("✨ Generate Story"):

    result = generate_story(
        prompt,
        genre,
        protagonist,
        setting
    )

    st.markdown(f"""
    <div class="story-card">
        <h1>{result.title}</h1>
        <div class="genre-chip">{genre}</div>
        <br><br>
        <p style='line-height:2;font-size:1.05rem;'>{result.story}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🎬 Scenes")

    for scene in result.scenes:

        img = generate_scene_image(scene.title, genre)

        st.image(img, use_container_width=True)

        st.markdown(f"""
        <div class="scene-card">
            <h3>{scene.number}. {scene.title}</h3>
            <p>{scene.description}</p>
        </div>
        """, unsafe_allow_html=True)
