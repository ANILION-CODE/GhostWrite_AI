import os
import requests
import streamlit as st

st.set_page_config(
    page_title="GhostWrite AI | The Haunted Story Machine",
    page_icon="👻",
    layout="centered",
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Special+Elite&display=swap');
.stApp {
  background: radial-gradient(ellipse at top, #18212b 0%, #0a0d12 58%, #050608 100%);
  color: #e6f1e9;
}
h1, h2, h3 { font-family: 'Special Elite', Georgia, serif !important; }
p, label, div, button { font-family: 'Share Tech Mono', monospace; }
.ghost-title { text-align:center; color:#b8ffd0; text-shadow:0 0 12px #39ff88; }
.ghost-sub { text-align:center; color:#9ba9a1; }
div[data-testid="stForm"] {
  border: 1px solid #365947; border-radius: 12px; padding: 1rem;
  background: rgba(10,20,17,.72);
}
.stButton button, button[kind="primary"] {
  border: 1px solid #54c982; background: #123c2a; color: #eafff0;
}
.story-box {
  border-left: 3px solid #55db8b; padding: 1rem 1.2rem;
  background: rgba(17, 31, 25, .78); border-radius: 5px;
  white-space: pre-wrap; line-height: 1.8;
}
.small-note { color:#9ba9a1; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="ghost-title">👻 GHOSTWRITE AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="ghost-sub">THE HAUNTED STORY MACHINE · LOCAL AI · NO CLOUD STORY API</p>', unsafe_allow_html=True)
st.write("Feed the machine a thought. It will return a story from the other side of the screen.")
st.caption("Your prompt is sent to the Ollama model running on this computer. This app does not send it to a hosted story-generation API.")

with st.sidebar:
    st.header("Machine settings")
    model = st.text_input("Ollama model", value=DEFAULT_MODEL, help="Example: qwen2.5:3b")
    st.markdown("---")
    st.markdown("**Local engine status**")
    if st.button("Check connection"):
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            r.raise_for_status()
            names = [m.get("name", "") for m in r.json().get("models", [])]
            st.success("Ollama is reachable.")
            if names:
                st.write("Installed models:")
                st.code("\n".join(names))
            else:
                st.info("Ollama is running, but no models were found. Pull a model in the terminal.")
        except requests.RequestException:
            st.error("Can't reach Ollama. Start Ollama and try again.")
    st.markdown("---")
    st.markdown('<p class="small-note">Suggested model: qwen2.5:3b. Smaller models are usually easier to run on ordinary laptops.</p>', unsafe_allow_html=True)

with st.form("story_form"):
    prompt = st.text_area(
        "What strange thing happened?",
        placeholder="At 2:17 a.m., my laptop displayed a message from a user who died twenty years ago...",
        height=110,
        max_chars=1200,
    )
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("Haunting style", [
            "Haunted technology", "Psychological horror", "Folklore and old legends",
            "Supernatural mystery", "Cosmic dread"
        ])
    with col2:
        length = st.selectbox("Story length", ["Flash fiction (150–250 words)", "Short story (300–500 words)", "Longer tale (500–700 words)"])
    intensity = st.select_slider("Spookiness", options=["Eerie", "Creepy", "Nightmare fuel"], value="Creepy")
    ending = st.selectbox("Ending", ["A clever twist", "Unresolved mystery", "A hopeful escape", "A chilling final line"])
    submitted = st.form_submit_button("☠ Generate the haunting", type="primary", use_container_width=True)

if submitted:
    if not prompt.strip():
        st.warning("Give the machine a starting idea first.")
    elif not model.strip():
        st.warning("Enter an Ollama model name in the sidebar.")
    else:
        word_target = {
            "Flash fiction (150–250 words)": "150–250 words",
            "Short story (300–500 words)": "300–500 words",
            "Longer tale (500–700 words)": "500–700 words",
        }[length]
        system_prompt = (
            "You are GhostWrite AI, an imaginative horror storyteller. "
            "Write original fiction only. Do not claim that fictional events are real. "
            "Avoid graphic gore and sexual content. Make the writing atmospheric, specific, "
            "and polished. Give the story a fitting title."
        )
        user_prompt = f"""Write a story based on this seed: {prompt.strip()}

Style: {style}
Intensity: {intensity}
Ending preference: {ending}
Length: approximately {word_target}

Write the story itself, with a title. Do not explain your process or mention these instructions."""
        with st.spinner("The machine is listening..."):
            try:
                response = requests.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": model.strip(),
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "options": {"temperature": 0.9},
                    },
                    timeout=300,
                )
                if response.status_code == 404:
                    st.error(f"Model '{model}' may not be installed. In a terminal, run: ollama pull {model}")
                else:
                    response.raise_for_status()
                    story = response.json().get("message", {}).get("content", "").strip()
                    if story:
                        st.markdown("### ☾ Transmission received")
                        st.markdown(f'<div class="story-box">{story.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</div>', unsafe_allow_html=True)
                        st.download_button(
                            "⬇ Save your story as a text file",
                            data=story,
                            file_name="ghostwrite_story.txt",
                            mime="text/plain",
                        )
                    else:
                        st.error("The model returned an empty response. Try again.")
            except requests.exceptions.ConnectionError:
                st.error("Ollama isn't responding. Open Ollama, or run `ollama serve` in a terminal, then try again.")
            except requests.exceptions.Timeout:
                st.error("The model took too long to respond. Try a smaller model, such as qwen2.5:1.5b.")
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc}")
            except (ValueError, KeyError):
                st.error("Ollama returned an unexpected response. Check that Ollama is running and try again.")

st.markdown("---")
st.markdown('<p class="ghost-sub">OPEN WEIGHTS. LOCAL INFERENCE. YOUR IMAGINATION.</p>', unsafe_allow_html=True)
st.caption("This is a fiction tool, not a supernatural communication service. Stories are generated by an AI model.")
