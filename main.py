
import openai
import os

# Load API key securely
openai.api_key = "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"


# STEM subject prompts
STEM_PROMPTS = {
    "math": "You are a mathematics tutor. Focus on explaining mathematical concepts clearly, showing step-by-step solutions, and providing practice problems when appropriate. Cover topics from algebra, calculus, statistics, and other mathematical fields.",
    "science": "You are a science tutor. Explain scientific concepts with real-world examples, break down complex processes, and relate topics to current scientific developments. Cover physics, chemistry, and biology concepts.",
    "tech": "You are a technology and computer science tutor. Provide clear explanations of programming concepts, include code examples when relevant, and explain technical concepts in an accessible way. Focus on practical applications.",
    "engineering": "You are an engineering tutor. Focus on applied mathematics, physics, and design principles. Explain engineering concepts with real-world examples and problem-solving approaches."
}

QUIZ_PROMPTS = {
    "math": "Generate a math quiz question appropriate for the current topic. Format: {'question': 'detailed question', 'correct_answer': 'answer', 'explanation': 'detailed explanation'}",
    "science": "Generate a science quiz question about fundamental concepts. Format: {'question': 'detailed question', 'correct_answer': 'answer', 'explanation': 'detailed explanation'}",
    "tech": "Generate a technology/programming quiz question. Format: {'question': 'detailed question', 'correct_answer': 'answer', 'explanation': 'detailed explanation'}",
    "engineering": "Generate an engineering quiz question. Format: {'question': 'detailed question', 'correct_answer': 'answer', 'explanation': 'detailed explanation'}"
}

import json

conversation_history = []
current_mode = "math"  # Default mode
is_quiz_mode = False
current_question = None
quiz_score = 0
total_questions = 0

def generate_quiz_question(mode):
    """
    Generates a quiz question for the current mode.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": QUIZ_PROMPTS[mode]},
                {"role": "user", "content": "Generate a question in valid JSON format with fields: question, correct_answer, and explanation"}
            ],
            temperature=0.7
        )
        content = response["choices"][0]["message"]["content"]
        # Clean the content string before parsing
        content = content.strip()
        if not content.startswith('{'): 
            content = content[content.find('{'):]
        if not content.endswith('}'): 
            content = content[:content.rfind('}')+1]
        question_data = json.loads(content)
        
        # Validate required fields
        required_fields = ["question", "correct_answer", "explanation"]
        if all(field in question_data for field in required_fields):
            return question_data
        else:
            print("Missing required fields in question data")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error generating question: {str(e)}")
        return None

def check_answer(user_answer, correct_answer):
    """
    Checks if the user's answer matches the correct answer.
    """
    return user_answer.lower().strip() == correct_answer.lower().strip()

def ask_stem_tutor(question, mode):
    """
    Sends the user's question to OpenAI's GPT model with STEM-specific context.
    """
    conversation_history.append({"role": "user", "content": question})
    
    messages = [
        {"role": "system", "content": STEM_PROMPTS[mode]},
        *conversation_history
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        ai_response = response["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        return f"Error: {str(e)}"

def change_mode(new_mode):
    """
    Changes the current STEM mode.
    """
    if new_mode in STEM_PROMPTS:
        global current_mode
        current_mode = new_mode
        conversation_history.clear()  # Clear history when changing modes
        return f"Switched to {new_mode} mode!"
    return "Invalid mode. Available modes: math, science, technology, engineering"

# Interactive loop
print("🎓 Welcome to the STEM AI Tutor!")
print("Commands:")
print("- 'mode <subject>' to change subject")
print("- 'quiz start' to start quiz mode")
print("- 'quiz stop' to stop quiz mode")
print("- 'exit' to quit")
print("Available modes: math, science, tech, engineering")
print(f"Current mode: {current_mode}")

while True:
    if is_quiz_mode and current_question is None:
        current_question = generate_quiz_question(current_mode)
        if current_question:
            print("\n📝 Quiz Question:", current_question["question"])
        else:
            print("Error generating question. Quiz mode disabled.")
            is_quiz_mode = False
            continue

    user_input = input("\nYour response: ").strip()
    
    if user_input.lower() == "exit":
        if total_questions > 0:
            print(f"\nFinal Score: {quiz_score}/{total_questions} ({(quiz_score/total_questions)*100:.1f}%)")
        print("Goodbye! Keep learning! 😊")
        break
    
    if user_input.lower().startswith("mode "):
        new_mode = user_input.split()[1].lower()
        print(change_mode(new_mode))
        is_quiz_mode = False
        current_question = None
        continue
    
    if user_input.lower() == "quiz start":
        is_quiz_mode = True
        quiz_score = 0
        total_questions = 0
        current_question = None
        print("📚 Quiz mode activated! Get ready for some questions!")
        continue
        
    if user_input.lower() == "quiz stop":
        is_quiz_mode = False
        if total_questions > 0:
            print(f"\nQuiz Results: {quiz_score}/{total_questions} ({(quiz_score/total_questions)*100:.1f}%)")
        current_question = None
        print("Quiz mode deactivated.")
        continue
    
    if is_quiz_mode and current_question:
        total_questions += 1
        if check_answer(user_input, current_question["correct_answer"]):
            quiz_score += 1
            print("✅ Correct!")
        else:
            print(f"❌ Incorrect. The correct answer was: {current_question['correct_answer']}")
        print("📖 Explanation:", current_question["explanation"])
        current_question = None
        continue
        
    answer = ask_stem_tutor(user_input, current_mode)
    print("\n🧑‍🏫 Tutor:", answer)
