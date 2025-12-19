import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
load_dotenv()

# ---------- OPENAI API KEY ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Trivia Game", page_icon="🎮", layout="centered")

st.title("🎮 Trivia Game")
st.write("Test your knowledge with AI-generated questions!")

# ---------------- Sidebar ----------------
st.sidebar.header("⚙ Game Options")

topic = st.sidebar.selectbox(
    "Select Topic",
    ["General Knowledge", "Movies", "Sports", "Technology", "Science", "History", "Custom Topic"],index=None
)

if topic == "Custom Topic":
    topic = st.sidebar.text_input("Enter any custom topic")

difficulty = st.sidebar.radio("Difficulty", ["Easy", "Medium", "Hard"],index = None)

num_questions = st.sidebar.slider("Number of Questions", 3, 10)

start = st.sidebar.button("Start Game")

# ---------- Generate Questions from AI ----------
@st.cache_data(show_spinner=True)
def generate_questions(topic, difficulty, num_questions):
    prompt = f"""

    Generate {num_questions} multiple-choice trivia questions about '{topic}'.
    Difficulty: {difficulty}.

    OUTPUT RULES:
    - Output ONLY a JSON array.
    - Each question must follow the EXACT structure below.
    - No markdown, no explanations outside the JSON.

    FORMAT:
    [
    {{
        "question": "string",
        "options": ["option1", "option2", "option3", "option4"],
        "correct": "one of the options",
        "explanation": "short explanation"
    }}
    ]

    IMPORTANT:
    - "options" MUST contain REAL answers (not A/B/C/D).
    - "correct" MUST be EXACT text from "options".
    - Shuffle options randomly.
    - Provide believable wrong options.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_text = response.choices[0].message.content.strip()


    try:
        data = json.loads(ai_text)
        return data

    except Exception as e:
        st.error("⚠ AI returned invalid JSON. Retrying...")
        st.write("Raw Output:", ai_text)
        return []


# ---------- Start Game ----------
if start and topic:
    st.session_state["questions"] = generate_questions(topic, difficulty, num_questions)
    st.session_state["index"] = 0
    st.session_state["score"] = 0

# ---------- Game UI ----------
if "questions" in st.session_state:
    q_index = st.session_state["index"]
    questions = st.session_state["questions"]

    if q_index < len(questions):
        q = questions[q_index]

        st.subheader(f"Question {q_index+1}")
        st.write(q["question"])

        options = q["options"]
        user_answer = st.radio("Select your answer:",options,index = None)

        if st.button("Submit Answer") and user_answer:
            selected_text = user_answer
            options = q.get("options", [])

            # Defensive: strip whitespace
            options = [opt.strip() for opt in options]
            selected_text = selected_text.strip()

            # Determine selected index (0-3). If option not found, set -1
            try:
                selected_index = options.index(selected_text)
            except ValueError:
                selected_index = -1

            # Normalize correct answer into an index (0-3) if possible
            correct_raw = q.get("correct")
            correct_index = None

            # If correct is an int (0-based index)
            if isinstance(correct_raw, int):
                correct_index = int(correct_raw)

            # If correct is a letter like "A" or "a"
            elif isinstance(correct_raw, str) and len(correct_raw.strip()) == 1 and correct_raw.strip().upper() in "ABCD":
                letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
                correct_index = letter_to_index[correct_raw.strip().upper()]

            # If correct is a text string, try to match to options
            elif isinstance(correct_raw, str):
                corr = correct_raw.strip()
                # if the correct text equals one of the options (case-insensitive), use that
                for i, opt in enumerate(options):
                    if opt.lower() == corr.lower():
                        correct_index = i
                        break

            # As a last resort, if we couldn't get an index, compare text directly (case-insensitive)
            is_correct = False
            if correct_index is not None and selected_index != -1:
                is_correct = (selected_index == correct_index)
            else:
                # fallback: compare normalized text
                if isinstance(correct_raw, str) and selected_text.lower() == correct_raw.strip().lower():
                    is_correct = True

            # Feedback + debug (hide debug in production)
            if is_correct:
                st.success("Correct! 🎉")
                st.session_state["score"] += 1
            else:
                # Helpful debug lines to print to the app - remove when done
                st.error("Wrong!")

                # If we have a correct_index, show the correct option text too
                if correct_index is not None and 0 <= correct_index < len(options):
                    st.info(f"The correct answer is: **{options[correct_index]}** (option {['A','B','C','D'][correct_index]})")
                    st.info(q.get("explanation"))
                else:
                    st.info(f"The correct answer is: **{correct_raw}**")

            st.session_state["index"] += 1
            if st.button("Next"):
                st.rerun()

    else:
        st.success("🎉 Game Over!")
        st.subheader(f"Your Final Score: {st.session_state['score']} / {len(questions)}")

        if st.session_state['score'] == len(questions):
            st.balloons()
