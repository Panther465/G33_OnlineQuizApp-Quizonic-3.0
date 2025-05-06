// Create Own Quiz Specific JavaScript

let numberOfQuestions = 2;

// DOM Elements
const customQuizBuilder = document.getElementById('customQuizBuilder');
const loadingContainer = document.getElementById('loadingContainer');
const quizContainer = document.getElementById('quizContainer');
const resultContainer = document.getElementById('resultContainer');
const questionContainer = document.getElementById('questionContainer');
const progressFill = document.getElementById('progressFill');
const currentQuestionText = document.getElementById('currentQuestionText');
const timeElapsed = document.getElementById('timeElapsed');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const reviewBtn = document.getElementById('reviewBtn');
const newQuizBtn = document.getElementById('newQuizBtn');
const displayQuizTitle = document.getElementById('displayQuizTitle');
const displaySubject = document.getElementById('displaySubject');
const displayNumQuestions = document.getElementById('displayNumQuestions');
const scoreDisplay = document.getElementById('scoreDisplay');
const correctAnswers = document.getElementById('correctAnswers');
const totalQuestions = document.getElementById('totalQuestions');
const generateQuestionsBtn = document.getElementById('generateQuestionsBtn');
const startCustomQuizBtn = document.getElementById('startCustomQuizBtn');

// Event Listeners
prevBtn.addEventListener('click', showPrevQuestion);
nextBtn.addEventListener('click', showNextQuestion);
reviewBtn.addEventListener('click', reviewQuiz);
newQuizBtn.addEventListener('click', resetQuiz);
generateQuestionsBtn.addEventListener('click', generateQuestionForms);
startCustomQuizBtn.addEventListener('click', startCustomQuiz);

document.getElementById('customNumQuestions').addEventListener('change', function() {
    numberOfQuestions = parseInt(this.value);
});

function init() {
    customQuizBuilder.style.display = 'block';
    loadingContainer.style.display = 'none';
    quizContainer.style.display = 'none';
    resultContainer.style.display = 'none';
}

// Custom Quiz Functions
function generateQuestionForms() {
    const container = document.getElementById('dynamicQuestionsContainer');
    container.innerHTML = '';
    
    for(let i = 0; i < numberOfQuestions; i++) {
        const questionHTML = `
            <div class="custom-question-form" data-index="${i}">
                <h3>Question ${i + 1}</h3>
                <div class="form-group">
                    <label>Question Text</label>
                    <textarea class="question-input" rows="2" placeholder="Enter question" required></textarea>
                </div>
                <div class="form-group">
                    <label>Options (select correct answer)</label>
                    ${Array.from({length: 4}, (_, j) => `
                        <div class="option-group">
                            <div class="correct-toggle" data-question="${i}" data-option="${j}"></div>
                            <input type="text" class="option-input" placeholder="Option ${j + 1}" required>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', questionHTML);
    }

    document.querySelectorAll('.correct-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const questionIndex = parseInt(this.dataset.question);
            const optionIndex = parseInt(this.dataset.option);
            
            document.querySelectorAll(`[data-question="${questionIndex}"]`).forEach(t => {
                t.classList.remove('selected');
            });
            
            this.classList.add('selected');
        });
    });

    startCustomQuizBtn.disabled = false;
}

function startCustomQuiz() {
    const title = document.getElementById('customQuizTitle').value;
    const subject = document.getElementById('customQuizSubject').value;
    
    if (!title || !subject) {
        alert('Please fill in quiz title and subject');
        return;
    }

    quizData = [];
    const questionForms = document.querySelectorAll('.custom-question-form');
    
    questionForms.forEach((form, index) => {
        const questionText = form.querySelector('.question-input').value.trim();
        const options = Array.from(form.querySelectorAll('.option-input')).map(input => input.value.trim());
        const correctToggle = form.querySelector('.correct-toggle.selected');
        
        if (!questionText || options.some(opt => !opt) || !correctToggle) {
            alert(`Please complete all fields for Question ${index + 1}`);
            return;
        }

        const correctAnswer = parseInt(correctToggle.dataset.option);
        
        quizData.push({
            question: questionText,
            options: options,
            correctAnswer: correctAnswer
        });
    });

    if (quizData.length !== numberOfQuestions) {
        alert('Please complete all questions properly');
        return;
    }

    // Hide the custom quiz builder when starting the quiz
    customQuizBuilder.style.display = 'none';
    
    userAnswers = new Array(quizData.length).fill(null);
    displayQuiz(title, subject, quizData.length);
    startTimer();
    document.getElementById('quizContainer').scrollIntoView({ behavior: 'smooth' });
}

function displayQuiz(title, subject, numQuestions) {
    displayQuizTitle.textContent = title;
    displaySubject.textContent = subject;
    displayNumQuestions.textContent = numQuestions;
    
    loadingContainer.style.display = 'none';
    quizContainer.style.display = 'block';
    
    currentQuestionIndex = 0;
    showQuestion(currentQuestionIndex);
    updateProgress();
}

function reviewQuiz() {
    let reviewHTML = '';
    
    quizData.forEach((question, index) => {
        const userAnswer = userAnswers[index];
        const isCorrect = userAnswer === question.correctAnswer;
        
        reviewHTML += `
            <div class="question-card" style="border-left: 4px solid ${isCorrect ? 'var(--success)' : 'var(--danger)'}">
                <div class="question-number">Question ${index + 1}</div>
                <div class="question-text">${question.question}</div>
                <div class="options">
        `;
        
        question.options.forEach((option, i) => {
            const isUserAnswer = userAnswer === i;
            const isCorrectAnswer = question.correctAnswer === i;
            
            let optionClass = '';
            if (isUserAnswer && isCorrectAnswer) {
                optionClass = 'selected';
            } else if (isUserAnswer) {
                optionClass = 'selected';
            } else if (isCorrectAnswer) {
                optionClass = 'selected';
            }
            
            reviewHTML += `
                <div class="option ${optionClass}" style="${isCorrectAnswer ? 'border-color: var(--success);' : ''}${isUserAnswer && !isCorrectAnswer ? 'border-color: var(--danger);' : ''}">
                    <div class="radio-custom" style="${isCorrectAnswer ? 'border-color: var(--success);' : ''}"></div>
                    ${option}
                    ${isCorrectAnswer ? ' <span style="margin-left: auto; color: var(--success);">✓ Correct</span>' : ''}
                    ${isUserAnswer && !isCorrectAnswer ? ' <span style="margin-left: auto; color: var(--danger);">✗ Your Answer</span>' : ''}
                </div>
            `;
        });
        
        reviewHTML += `</div></div>`;
    });
    
    resultContainer.style.display = 'none';
    questionContainer.innerHTML = reviewHTML;
    currentQuestionText.textContent = `Review: All Questions`;
    progressFill.style.width = '100%';
    nextBtn.style.display = 'none';
    prevBtn.style.display = 'none';
    quizContainer.style.display = 'block';
}

function resetQuiz() {
    init();
    quizData = [];
    userAnswers = [];
    currentQuestionIndex = 0;
    clearInterval(timerInterval);
}

// Initialize the app
init();