import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import random # Import random for the cache seed

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Trivia Game", page_icon="🎮", layout="centered")

st.title("🎮 Trivia Game")
st.write("Test your knowledge with AI-generated questions!")

# ---------------- Sidebar ----------------
st.sidebar.header("⚙ Game Options")

topic = st.sidebar.selectbox(
    "Select Topic",
    ["General Knowledge", "Movies", "Sports", "Technology", "Science", "History", "Custom Topic"],
    index=None
)

if topic == "Custom Topic":
    topic = st.sidebar.text_input("Enter any custom topic")

difficulty = st.sidebar.radio("Difficulty", ["Easy", "Medium", "Hard"], index=None)
num_questions = st.sidebar.slider("Number of Questions", 3, 10)

start = st.sidebar.button("Start Game")

# ---------- Generate Questions from AI ----------
# Added 'seed' parameter to prevent getting the same cached results
@st.cache_data(show_spinner=True)
def generate_questions(topic, difficulty, num_questions, seed):
    prompt = f"""
    Generate {num_questions} multiple-choice trivia questions about '{topic}'.
    Difficulty: {difficulty}.

    OUTPUT RULES:
    - Output ONLY a JSON array.
    - Each question must follow the EXACT structure below.
    - FORMAT:
    [
      {{
        "question": "string",
        "options": ["option1", "option2", "option3", "option4"],
        "correct": "one of the options",
        "explanation": "short explanation"
      }}
    ]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_text = response.choices[0].message.content.strip()

    try:
        # Standard cleaning to remove potential markdown code blocks
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "").replace("```", "")
        return json.loads(ai_text)
    except Exception as e:
        st.error("⚠ AI returned invalid JSON.")
        return []

# ---------- Start/Reset Logic ----------
if start and topic and difficulty:
    # 1. Clear previous game state
    if "questions" in st.session_state:
        del st.session_state["questions"]
    
    # 2. Generate new questions with a random seed to bypass cache
    random_seed = random.randint(1, 10000)
    st.session_state["questions"] = generate_questions(topic, difficulty, num_questions, random_seed)
    st.session_state["index"] = 0
    st.session_state["score"] = 0
    st.session_state["answered"] = False # Track if current question is answered
    st.rerun()

# ---------- Game UI ----------
if "questions" in st.session_state and st.session_state["questions"]:
    q_index = st.session_state["index"]
    questions = st.session_state["questions"]

    if q_index < len(questions):
        q = questions[q_index]

        st.subheader(f"Question {q_index+1} of {len(questions)}")
        st.write(q["question"])

        # We use a key based on the index to reset the radio button every question
        user_answer = st.radio("Select your answer:", q["options"], index=None, key=f"q_{q_index}")

        if st.button("Submit Answer") and user_answer and not st.session_state.get("answered"):
            st.session_state["answered"] = True
            
            if user_answer.strip().lower() == q["correct"].strip().lower():
                st.success("Correct! 🎉")
                st.session_state["score"] += 1
            else:
                st.error(f"Wrong! The correct answer was: {q['correct']}")
                st.info(f"💡 {q['explanation']}")

        # Only show "Next" if they have answered
        if st.session_state.get("answered"):
            if st.button("Next Question"):
                st.session_state["index"] += 1
                st.session_state["answered"] = False
                st.rerun()

    else:
        st.success("🎉 Game Over!")
        st.subheader(f"Your Final Score: {st.session_state['score']} / {len(questions)}")
        
        if st.session_state['score'] == len(questions):
            st.balloons()

        # FIXED PLAY AGAIN
        if st.button("Play Again"):
            # Clear the specific game keys
            keys_to_reset = ["questions", "index", "score", "answered"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Clear the AI cache to ensure NEW questions next time
            st.cache_data.clear()
            
            # Force a rerun to show the "Start Game" screen
            st.rerun()

else:
    # This shows when the game hasn't started or was just reset
    st.info("👈 Select your options in the sidebar and click 'Start Game' to begin!")