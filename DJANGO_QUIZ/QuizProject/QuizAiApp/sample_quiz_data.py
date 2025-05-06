"""
Sample quiz data to use as fallback when API generation fails
"""

SAMPLE_QUIZZES = {
    "general_knowledge": [
        {
            "question": "Which planet is known as the Red Planet?",
            "options": [
                "A. Earth",
                "B. Mars",
                "C. Venus",
                "D. Jupiter"
            ],
            "correct_answer": "B",
            "explanation": "Mars is called the Red Planet because of its reddish appearance due to iron oxide (rust) on its surface."
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options": [
                "A. Atlantic Ocean",
                "B. Indian Ocean",
                "C. Arctic Ocean",
                "D. Pacific Ocean"
            ],
            "correct_answer": "D",
            "explanation": "The Pacific Ocean is the largest and deepest ocean on Earth, covering more than 30% of the Earth's surface."
        },
        {
            "question": "Which of these elements has the chemical symbol 'Au'?",
            "options": [
                "A. Silver",
                "B. Aluminum",
                "C. Gold",
                "D. Copper"
            ],
            "correct_answer": "C",
            "explanation": "Gold's chemical symbol 'Au' comes from the Latin word 'aurum', meaning gold."
        },
        {
            "question": "Who painted the Mona Lisa?",
            "options": [
                "A. Vincent van Gogh",
                "B. Pablo Picasso",
                "C. Michelangelo",
                "D. Leonardo da Vinci"
            ],
            "correct_answer": "D",
            "explanation": "The Mona Lisa was painted by Leonardo da Vinci in the early 16th century."
        },
        {
            "question": "Which country is home to the kangaroo?",
            "options": [
                "A. New Zealand",
                "B. South Africa",
                "C. Australia",
                "D. Brazil"
            ],
            "correct_answer": "C",
            "explanation": "Kangaroos are native to Australia and are one of the country's most recognizable symbols."
        }
    ],
    "mathematics": [
        {
            "question": "What is the value of π (pi) to two decimal places?",
            "options": [
                "A. 3.14",
                "B. 3.41",
                "C. 3.12",
                "D. 3.16"
            ],
            "correct_answer": "A",
            "explanation": "Pi (π) is approximately equal to 3.14159..., so to two decimal places it's 3.14."
        },
        {
            "question": "What is the square root of 144?",
            "options": [
                "A. 12",
                "B. 14",
                "C. 10",
                "D. 16"
            ],
            "correct_answer": "A",
            "explanation": "The square root of 144 is 12, because 12² = 144."
        },
        {
            "question": "If x + y = 10 and x - y = 4, what is the value of x?",
            "options": [
                "A. 3",
                "B. 5",
                "C. 7",
                "D. 9"
            ],
            "correct_answer": "C",
            "explanation": "Solving the system of equations: From x - y = 4, we get x = 4 + y. Substituting into x + y = 10: (4 + y) + y = 10, so 4 + 2y = 10, thus 2y = 6, and y = 3. Therefore, x = 4 + 3 = 7."
        },
        {
            "question": "What is the area of a circle with radius 5 units?",
            "options": [
                "A. 25π square units",
                "B. 10π square units",
                "C. 5π square units",
                "D. 15π square units"
            ],
            "correct_answer": "A",
            "explanation": "The area of a circle is calculated using the formula A = πr², where r is the radius. So, A = π × 5² = 25π square units."
        },
        {
            "question": "What is the result of 3² + 4²?",
            "options": [
                "A. 49",
                "B. 25",
                "C. 24",
                "D. 25"
            ],
            "correct_answer": "D",
            "explanation": "3² + 4² = 9 + 16 = 25."
        }
    ],
    "science": [
        {
            "question": "What is the chemical formula for water?",
            "options": [
                "A. CO2",
                "B. H2O",
                "C. O2",
                "D. NaCl"
            ],
            "correct_answer": "B",
            "explanation": "Water has the chemical formula H2O, meaning each molecule consists of two hydrogen atoms bonded to one oxygen atom."
        },
        {
            "question": "Which of these is NOT a state of matter?",
            "options": [
                "A. Solid",
                "B. Liquid",
                "C. Energy",
                "D. Gas"
            ],
            "correct_answer": "C",
            "explanation": "The traditional states of matter are solid, liquid, and gas. Energy is not a state of matter but a property that matter can possess."
        },
        {
            "question": "Which scientist proposed the theory of evolution by natural selection?",
            "options": [
                "A. Isaac Newton",
                "B. Albert Einstein",
                "C. Charles Darwin",
                "D. Galileo Galilei"
            ],
            "correct_answer": "C",
            "explanation": "Charles Darwin proposed the theory of evolution by natural selection in his book 'On the Origin of Species' published in 1859."
        },
        {
            "question": "What is the closest planet to the Sun?",
            "options": [
                "A. Venus",
                "B. Earth",
                "C. Mars",
                "D. Mercury"
            ],
            "correct_answer": "D",
            "explanation": "Mercury is the closest planet to the Sun in our solar system."
        },
        {
            "question": "What is the basic unit of life?",
            "options": [
                "A. Atom",
                "B. Cell",
                "C. Tissue",
                "D. Molecule"
            ],
            "correct_answer": "B",
            "explanation": "The cell is considered the basic unit of life as all living organisms are composed of one or more cells."
        }
    ],
    "history": [
        {
            "question": "In which year did World War II end?",
            "options": [
                "A. 1943",
                "B. 1945",
                "C. 1947",
                "D. 1950"
            ],
            "correct_answer": "B",
            "explanation": "World War II ended in 1945 with the surrender of Germany in May and Japan in September."
        },
        {
            "question": "Who was the first President of the United States?",
            "options": [
                "A. Thomas Jefferson",
                "B. John Adams",
                "C. George Washington",
                "D. Abraham Lincoln"
            ],
            "correct_answer": "C",
            "explanation": "George Washington served as the first President of the United States from 1789 to 1797."
        },
        {
            "question": "Which ancient civilization built the pyramids at Giza?",
            "options": [
                "A. Roman",
                "B. Greek",
                "C. Mayan",
                "D. Egyptian"
            ],
            "correct_answer": "D",
            "explanation": "The ancient Egyptians built the pyramids at Giza around 4,500 years ago."
        },
        {
            "question": "Who painted the Sistine Chapel ceiling?",
            "options": [
                "A. Leonardo da Vinci",
                "B. Raphael",
                "C. Michelangelo",
                "D. Donatello"
            ],
            "correct_answer": "C",
            "explanation": "Michelangelo painted the ceiling of the Sistine Chapel in Vatican City between 1508 and 1512."
        },
        {
            "question": "The Renaissance period originated in which country?",
            "options": [
                "A. France",
                "B. England",
                "C. Spain",
                "D. Italy"
            ],
            "correct_answer": "D",
            "explanation": "The Renaissance period began in Italy in the 14th century before spreading to the rest of Europe."
        }
    ]
}

def get_sample_quiz(topic=None, num_questions=5):
    """
    Get a sample quiz based on topic, or a general knowledge quiz if no matching topic is found.
    
    Args:
        topic (str): The quiz topic
        num_questions (int): Number of questions to include (max 5)
    
    Returns:
        list: A list of question dictionaries
    """
    # Map common topic keywords to our available quizzes
    topic_map = {
        "math": "mathematics",
        "mathematics": "mathematics",
        "algebra": "mathematics",
        "arithmetic": "mathematics",
        "calculus": "mathematics",
        "geometry": "mathematics",
        
        "science": "science",
        "biology": "science",
        "chemistry": "science",
        "physics": "science",
        "astronomy": "science",
        
        "history": "history",
        "world history": "history",
        "american history": "history",
        "ancient history": "history",
        
        "general": "general_knowledge",
        "general knowledge": "general_knowledge",
        "trivia": "general_knowledge"
    }
    
    # Find the appropriate quiz
    if topic:
        topic_lower = topic.lower()
        for key, value in topic_map.items():
            if key in topic_lower:
                quiz_key = value
                break
        else:
            quiz_key = "general_knowledge"
    else:
        quiz_key = "general_knowledge"
    
    # Get the quiz and limit number of questions
    quiz = SAMPLE_QUIZZES.get(quiz_key, SAMPLE_QUIZZES["general_knowledge"])
    
    # Ensure num_questions is within bounds
    if num_questions < 1:
        num_questions = 1
    if num_questions > len(quiz):
        num_questions = len(quiz)
    
    return quiz[:num_questions] 