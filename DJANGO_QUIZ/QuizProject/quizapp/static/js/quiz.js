// Common Quiz Functionality
let quizData = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let startTime;
let timerInterval;

// Show a specific question
function showQuestion(index) {
    if (index < 0 || index >= quizData.length) return;
    
    currentQuestionIndex = index;
    const question = quizData[index];
    
    questionContainer.innerHTML = '';
    
    const questionCard = document.createElement('div');
    questionCard.className = 'question-card';
    
    questionCard.innerHTML = `
        <div class="question-number">Question ${index + 1} of ${quizData.length}</div>
        <div class="question-text">${question.question}</div>
        <div class="options"></div>
    `;
    
    const optionsContainer = questionCard.querySelector('.options');
    
    question.options.forEach((option, optionIndex) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        if (userAnswers[index] === optionIndex) {
            optionDiv.classList.add('selected');
        }
        
        optionDiv.innerHTML = `
            <span class="radio-custom"></span>
            <span>${option}</span>
        `;
        
        optionDiv.addEventListener('click', () => {
            selectAnswer(optionIndex);
        });
        
        optionsContainer.appendChild(optionDiv);
    });
    
    questionContainer.appendChild(questionCard);
    updateProgress();
    updateNavButtons();
}

// Select an answer
function selectAnswer(optionIndex) {
    userAnswers[currentQuestionIndex] = optionIndex;
    
    const options = document.querySelectorAll('.option');
    options.forEach(option => option.classList.remove('selected'));
    options[optionIndex].classList.add('selected');
}

// Show the previous question
function showPrevQuestion() {
    if (currentQuestionIndex > 0) {
        showQuestion(currentQuestionIndex - 1);
    }
}

// Show the next question or finish quiz
function showNextQuestion() {
    if (currentQuestionIndex < quizData.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    } else {
        finishQuiz();
    }
}

// Update progress bar and text
function updateProgress() {
    const progress = ((currentQuestionIndex + 1) / quizData.length) * 100;
    progressFill.style.width = `${progress}%`;
    currentQuestionText.textContent = `Question ${currentQuestionIndex + 1} of ${quizData.length}`;
}

// Update navigation buttons
function updateNavButtons() {
    prevBtn.disabled = currentQuestionIndex === 0;
    
    if (currentQuestionIndex === quizData.length - 1) {
        nextBtn.textContent = 'Finish Quiz';
    } else {
        nextBtn.textContent = 'Next';
    }
}

// Start the timer
function startTimer() {
    startTime = new Date();
    clearInterval(timerInterval);
    timerInterval = setInterval(updateTimer, 1000);
}

// Update the timer display
function updateTimer() {
    const now = new Date();
    const elapsed = Math.floor((now - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');
    timeElapsed.textContent = `${minutes}:${seconds}`;
}

// Finish the quiz and show results
function finishQuiz() {
    clearInterval(timerInterval);
    
    quizContainer.style.display = 'none';
    resultContainer.style.display = 'block';
    
    // Calculate results
    let numCorrect = 0;
    userAnswers.forEach((answer, index) => {
        if (answer === quizData[index].correctAnswer) {
            numCorrect++;
        }
    });
    
    const score = Math.round((numCorrect / quizData.length) * 100);
    
    scoreDisplay.textContent = `${score}%`;
    correctAnswers.textContent = numCorrect;
    totalQuestions.textContent = quizData.length;
    
    // Change color based on score
    const scoreCircle = document.querySelector('.score-circle');
    if (score >= 80) {
        scoreCircle.style.background = 'linear-gradient(135deg, var(--success), var(--secondary))';
    } else if (score >= 60) {
        scoreCircle.style.background = 'linear-gradient(135deg, var(--warning), var(--secondary))';
    } else {
        scoreCircle.style.background = 'linear-gradient(135deg, var(--danger), var(--primary))';
    }
}

// Helper function to shuffle an array
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

// Helper function to decode HTML entities
function decodeHTML(html) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = html;
    return textarea.value;
}