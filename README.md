# 🎮 AI Trivia Game

An interactive **AI-powered Trivia Game** built using **Streamlit** and **OpenAI**.  
The application dynamically generates multiple-choice quiz questions based on selected topics and difficulty levels, providing an engaging and personalized quiz experience.

This project demonstrates **API integration**, **prompt engineering**, **state management**, and **interactive UI development** using Python.

---

## 🚀 Features

- 🧠 AI-generated trivia questions
- 🎯 Multiple topics:
  - General Knowledge
  - Movies
  - Sports
  - Technology
  - Science
  - History
  - Custom Topic
- ⚙ Difficulty levels: Easy, Medium, Hard
- 🔢 Configurable number of questions (3–10)
- 📊 Real-time score tracking
- ✅ Instant answer feedback with explanations
- 🎉 Balloons celebration for perfect score
- 🔁 Play Again functionality
- ⚡ Fast UI using Streamlit caching

---

## 🛠 Tech Stack

- **Python**
- **Streamlit** – Interactive web UI
- **OpenAI API** – AI-powered question generation
- **GPT-4o-mini** – Trivia generation model
- **python-dotenv** – Environment variable management

---

## 📂 Project Structure
ai-trivia-game/
│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
└── README.md # Project documentation



---

## ⚙ How It Works

1. User selects:
   - Topic
   - Difficulty
   - Number of questions
2. The app sends a structured prompt to OpenAI.
3. AI returns questions in **strict JSON format**.
4. Questions are cached using `st.cache_data`.
5. Player answers each question:
   - Immediate correctness feedback
   - Explanation shown
6. Final score displayed at the end of the game.

---

## ▶️ Run Locally

pip install -r requirements.txt
streamlit run app.py

