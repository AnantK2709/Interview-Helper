from typing import List, Dict, Any
import random

class QuestionService:
    def __init__(self):
        # Basic questions to start with before implementing LLAMA
        self.basic_questions = {
            "beginner": [
                "Tell me about yourself.",
                "What are your strengths and weaknesses?",
                "Why do you want to work for this company?",
                "Where do you see yourself in 5 years?",
                "Describe a challenging situation you faced at work and how you handled it."
            ],
            "intermediate": [
                "Tell me about a time when you had to work with a difficult team member.",
                "How do you handle stress and pressure?",
                "What are your salary expectations?",
                "Why should we hire you?",
                "What is your leadership style?"
            ],
            "advanced": [
                "Describe a situation where you had to make an unpopular decision.",
                "How do you stay motivated in your work?",
                "Tell me about a time when you failed and what you learned from it.",
                "How do you prioritize your work when dealing with multiple deadlines?",
                "What questions do you have for me about the role or company?"
            ]
        }
    
    def get_random_question(self, difficulty: str = "beginner") -> Dict[str, Any]:
        """Get a random question based on difficulty level."""
        if difficulty not in self.basic_questions:
            difficulty = "beginner"
        
        questions = self.basic_questions[difficulty]
        question = random.choice(questions)
        
        return {
            "question": question,
            "difficulty": difficulty
        }
    
    def get_questions_by_category(self, category: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get multiple questions by category."""
        questions = []
        for difficulty in self.basic_questions:
            for _ in range(count // 3 + (count % 3 if difficulty == "beginner" else 0)):
                questions.append(self.get_random_question(difficulty))
        
        return questions[:count]