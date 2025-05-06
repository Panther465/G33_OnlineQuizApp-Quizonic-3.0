document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            "particles": {
                "number": {
                    "value": 80,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": ["#4a6bff", "#ff4a9e", "#28a745"]
                },
                "shape": {
                    "type": "circle",
                    "stroke": {
                        "width": 0,
                        "color": "#000000"
                    }
                },
                "opacity": {
                    "value": 0.5,
                    "random": true
                },
                "size": {
                    "value": 3,
                    "random": true
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#4a6bff",
                    "opacity": 0.4,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1,
                    "direction": "none",
                    "random": true,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "grab"
                    },
                    "onclick": {
                        "enable": true,
                        "mode": "push"
                    },
                    "resize": true
                }
            },
            "retina_detect": true
        });
    }
    
    // Simple 5-question quiz
    const quizQuestions = [
        {
            question: "What is the capital of Japan?",
            options: ["Beijing", "Seoul", "Tokyo", "Bangkok"],
            answer: 2
        },
        {
            question: "Which element has the chemical symbol 'O'?",
            options: ["Gold", "Oxygen", "Osmium", "Oganesson"],
            answer: 1
        },
        {
            question: "Who wrote 'Romeo and Juliet'?",
            options: ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
            answer: 1
        },
        {
            question: "What is the largest ocean on Earth?",
            options: ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            answer: 3
        },
        {
            question: "Which planet is closest to the Sun?",
            options: ["Venus", "Mars", "Mercury", "Earth"],
            answer: 2
        }
    ];
    
    // Quiz elements
    const quizContainer = document.getElementById('quiz-container');
    const quizQuestion = document.getElementById('quiz-question');
    const quizOptions = document.getElementById('quiz-options');
    const quizControls = document.getElementById('quiz-controls');
    const quizPrevBtn = document.getElementById('quiz-prev-btn');
    const quizNextBtn = document.getElementById('quiz-next-btn');
    const quizResults = document.getElementById('quiz-results');
    const quizScoreValue = document.getElementById('quiz-score-value');
    const quizResultTitle = document.getElementById('quiz-result-title');
    const quizResultText = document.getElementById('quiz-result-text');
    const quizRestartBtn = document.getElementById('quiz-restart-btn');
    
    // Quiz state
    let currentQuestion = 0;
    let userAnswers = [-1, -1, -1, -1, -1];
    
    // Initialize quiz
    function initQuiz() {
        // Display first question
        showQuestion(currentQuestion);
    }
    
    // Show current question
    function showQuestion(index) {
        const question = quizQuestions[index];
        quizQuestion.textContent = question.question;
        
        // Create options
        quizOptions.innerHTML = '';
        question.options.forEach((option, i) => {
            const optionElement = document.createElement('div');
            optionElement.className = `quiz-option ${userAnswers[index] === i ? 'selected' : ''}`;
            
            // Create marker
            const marker = document.createElement('div');
            marker.className = 'quiz-option-marker';
            optionElement.appendChild(marker);
            
            // Create option text
            const textSpan = document.createElement('span');
            textSpan.textContent = option;
            optionElement.appendChild(textSpan);
            
            optionElement.addEventListener('click', () => selectOption(i));
            quizOptions.appendChild(optionElement);
        });
        
        // Update button states
        quizPrevBtn.disabled = index === 0;
        
        if (index === quizQuestions.length - 1) {
            quizNextBtn.innerHTML = 'Finish <i class="fas fa-check"></i>';
        } else {
            quizNextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        }
    }
    
    // Select an option
    function selectOption(optionIndex) {
        userAnswers[currentQuestion] = optionIndex;
        
        // Update selected styling
        const options = quizOptions.querySelectorAll('.quiz-option');
        options.forEach((option, i) => {
            if (i === optionIndex) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }
    
    // Go to next question or finish quiz
    function nextQuestion() {
        if (currentQuestion < quizQuestions.length - 1) {
            currentQuestion++;
            showQuestion(currentQuestion);
        } else {
            showResults();
        }
    }
    
    // Go to previous question
    function prevQuestion() {
        if (currentQuestion > 0) {
            currentQuestion--;
            showQuestion(currentQuestion);
        }
    }
    
    // Show quiz results
    function showResults() {
        // Calculate score
        let correctAnswers = 0;
        userAnswers.forEach((answer, index) => {
            if (answer === quizQuestions[index].answer) {
                correctAnswers++;
            }
        });
        
        const scorePercentage = Math.round((correctAnswers / quizQuestions.length) * 100);
        
        // Update results display
        quizScoreValue.textContent = `${scorePercentage}%`;
        quizResultText.textContent = `You scored ${correctAnswers} out of ${quizQuestions.length} correct.`;
        
        // Set result title based on score
        if (scorePercentage >= 80) {
            quizResultTitle.textContent = 'Excellent!';
        } else if (scorePercentage >= 60) {
            quizResultTitle.textContent = 'Good Job!';
        } else if (scorePercentage >= 40) {
            quizResultTitle.textContent = 'Not Bad!';
        } else {
            quizResultTitle.textContent = 'Keep Practicing!';
        }
        
        // Show results, hide quiz
        quizContainer.style.display = 'none';
        quizControls.style.display = 'none';
        quizResults.style.display = 'block';
    }
    
    // Restart quiz
    function restartQuiz() {
        currentQuestion = 0;
        userAnswers = [-1, -1, -1, -1, -1];
        
        quizContainer.style.display = 'block';
        quizControls.style.display = 'flex';
        quizResults.style.display = 'none';
        
        showQuestion(currentQuestion);
    }
    
    // Event listeners
    quizNextBtn.addEventListener('click', nextQuestion);
    quizPrevBtn.addEventListener('click', prevQuestion);
    quizRestartBtn.addEventListener('click', restartQuiz);
    
    // Start the quiz
    initQuiz();
}); 