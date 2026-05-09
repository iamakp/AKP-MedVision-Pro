import os
import base64
import io
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps, ImageStat
import numpy as np
import uuid
import datetime
from groq import Groq

# External Files Import
from ui_components import apply_modern_ui, header_component
from report_generator import generate_professional_pdf

# ✅ Database import
from database import (
    save_patient,
    save_scan_result,
    upload_pdf,
    get_patient_history,
    get_total_patients,
    get_total_scans,
    get_positive_cases
)

# --- 1. CONFIG & UI SETUP ---
st.set_page_config(page_title="AKP Med-Vision Pro", layout="wide", page_icon="🧬")
apply_modern_ui()

if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'res' not in st.session_state: st.session_state.res = None
if 'conf' not in st.session_state: st.session_state.conf = 0

# --- 2. UNIQUE MEDICAL ID LOGIC ---
if 'generated_id' not in st.session_state:
    current_year = datetime.datetime.now().year
    unique_code = str(uuid.uuid4().hex[:6]).upper()
    st.session_state.generated_id = f"REG-{current_year}-{unique_code}"

# --- 3. API SETUP ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
groq_client  = Groq(api_key=GROQ_API_KEY)

# --- 4. MODEL LOADER ---
@st.cache_resource
def load_models():
    try:
        p_model = tf.keras.models.load_model('pneumonia_trained_model.h5')
        b_model = tf.keras.models.load_model('brain_tumor_model.h5')
        return p_model, b_model
    except:
        return None, None

p_model, b_model = load_models()


# --- 5. GROQ VISION VALIDATION (BEST VERSION) ---
def is_valid_medical_scan(image, mode):
    """
    Groq Llama 4 Scout Vision se validate karo.

    Strategy:
    - Pehle pixel check karo (fast & free)
    - Agar pixel check pass ho tabhi Groq Vision call karo
    - Dono milke decide karenge

    Isse:
    - Real X-Ray / MRI kabhi reject nahi hogi
    - Selfie / colorful photo reject hogi
    """

    # --- STEP A: Pixel Check (instant, free) ---
    pixel_valid = pixel_check(image)

    # Agar pixel check hi fail ho (colorful image) toh
    # seedha reject karo — Groq call ki zaroorat nahi
    if not pixel_valid:
        return False, "Image appears colorful or invalid (not a medical scan)"

    # --- STEP B: Groq Vision (sirf grayscale images pe) ---
    try:
        buffered = io.BytesIO()
        image.convert("RGB").save(buffered, format="JPEG", quality=90)
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        scan_type = "Chest X-Ray" if "Pneumonia" in mode else "Brain MRI Scan"

        # BEST PROMPT — very detailed, lenient for medical scans
        prompt = f"""You are a radiologist. Your task is simple: look at this image and decide if it is a medical scan.

This is the type of scan to check for: {scan_type}

IMPORTANT RULES:
1. Medical scans are ALWAYS grayscale or black-and-white
2. Chest X-Rays show: ribcage bones, lungs (dark areas), heart (white oval), spine
3. Brain MRI shows: brain tissue (gray), skull (white ring), dark background
4. Medical scans may look blurry, low quality, or have text/markers on them — still count as YES
5. Only say NO if the image is CLEARLY something non-medical like:
   - A person's face or body photo
   - Nature, food, animals, objects
   - A cartoon, drawing, or screenshot
   - A completely random non-medical image

Based on these rules, is this image a {scan_type}?

Answer with ONLY one word: YES or NO"""

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=5,
        )

        result = response.choices[0].message.content.strip().upper()

        # Sirf clearly "NO" hone pe reject karo
        if result.startswith("NO"):
            return False, "AI Vision: Not a valid medical scan"

        return True, "Valid medical scan"

    except Exception as e:
        # Groq fail ho toh pixel check result pe trust karo
        st.warning(f"⚠️ Groq Vision skipped, pixel check used: {e}")
        return True, "Valid (pixel check passed)"


def pixel_check(image):
    """
    Fast pixel-level check:
    - Grayscale honi chahiye (R ≈ G ≈ B)
    - Blank nahi honi chahiye
    - Kuch texture honi chahiye
    """
    try:
        stat = ImageStat.Stat(image.convert("RGB"))
        r, g, b = stat.mean[0], stat.mean[1], stat.mean[2]
        r_std, g_std, b_std = stat.stddev[0], stat.stddev[1], stat.stddev[2]

        color_diff   = abs(r - g) + abs(g - b) + abs(r - b)
        overall_mean = (r + g + b) / 3
        overall_std  = (r_std + g_std + b_std) / 3

        if color_diff > 35:   return False  # Colorful image
        if overall_mean > 245: return False  # Blank white
        if overall_mean < 5:   return False  # Blank black
        if overall_std < 8:    return False  # No texture

        return True
    except:
        return True  # Error = allow


# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    st.markdown("### 📋 PATIENT REGISTRY")

    raw_name = st.text_input("Full Name", value="", placeholder="Enter Patient Name")
    clean_p_name = raw_name.split('[')[0].strip()

    p_id = st.text_input("Patient ID (Auto-Generated)", value=st.session_state.generated_id, disabled=True)
    p_gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    p_age = st.number_input("Age", min_value=0, max_value=120, value=0)

    if st.button("Generate New Patient ID"):
        unique_code = str(uuid.uuid4().hex[:6]).upper()
        st.session_state.generated_id = f"REG-{datetime.datetime.now().year}-{unique_code}"
        st.rerun()

    st.divider()

    # 📊 Live Stats
    st.markdown("### 📊 SYSTEM STATS")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Patients", get_total_patients())
        st.metric("Positive", get_positive_cases())
    with col_b:
        st.metric("Scans", get_total_scans())

    st.divider()

    # 🕓 Scan History
    if clean_p_name:
        st.markdown("### 🕓 Scan History")
        history = get_patient_history(st.session_state.generated_id)
        if history:
            for record in history:
                is_normal = record['result'] in ["NORMAL", "No Tumor"]
                color = "#00ffcc" if is_normal else "#ff4b4b"
                st.markdown(f"""
                    <div style="background:#1a1a2e; padding:8px; border-radius:8px;
                                margin-bottom:5px; font-size:12px;
                                border-left: 3px solid {color};">
                        <b style="color:{color};">{record['result']}</b><br>
                        <span style="color:#aaa;">{record['scan_mode']}</span><br>
                        <span style="color:#aaa;">Conf: {record['confidence']}%</span><br>
                        <span style="color:#555;">{record['scanned_at'][:10]}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No previous scans found.")

    st.divider()
    st.success("System Status: Online 🟢")
    st.success("Database: Connected 🟢")


# --- 7. MAIN DASHBOARD ---
header_component()

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🛠️ SCAN CONFIGURATION")
    mode = st.selectbox("Select Modality", ["Pneumonia (Chest X-Ray)", "Brain Tumor (MRI Scan)"])
    file = st.file_uploader("Upload Medical Scan", type=["jpg", "png", "jpeg"])

    if file:
        img = Image.open(file)
        st.image(img, caption="Input Stream", use_container_width=True)

        if st.button("🚀 EXECUTE NEURAL SCAN"):

            # ✅ STEP 1: Validation
            with st.spinner("🔍 Verifying scan authenticity..."):
                is_medical, reason = is_valid_medical_scan(img, mode)

            if not is_medical:
                scan_label = "Chest X-Ray" if "Pneumonia" in mode else "Brain MRI Scan"
                st.error(
                    f"❌ INVALID IMAGE: This does not appear to be a valid {scan_label}.\n\n"
                    f"Reason: {reason}\n\n"
                    "Please upload a genuine medical radiological image."
                )
                st.session_state.res = None

            else:
                # ✅ STEP 2: Model Prediction
                with st.spinner("⚙️ Analyzing Clinical Features..."):
                    processed = ImageOps.fit(img.convert('RGB'), (224, 224), Image.Resampling.LANCZOS)
                    arr = np.expand_dims(np.array(processed).astype(np.float32) / 255.0, axis=0)

                    if "Pneumonia" in mode:
                        if p_model is None:
                            st.error("❌ Pneumonia model not loaded.")
                        else:
                            pred = p_model.predict(arr, verbose=0)[0][0]
                            res = "PNEUMONIA DETECTED" if pred > 0.5 else "NORMAL"
                            conf = pred if pred > 0.5 else (1 - pred)
                            st.session_state.res, st.session_state.conf = res, conf * 100
                    else:
                        if b_model is None:
                            st.error("❌ Brain tumor model not loaded.")
                        else:
                            pred = b_model.predict(arr, verbose=0)
                            classes = ['Glioma Tumor', 'Meningioma Tumor', 'No Tumor', 'Pituitary Tumor']
                            res = classes[np.argmax(pred[0])]
                            conf = np.max(pred[0])
                            st.session_state.res, st.session_state.conf = res, conf * 100

                # ✅ STEP 3: Database mein save karo
                if st.session_state.res:
                    with st.spinner("💾 Saving to database..."):
                        save_patient(
                            st.session_state.generated_id,
                            clean_p_name,
                            p_age,
                            p_gender
                        )
                        save_scan_result(
                            st.session_state.generated_id,
                            mode,
                            st.session_state.res,
                            st.session_state.conf
                        )
                    st.success("✅ Scan saved to database!")

    st.markdown('</div>', unsafe_allow_html=True)


# --- 8. RESULTS PANEL ---
with col2:
    if st.session_state.res:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 ANALYSIS FINDINGS")

        is_normal = "NORMAL" in st.session_state.res or "No Tumor" in st.session_state.res
        color = "#00ffcc" if is_normal else "#ff4b4b"

        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3); padding:20px; border-radius:15px;
                        border-left: 5px solid {color};">
                <h2 style="color:{color}; margin:0;">{st.session_state.res}</h2>
                <p style="color:#aaa;">Confidence Score: {st.session_state.conf:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📄 DOCUMENTATION")
        report_file = f"Report_{st.session_state.generated_id}.pdf"

        if st.button("GENERATE CLINICAL PDF"):
            generate_professional_pdf(
                clean_p_name, st.session_state.generated_id,
                p_age, p_gender, mode,
                st.session_state.res, st.session_state.conf, report_file
            )

            with st.spinner("☁️ Uploading PDF to cloud..."):
                pdf_url = upload_pdf(report_file, st.session_state.generated_id)

            if pdf_url:
                st.success("✅ PDF saved to cloud!")
                st.markdown(f"[☁️ View Online]({pdf_url})")

            with open(report_file, "rb") as f:
                st.download_button("📥 DOWNLOAD REPORT", f, file_name=report_file)

        st.markdown('</div>', unsafe_allow_html=True)


# --- 9. AI CLINICAL CHATBOT ---
if st.session_state.res:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💬 AI CLINICAL ASSISTANT")
    user_q = st.chat_input("Ask a question about the diagnosis...")

    if user_q:
        sys_prompt = (
            f"You are a Clinical AI Assistant. Always address the patient as '{clean_p_name}'. "
            "Strict Rule: Do NOT explain or expand acronyms like 'AKP'. "
            "Do NOT mention biochemistry terms like 'Phosphate' or 'Adenosine'. "
            "Answer the query based on the scan result professionally."
        )

        ans = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"Diagnosis: {st.session_state.res}. Question: {user_q}"}
            ]
        ).choices[0].message.content
        st.session_state.chat_log.append({"u": user_q, "a": ans})

    for m in reversed(st.session_state.chat_log):
        st.markdown(f"<div class='chat-bubble user-bubble'><b>Physician:</b> {m['u']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble ai-bubble'><b>AI Assistant:</b> {m['a']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- 10. FOOTER ---
st.markdown(
    "<p style='text-align:center; color:#555; font-size:12px;'>"
    "Project by Abhishek Kumar Prajapati (23BCS006) and Laxman Singh Kirar (23bcs048) | SMVDU Katra | 2026"
    "</p>",
    unsafe_allow_html=True
)