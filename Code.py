import os
import streamlit as st
import base64
import zipfile
import tempfile
from PIL import Image
import time as t
from PyPDF2 import PdfReader
import re
import soundfile as sf
from threading import Thread
import playsound
def fetch_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
def play_alarm():
    sound_file = "alarm-327234.mp3"
    try:
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception:
        st.warning("Alarm sound file missing or error playing alarm.")

if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "stop" not in st.session_state:
    st.session_state.stop = False
if "start_clicked" not in st.session_state:
    st.session_state.start_clicked = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
# Sidebar navigation
st.sidebar.title("Test")
selection = st.sidebar.radio("Go to", [
    "Home",
    "TAT (Thematic Apperception test)",
    "WAT (Word Association test)",
    "SRT (Situation Reaction test)",
    "Lecturrette"
])

if selection == "Home":
    final_image = fetch_image("backgroundimage.jpg")
    st.markdown(
        f"""
        <style>
        .main-title {{
            text-align: center !important;
            color: black !important;
            font-size: 80px !important;
            font-weight: bold !important;
            margin-top: 2rem;
        }}
        .stApp {{
            background-image: url("data:image/jpg;base64,{final_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;
        }}
        </style>
        <div class="main-title">Welcome Cadets</div>
        """,
        unsafe_allow_html=True
    )

elif selection == "TAT (Thematic Apperception test)":
    st.title("Thematic Apperception Test")

    # Inputs
    time_image = st.number_input("Enter viewing time for image (seconds)", min_value=1, value=30)
    time_story = st.number_input("Enter time for story writing (seconds)", min_value=1, value=240)
    frequency = st.number_input("Enter frequency (number of cycles)", min_value=1, value=5)
    break_time = st.number_input("Enter break/interval time (seconds)", min_value=1, value=10)
    show_timer_and_alarm = st.toggle("Show Timer and Play Alarm Sound", value=True)
    uploaded_zip = st.file_uploader("Upload a ZIP file containing images", type=["zip"])

    # State variables
    if "tat_running" not in st.session_state:
        st.session_state.tat_running = False
    if "tat_start_clicked" not in st.session_state:
        st.session_state.tat_start_clicked = False
    if "tat_stop" not in st.session_state:
        st.session_state.tat_stop = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start TAT Test", disabled=not uploaded_zip or st.session_state.tat_running):
            st.session_state.tat_running = True
            st.session_state.tat_start_clicked = True
            st.session_state.tat_stop = False
    with col2:
        if st.button("Stop Test", disabled=not st.session_state.tat_running):
            st.session_state.tat_running = False
            st.session_state.tat_start_clicked = False
            st.session_state.tat_stop = True

    # Alarm function
    def play_alarm():
        if not show_timer_and_alarm:
            return
        sound_file = "sound.mp3"
        try:
            with open(sound_file, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    """
                st.markdown(md, unsafe_allow_html=True)
        except Exception:
            st.warning("Alarm sound file missing or error playing alarm.")

    # If test is started
    if st.session_state.tat_start_clicked and uploaded_zip:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract ZIP
            with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            # Collect image file paths (including subdirectories)
            image_files = []
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        image_files.append(os.path.join(root, file))
            image_files = sorted(image_files)

            if not image_files:
                st.error("No images found in ZIP file. Ensure it contains .jpg/.jpeg/.png files.")
                st.session_state.tat_running = False
                st.session_state.tat_start_clicked = False
                st.stop()

            # Limit to frequency if more images
            image_files = image_files[:frequency]

            # Placeholders
            image_placeholder = st.empty()
            message_placeholder = st.empty()
            break_placeholder = st.empty()

            # Test Loop
            for i, img_path in enumerate(image_files):
                if st.session_state.tat_stop:
                    break

                # 1. Show image
                image = Image.open(img_path)
                image_placeholder.image(image, caption=f"Image {i+1}", use_container_width=True)

                if show_timer_and_alarm:
                    for sec in range(time_image, 0, -1):
                        if st.session_state.tat_stop:
                            break
                        message_placeholder.markdown(f"⏳ Viewing Time Remaining: **{sec} seconds**")
                        t.sleep(1)

                if st.session_state.tat_stop:
                    break

                image_placeholder.empty()
                message_placeholder.empty()

                # 2. Alarm + Break after image
                play_alarm()
                if show_timer_and_alarm:
                    for sec in range(break_time, 0, -1):
                        if st.session_state.tat_stop:
                            break
                        break_placeholder.markdown(f"🔔 Break Time (after image): **{sec} seconds**")
                        t.sleep(1)
                    break_placeholder.empty()

                if st.session_state.tat_stop:
                    break

                # 3. Story Writing
                if show_timer_and_alarm:
                    for sec in range(time_story, 0, -1):
                        if st.session_state.tat_stop:
                            break
                        message_placeholder.markdown(f"✍️ Story Writing Time Remaining: **{sec} seconds**")
                        t.sleep(1)
                    message_placeholder.empty()
                else:
                    message_placeholder.markdown("✍️ Story writing in progress... (Timer Hidden)")
                    t.sleep(time_story)
                    message_placeholder.empty()

                if st.session_state.tat_stop:
                    break

                # 4. Alarm + Break after story
                play_alarm()
                if show_timer_and_alarm:
                    for sec in range(break_time, 0, -1):
                        if st.session_state.tat_stop:
                            break
                        break_placeholder.markdown(f"🔔 Break Time (after story): **{sec} seconds**")
                        t.sleep(1)
                    break_placeholder.empty()

            st.session_state.tat_running = False
            st.session_state.tat_start_clicked = False
            st.success("TAT session completed or stopped.")
elif selection == "WAT (Word Association test)":
    st.title("Word Association Test")

    # Initialize session state
    for key in ["wat_running", "wat_stop", "wat_start_clicked", "wat_file", "wat_show_timer"]:
        if key not in st.session_state:
            st.session_state[key] = False if "file" not in key else None

    # Only set toggle before starting
    if not st.session_state.wat_running:
        st.session_state.wat_show_timer = st.toggle("Show Timer & Play Sound")

    # Inputs
    word_display_time = st.number_input("Word Display Time (seconds)", min_value=1, value=15)
    break_time = st.number_input("Break Time (seconds)", min_value=1, value=3)
    frequency = st.number_input("Number of Words to Show", min_value=1, value=3)
    uploaded_file = st.file_uploader("Upload Words File (.txt or .pdf)", type=["txt", "pdf"])

    # Extract words function
    if uploaded_file and not st.session_state.get("wat_words"):
        def extract_words(file):
            if file.name.endswith(".txt"):
                content = file.read().decode("utf-8")
            elif file.name.endswith(".pdf"):
                reader = PdfReader(file)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
            else:
                return []
            lines = content.splitlines()
            words = []
            for line in lines:
                cleaned = ''.join([c for c in line if not c.isdigit()]).strip()
                words.extend(cleaned.split())
            return [word.strip() for word in words if word.strip()]


        st.session_state.wat_words = extract_words(uploaded_file)


    # Play alarm
    def play_alarm():
        sound_file = "mixkit-software-interface-back-2575.wav"
        try:
            with open(sound_file, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>""", unsafe_allow_html=True)
        except:
            st.warning("Sound file not found or failed to play.")

    # Start / Stop buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Test", disabled=st.session_state.wat_running or not uploaded_file):
            st.session_state.wat_start_clicked = True
            st.session_state.wat_running = True
            st.session_state.wat_stop = False
            st.session_state.wat_file = uploaded_file
    with col2:
        if st.button("Stop Test", disabled=not st.session_state.wat_running):
            st.session_state.wat_stop = True
            st.session_state.wat_running = False
            st.session_state.wat_start_clicked = False

    # Main logic
    if st.session_state.wat_start_clicked and st.session_state.wat_file:
        words = st.session_state.get("wat_words", [])
        display = st.empty()
        timer = st.empty()
        total = min(frequency, len(words))
        show_timer = st.session_state.wat_show_timer  # store toggle value before loop

        for i in range(total):
            if st.session_state.wat_stop:
                break

            # Show word
            word = words[i]
            display.markdown(f"<h1 style='text-align:center; color:green;'>{word}</h1>", unsafe_allow_html=True)

            # First Timer (Word Display)
            for sec in range(word_display_time, 0, -1):
                if st.session_state.wat_stop:
                    break
                if show_timer:
                    timer.markdown(f"⏳ **Time Left: {sec} sec**")
                t.sleep(1)
            timer.empty()

            if show_timer:
                play_alarm()

            display.empty()
            if st.session_state.wat_stop:
                break

            # Break Time
            for sec in range(break_time, 0, -1):
                if st.session_state.wat_stop:
                    break
                if show_timer:
                    display.markdown(f"🛑 **Break Time: {sec} sec**", unsafe_allow_html=True)
                t.sleep(1)
            display.empty()

        st.session_state.wat_running = False
        st.session_state.wat_start_clicked = False
        st.success("WAT session completed or stopped.")
        st.session_state.wat_words = None
elif selection == "SRT (Situation Reaction test)":
    st.title("Situation Reaction Test")

    # Session state init
    for key in ["srt_running", "srt_stop", "srt_start_clicked", "srt_file"]:
        if key not in st.session_state:
            st.session_state[key] = False if "file" not in key else None

    # Toggle for timers and audio
    show_timer_audio = st.toggle("Show Timer & Play Sound")

    # Inputs
    display_time = st.number_input("Situation Display Time (seconds)", min_value=1, value=15)
    break_time = st.number_input("Break Time (seconds)", min_value=1, value=5)
    frequency = st.number_input("Number of Situations", min_value=1, value=5)
    uploaded_file = st.file_uploader("Upload File (.txt or .pdf)", type=["txt", "pdf"])

    # Alarm function
    def play_alarm():
        sound_file = "mixkit-software-interface-back-2575.wav"
        try:
            with open(sound_file, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(md, unsafe_allow_html=True)
        except Exception:
            st.warning("Alarm sound file not found or failed to play.")

    # Extract sentences
    def extract_sentences(file):
        if file.name.endswith(".txt"):
            content = file.read().decode("utf-8")
        elif file.name.endswith(".pdf"):
            reader = PdfReader(file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
        else:
            return []
        return [line.strip() for line in content.splitlines() if line.strip()]

    # Start/Stop buttons
    if st.button("Start Test", disabled=st.session_state.srt_running or not uploaded_file):
        st.session_state.srt_start_clicked = True
        st.session_state.srt_running = True
        st.session_state.srt_stop = False
        st.session_state.srt_file = uploaded_file

    if st.button("Stop Test", disabled=not st.session_state.srt_running):
        st.session_state.srt_stop = True
        st.session_state.srt_running = False
        st.session_state.srt_start_clicked = False

    # Main Test Logic
    if st.session_state.srt_start_clicked and st.session_state.srt_file:
        situations = extract_sentences(st.session_state.srt_file)
        display = st.empty()
        timer = st.empty()
        total = min(frequency, len(situations))

        for i in range(total):
            if st.session_state.srt_stop:
                break

            display.markdown(f"<h2 style='text-align:center'>{situations[i]}</h2>", unsafe_allow_html=True)

            # Display Time
            if show_timer_audio:
                for sec in range(display_time, 0, -1):
                    if st.session_state.srt_stop:
                        break
                    timer.markdown(f"⏳ Time Left: **{sec} sec**")
                    t.sleep(1)
                timer.empty()
                play_alarm()
            else:
                t.sleep(display_time)

            display.empty()

            if st.session_state.srt_stop:
                break

            # Break Time
            if show_timer_audio:
                for sec in range(break_time, 0, -1):
                    if st.session_state.srt_stop:
                        break
                    display.markdown(f"🛑 Break Time: **{sec} sec**")
                    t.sleep(1)
                display.empty()
                play_alarm()
            else:
                t.sleep(break_time)

        st.session_state.srt_running = False
        st.session_state.srt_start_clicked = False
        st.success("SRT session completed or stopped.")
# elif selection == "Lecturrette":
#     st.title("Lecturrette")

#     for key in ["lec_running", "lec_stop", "lec_start_clicked", "audio_data"]:
#         if key not in st.session_state:
#             st.session_state[key] = False if key != "audio_data" else None

#     show_timer = st.toggle("Show Timer & Play Sound")

#     prep_time = st.number_input("Lecture Time (seconds)", min_value=10, value=150)
#     talk_time = st.number_input("Remaining Time (seconds)", min_value=5, value=30)
#     total_time = prep_time + talk_time

#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Start Lecturrette", disabled=st.session_state.lec_running):
#             st.session_state.lec_running = True
#             st.session_state.lec_stop = False
#             st.session_state.lec_start_clicked = True
#     with col2:
#         if st.button("Stop Lecturrette", disabled=not st.session_state.lec_running):
#             st.session_state.lec_stop = True
#             st.session_state.lec_running = False
#             st.session_state.lec_start_clicked = False

#     def record_audio(duration, filename="recorded_lecturrette.wav"):
#         fs = 44100
#         st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1)
#         sd.wait()
#         sf.write(filename, st.session_state.audio_data, fs)
#         return filename

#     def play_alarm():
#         sound_file = "mixkit-software-interface-back-2575.wav"
#         try:
#             with open(sound_file, "rb") as f:
#                 b64 = base64.b64encode(f.read()).decode()
#                 st.markdown(f"""
#                     <audio autoplay>
#                         <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#                     </audio>""", unsafe_allow_html=True)
#         except:
#             st.warning("Alarm sound file missing.")

#     if st.session_state.lec_start_clicked:
#         status = st.empty()
#         timer = st.empty()

#         status.markdown("🎙️ **Recording Started...**")
#         record_thread = Thread(target=record_audio, args=(total_time,))
#         record_thread.start()

#         # Lecture Time Countdown
#         if show_timer:
#             for sec in range(prep_time, 0, -1):
#                 if st.session_state.lec_stop:
#                     break
#                 timer.markdown(f"📝 **Lecture Time: {sec} seconds**")
#                 t.sleep(1)
#             timer.empty()
#         else:
#             t.sleep(prep_time)

#         if not st.session_state.lec_stop:
#             play_alarm()  # Always alert after lecture time (toggle doesn't matter)

#         # Talk Time Countdown
#         if not st.session_state.lec_stop:
#             if show_timer:
#                 for sec in range(talk_time, 0, -1):
#                     if st.session_state.lec_stop:
#                         break
#                     timer.markdown(f"🗣️ **Talk Time Remaining: {sec} seconds**")
#                     t.sleep(1)
#                 timer.empty()
#                 play_alarm()
#             else:
#                 t.sleep(talk_time)

#         record_thread.join()
#         st.session_state.lec_running = False
#         st.session_state.lec_start_clicked = False
#         st.success("Lecturrette session completed or stopped.")

#         # Show playback + download
#         if os.path.exists("recorded_lecturrette.wav"):
#             with open("recorded_lecturrette.wav", "rb") as f:
#                 audio_bytes = f.read()
#                 st.audio(audio_bytes, format="audio/wav")
#                 b64 = base64.b64encode(audio_bytes).decode()
#                 st.markdown(
#                     f'<a href="data:audio/wav;base64,{b64}" download="Lecturrette_Recording.wav">📥 Download Recording</a>',
#                     unsafe_allow_html=True
#                 )
elif selection == "Lecturrette":
    st.title("Lecturrette")

    for key in ["lec_running", "lec_stop", "lec_start_clicked"]:
        if key not in st.session_state:
            st.session_state[key] = False

    show_timer = st.toggle("Show Timer & Play Sound")

    prep_time = st.number_input("Lecture Time (seconds)", min_value=10, value=150)
    talk_time = st.number_input("Remaining Time (seconds)", min_value=5, value=30)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Lecturrette", disabled=st.session_state.lec_running):
            st.session_state.lec_running = True
            st.session_state.lec_stop = False
            st.session_state.lec_start_clicked = True
    with col2:
        if st.button("Stop Lecturrette", disabled=not st.session_state.lec_running):
            st.session_state.lec_stop = True
            st.session_state.lec_running = False
            st.session_state.lec_start_clicked = False

    def play_alarm():
        sound_file = "mixkit-software-interface-back-2575.mp3"  # Use just file name if in same directory
        try:
            with open(sound_file, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>""", unsafe_allow_html=True)
        except:
            st.warning("Alarm sound file missing.")

    if st.session_state.lec_start_clicked:
        timer = st.empty()

        # ⏳ Lecture Time
        if show_timer:
            for sec in range(prep_time, 0, -1):
                if st.session_state.lec_stop:
                    break
                timer.markdown(f"📝 **Lecture Time: {sec} seconds**")
                t.sleep(1)
            timer.empty()
        else:
            t.sleep(prep_time)

        if not st.session_state.lec_stop:
            play_alarm()  # Always play alarm after lecture time

        # 🗣️ Talk Time
        if not st.session_state.lec_stop:
            if show_timer:
                for sec in range(talk_time, 0, -1):
                    if st.session_state.lec_stop:
                        break
                    timer.markdown(f"🗣️ **Talk Time Remaining: {sec} seconds**")
                    t.sleep(1)
                timer.empty()
                play_alarm()
            else:
                t.sleep(talk_time)

        # Reset state
        st.session_state.lec_running = False
        st.session_state.lec_start_clicked = False
        st.success("Lecturrette session completed or stopped.")
