import streamlit as st
import google.generativeai as genai
import json
import re

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCPMGvTVUsZPgGC3jM9Wa9Ykj7GLXYreNA")  

# Load Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Page Config
st.set_page_config(page_title="Python MCQ Quiz", page_icon="🐍", layout="centered")

# Initialize session state
for key in ["mcqs", "current_q", "score", "topic_entered", "mode", "answers"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["mcqs", "answers"] else 0 if key in ["current_q", "score"] else False if key == "topic_entered" else None

# Function to clean and parse JSON from Gemini
def clean_json_response(response_text):
    cleaned = re.sub(r"```(?:json)?", "", response_text).strip()
    return json.loads(cleaned)

# Function to generate MCQs
def generate_mcqs(topic):
    prompt = f"""
Generate exactly 20 Python MCQs on the topic: '{topic}'.
Format response as raw JSON:
[{{"question": "What does 'len()' do?", "options": {{"A": "Adds numbers", "B": "Returns length", "C": "Deletes variable", "D": "Loops over list"}}, "answer": "B", "explanation": "The len() function returns the number of items in an object."}}]
Only return JSON. Do not include markdown or text outside the JSON.
"""
    try:
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        st.error(f"❌ Error parsing MCQs: {e}")
        st.code(response.text, language="markdown")
        return []

# UI: Title and Input
st.title("🐍 Python MCQ Quiz Generator")

if not st.session_state.topic_entered:
    topic = st.text_input("🎯 Enter a Python topic:", placeholder="e.g., Loops, Lists, Functions")
    if st.button("🚀 Start Quiz"):
        with st.spinner("Generating Quiz..."):
            mcqs = generate_mcqs(topic)
            if mcqs:
                st.session_state.mcqs = mcqs
                st.session_state.topic_entered = True
                st.session_state.mode = "quiz"
                st.rerun()
else:
    mcqs = st.session_state.mcqs
    current_q = st.session_state.current_q
    mode = st.session_state.mode

    if mode == "quiz":
        if current_q < len(mcqs):
            q = mcqs[current_q]
            st.subheader(f"Question {current_q + 1} of {len(mcqs)}")
            st.write(q["question"])

            options = q["options"]
            selected = st.radio("Select an answer:", list(options.keys()), format_func=lambda x: f"{x}: {options[x]}")

            if st.button("Submit"):
                correct_answer = q["answer"]
                if selected == correct_answer:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                    st.session_state.answers.append({"question": q["question"], "correct": True})
                else:
                    st.error(f"❌ Incorrect. Correct answer is {correct_answer}: {options[correct_answer]}")
                    st.session_state.answers.append({
                        "question": q["question"],
                        "correct": False,
                        "your_answer": selected,
                        "correct_answer": correct_answer,
                        "explanation": q.get("explanation", "No explanation available.")
                    })
                st.session_state.current_q += 1
                st.rerun()
        else:
            st.success("🎉 Quiz Completed!")
            st.markdown(f"### 🏆 Your Score: **{st.session_state.score} / {len(mcqs)}**")
            incorrects = [a for a in st.session_state.answers if not a["correct"]]
            if incorrects:
                st.markdown("### ❌ Review Incorrect Answers:")
                for i, wrong in enumerate(incorrects, 1):
                    st.markdown(f"**{i}. {wrong['question']}**")
                    st.markdown(f"Your Answer: {wrong['your_answer']} ❌")
                    st.markdown(f"Correct Answer: {wrong['correct_answer']} ✅")
                    st.markdown(f"💡 Explanation: {wrong['explanation']}")
                    st.markdown("---")
            else:
                st.markdown("🎯 Amazing! All answers correct!")

            if st.button("🔁 Restart"):
                for key in ["mcqs", "current_q", "score", "topic_entered", "mode", "answers"]:
                    del st.session_state[key]
                st.rerun()
