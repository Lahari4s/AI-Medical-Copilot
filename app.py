import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from database.db import (
    init_db,
    create_chat,
    get_user_chats,
    rename_chat,
    delete_chat,
    add_message,
    get_messages,
    save_report,
    save_food_log,
    get_food_logs,
    add_reminder,
    get_reminders,
    save_health_log,
    get_health_logs
)

from src.auth import signup, login
from src.ocr_utils import extract_text_from_pdf, extract_text_from_scanned_pdf, extract_text_from_image
from src.smart_analyzer import detect_abnormal_values
from src.disease_predictor import predict_possible_conditions
from src.medicine_checker import check_medicine_safety
from src.pdf_export import generate_pdf_report
from src.llm_client import call_ai
from src.food_tracker import analyze_food
from src.health_tracker import build_health_dataframe, create_trend_chart
from src.report_comparator import compare_reports
from src.prompts import report_analysis_prompt, prescription_prompt

init_db()

st.set_page_config(
    page_title="AI Medical Copilot",
    page_icon="🩺",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "report_text" not in st.session_state:
    st.session_state.report_text = ""


def read_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)

        if len(text.strip()) < 50:
            uploaded_file.seek(0)
            text = extract_text_from_scanned_pdf(uploaded_file)

        return text

    return extract_text_from_image(uploaded_file)


def calculate_health_score(text):
    score = 100
    lower = text.lower()

    if "glucose" in lower:
        score -= 10
    if "cholesterol" in lower:
        score -= 10
    if "diabetes" in lower:
        score -= 10
    if "thyroid" in lower:
        score -= 5
    if "blood pressure" in lower or "bp" in lower:
        score -= 5

    return max(score, 0)


# ---------------- AUTH ----------------

if not st.session_state.logged_in:
    st.title("🩺 AI Medical Copilot")

    option = st.radio(
        "Choose",
        ["Login", "Signup"],
        horizontal=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        if st.button("Create Account"):
            ok, msg = signup(username, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    if option == "Login":
        if st.button("Login"):
            ok, user_id = login(username, password)

            if ok:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username

                chats = get_user_chats(user_id)

                if chats:
                    st.session_state.active_chat_id = chats[0][0]
                else:
                    st.session_state.active_chat_id = create_chat(user_id)

                st.rerun()
            else:
                st.error("Invalid login")

    st.stop()


# ---------------- SIDEBAR ----------------

st.sidebar.title("🧠 AI Medical Copilot")
st.sidebar.success(f"User: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

if st.sidebar.button("➕ New Chat"):
    st.session_state.active_chat_id = create_chat(st.session_state.user_id)
    st.session_state.report_text = ""
    st.rerun()

st.sidebar.subheader("💬 Chat History")

for chat_id, title, updated_at in get_user_chats(st.session_state.user_id):
    col1, col2, col3 = st.sidebar.columns([5, 1, 1])

    if col1.button(title[:24], key=f"open_{chat_id}"):
        st.session_state.active_chat_id = chat_id
        st.session_state.report_text = ""
        st.rerun()

    if col2.button("✏", key=f"edit_{chat_id}"):
        st.session_state[f"rename_{chat_id}"] = True

    if col3.button("🗑", key=f"delete_{chat_id}"):
        delete_chat(chat_id)

        chats = get_user_chats(st.session_state.user_id)

        if chats:
            st.session_state.active_chat_id = chats[0][0]
        else:
            st.session_state.active_chat_id = create_chat(st.session_state.user_id)

        st.rerun()

    if st.session_state.get(f"rename_{chat_id}", False):
        new_title = st.sidebar.text_input(
            "Rename",
            value=title,
            key=f"rename_input_{chat_id}"
        )

        if st.sidebar.button("Save", key=f"save_{chat_id}"):
            rename_chat(chat_id, new_title)
            st.session_state[f"rename_{chat_id}"] = False
            st.rerun()


# ---------------- MAIN ----------------

st.title("🩺 AI Medical Copilot")

module = st.sidebar.radio(
    "Choose Module",
    [
        "AI Chatbot",
        "Optional Report Analysis",
        "Food Tracker",
        "Prescription & Reminders",
        "Symptom Checker",
        "Live Health Tracking"
    ]
)


# ---------------- CHATBOT ----------------

if module == "AI Chatbot":
    st.header("💬 AI Healthcare Chatbot")

    messages = get_messages(st.session_state.active_chat_id)

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask anything about your health...")

    if user_input:
        add_message(st.session_state.active_chat_id, "user", user_input)

        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = f"""
You are a personalized AI Medical Copilot.

User:
{st.session_state.username}

Previous conversation:
{messages}

Question:
{user_input}

Give safe, helpful healthcare guidance. Do not diagnose.
"""

        with st.chat_message("assistant"):
            answer = call_ai(prompt)
            st.markdown(answer)

        add_message(st.session_state.active_chat_id, "assistant", answer)


# ---------------- REPORT ----------------

elif module == "Optional Report Analysis":
    st.header("📄 Optional Medical Report Analysis")

    uploaded = st.file_uploader(
        "Upload report only if needed",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded:
        text = read_uploaded_file(uploaded)
        st.session_state.report_text = text

        st.subheader("Extracted Report")
        st.text_area("Report Text", text, height=250)

        score = calculate_health_score(text)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Health Score", f"{score}/100")

        with col2:
            st.metric("Risk", "Low" if score >= 80 else "Moderate" if score >= 60 else "High")

        with col3:
            st.metric("Status", "Processed")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Health Score"},
            gauge={"axis": {"range": [0, 100]}}
        ))

        st.plotly_chart(fig, use_container_width=True)

        findings = detect_abnormal_values(text)

        st.subheader("Smart Medical Insights")

        if findings:
            for item in findings:
                st.warning(f"{item['test']} = {item['value']} → {item['message']}")
        else:
            st.success("No major abnormal value detected")

        st.subheader("Possible Conditions")

        for condition in predict_possible_conditions(text):
            st.info(condition)

        st.subheader("Medicine Safety")

        for warning in check_medicine_safety(text):
            st.info(warning)

        with st.expander("Optional: Compare with previous report"):
            old = st.file_uploader(
                "Upload previous report",
                type=["pdf", "png", "jpg", "jpeg"],
                key="old_report"
            )

            if old and st.button("Compare Reports"):
                old_text = read_uploaded_file(old)
                result = compare_reports(old_text, text)
                st.markdown(result)

        if st.button("Analyze Report with AI"):
            analysis = call_ai(report_analysis_prompt(text), max_tokens=1800)

            save_report(
                st.session_state.user_id,
                st.session_state.active_chat_id,
                text,
                analysis
            )


            rename_chat(
                st.session_state.active_chat_id,
                "Medical Report Analysis"
            )

            st.subheader("AI Medical Analysis")
            st.markdown(analysis)

            pdf_path = generate_pdf_report(analysis)

            with open(pdf_path, "rb") as file:
                st.download_button(
                    "Download PDF",
                    file,
                    file_name="AI_Healthcare_Report.pdf"
                )


# ---------------- FOOD ----------------

elif module == "Food Tracker":
    st.header("🍱 Daily Food Tracker")

    food = st.text_area("What did you eat today?")

    if st.button("Analyze Food"):
        if not food.strip():
            st.error("Please enter what you ate.")
        else:
            with st.spinner("Analyzing your food..."):
                feedback = analyze_food(food)

            st.markdown(feedback)

            save_food_log(
                st.session_state.user_id,
                food,
                feedback
            )

    st.subheader("Recent Food Logs")

    for food, feedback, created_at in get_food_logs(st.session_state.user_id):
        with st.expander(created_at):
            st.write(food)
            st.markdown(feedback)


# ---------------- PRESCRIPTION ----------------

elif module == "Prescription & Reminders":
    st.header("💊 Prescription Reader & Medicine Reminder")

    prescription = st.file_uploader(
        "Upload typed or handwritten prescription",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if prescription:
        extracted = read_uploaded_file(prescription)

        st.text_area("Extracted Prescription", extracted, height=220)

        if st.button("Analyze Prescription"):
            result = call_ai(prescription_prompt(extracted))
            st.markdown(result)

    st.subheader("Add Medicine Reminder")

    med = st.text_input("Medicine")
    dosage = st.text_input("Dosage")
    timing = st.text_input("Timing")

    if st.button("Save Reminder"):
        add_reminder(
            st.session_state.user_id,
            med,
            dosage,
            timing
        )
        st.success("Reminder saved")

    st.subheader("Your Reminders")

    for medicine, dosage, timing, status in get_reminders(st.session_state.user_id):
        st.info(f"{medicine} | {dosage} | {timing} | {status}")


# ---------------- SYMPTOM ----------------

elif module == "Symptom Checker":
    st.header("🧠 AI Symptom Checker")

    symptoms = st.text_area("Enter your symptoms")

    if st.button("Check Symptoms"):
        if not symptoms.strip():
            st.error("Please enter symptoms.")
        else:
            from src.symptom_checker import check_symptoms

            with st.spinner("Checking symptoms..."):
                result = check_symptoms(symptoms)

            st.markdown(result)


# ---------------- HEALTH TRACKING ----------------

elif module == "Live Health Tracking":
    st.header("📊 Live Health Tracking")

    col1, col2 = st.columns(2)

    with col1:
        bp = st.text_input("BP")
        sugar = st.text_input("Sugar")
        weight = st.text_input("Weight")

    with col2:
        sleep = st.text_input("Sleep hours")
        water = st.text_input("Water intake")
        steps = st.text_input("Steps")

    if st.button("Save Health Log"):
        save_health_log(
            st.session_state.user_id,
            bp,
            sugar,
            weight,
            sleep,
            water,
            steps
        )
        st.success("Saved")

    logs = get_health_logs(st.session_state.user_id)

    if logs:
        df = build_health_dataframe(logs)
        st.dataframe(df)

        if df["Sugar"].notna().any():
            st.plotly_chart(create_trend_chart(df, "Sugar"), use_container_width=True)

        if df["Weight"].notna().any():
            st.plotly_chart(create_trend_chart(df, "Weight"), use_container_width=True)