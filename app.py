import streamlit as st
import time
import random
import numpy as np
import io
import wave
import base64

st.set_page_config(page_title="Retro Timer Game", page_icon="🕹️")

st.title("🕹️ Retro Timer Game")
st.write("Stop de teller precies op de aangegeven tijd!")

# -------- Chiptune videogame muziek --------
def generate_chiptune(duration=12, sample_rate=44100):
    melody = [
        (880, 0.15), (988, 0.15), (1047, 0.2),
        (988, 0.15), (880, 0.15), (784, 0.2),
        (659, 0.15), (784, 0.15), (880, 0.2),
        (659, 0.15), (523, 0.3)
    ]

    audio = np.array([], dtype=np.float32)

    for freq, dur in melody * int(duration / 2):
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        wave_data = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))  # square wave
        audio = np.concatenate((audio, wave_data))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())

    return buffer.getvalue()

# autoplay muziek via HTML
music_bytes = generate_chiptune()
b64 = base64.b64encode(music_bytes).decode()
audio_html = f"""
<audio autoplay loop>
  <source src="data:audio/wav;base64,{b64}" type="audio/wav">
</audio>
"""
st.components.v1.html(audio_html, height=0)

# -------- Game state --------
if "target_time" not in st.session_state:
    st.session_state.target_time = round(random.uniform(5, 10), 3)

if "running" not in st.session_state:
    st.session_state.running = False

if "start_time" not in st.session_state:
    st.session_state.start_time = 0

st.subheader(f"🎯 Doeltijd: {st.session_state.target_time:.3f} seconden")

timer_display = st.empty()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start"):
        st.session_state.start_time = time.time()
        st.session_state.running = True

with col2:
    if st.button("Stop"):
        if st.session_state.running:
            elapsed = time.time() - st.session_state.start_time
            st.session_state.running = False
            diff = abs(elapsed - st.session_state.target_time)

            st.subheader("Resultaat")
            st.write(f"⏱️ Jouw tijd: **{elapsed:.3f} s**")
            st.write(f"📏 Verschil: **{diff:.3f} s**")

            if diff < 0.05:
                st.success("PERFECT! 🕹️✨")
            elif diff < 0.2:
                st.info("Bijna!")
            else:
                st.warning("Nog eens proberen!")

with col3:
    if st.button("Nieuwe ronde"):
        st.session_state.target_time = round(random.uniform(5, 10), 3)
        st.session_state.running = False
        st.rerun()

# -------- Live teller --------
if st.session_state.running:
    while st.session_state.running:
        elapsed = time.time() - st.session_state.start_time
        timer_display.markdown(
            f"# ⏱️ {elapsed:0.3f} s"
        )
        time.sleep(0.02)
else:
    timer_display.markdown("# ⏱️ 0.000 s")