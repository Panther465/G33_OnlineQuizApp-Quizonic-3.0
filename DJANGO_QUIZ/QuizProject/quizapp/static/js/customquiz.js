// Custom Quiz Generator with API Specific JavaScript

// Global variables
let quizData = [];
let userAnswers = [];
let currentQuestionIndex = 0;
let timerInterval;
let startTime;

// DOM Elements
const setupForm = document.getElementById('setupForm');
const loadingContainer = document.getElementById('loadingContainer');
const quizContainer = document.getElementById('quizContainer');
const resultContainer = document.getElementById('resultContainer');
const questionContainer = document.getElementById('questionContainer');
const progressFill = document.getElementById('progressFill');
const currentQuestionText = document.getElementById('currentQuestionText');
const timeElapsed = document.getElementById('timeElapsed');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const createQuizBtn = document.getElementById('createQuizBtn');
const reviewBtn = document.getElementById('reviewBtn');
const newQuizBtn = document.getElementById('newQuizBtn');
const displayQuizTitle = document.getElementById('displayQuizTitle');
const displayCategory = document.getElementById('displayCategory');
const displayDifficulty = document.getElementById('displayDifficulty');
const displayNumQuestions = document.getElementById('displayNumQuestions');
const scoreDisplay = document.getElementById('scoreDisplay');
const correctAnswers = document.getElementById('correctAnswers');
const totalQuestions = document.getElementById('totalQuestions');
const categorySelect = document.getElementById('quizCategory');
const difficultyBtns = document.querySelectorAll('.difficulty-btn');
const difficultyInput = document.getElementById('quizDifficulty');

let triviaCategories = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', fetchCategories);
createQuizBtn.addEventListener('click', generateQuiz);
prevBtn.addEventListener('click', showPrevQuestion);
nextBtn.addEventListener('click', showNextQuestion);
reviewBtn.addEventListener('click', reviewQuiz);
newQuizBtn.addEventListener('click', resetQuiz);

difficultyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        difficultyBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        difficultyInput.value = btn.dataset.difficulty;
    });
});

// Initialize the app
function init() {
    setupForm.style.display = 'block';
    loadingContainer.style.display = 'none';
    quizContainer.style.display = 'none';
    resultContainer.style.display = 'none';
}

// Fetch categories from the API
async function fetchCategories() {
    try {
        const response = await fetch('https://opentdb.com/api_category.php');
        const data = await response.json();
        triviaCategories = data.trivia_categories;
        
        // Populate category dropdown
        triviaCategories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching categories:', error);
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Failed to load categories. Please try again later.';
        setupForm.insertBefore(errorMsg, createQuizBtn.parentNode);
    }
}

// Generate quiz using the API
async function generateQuiz() {
    const title = document.getElementById('quizTitle').value;
    const category = document.getElementById('quizCategory').value;
    const difficulty = document.getElementById('quizDifficulty').value;
    const numQuestions = parseInt(document.getElementById('numQuestions').value);
    
    if (!title) {
        alert('Please enter a quiz title');
        return;
    }
    
    setupForm.style.display = 'none';
    loadingContainer.style.display = 'block';
    
    try {
        await fetchQuizData(category, difficulty, numQuestions);
        
        // Get category and difficulty display names
        let categoryName = 'Any Category';
        if (category) {
            const categoryObj = triviaCategories.find(c => c.id == category);
            if (categoryObj) categoryName = categoryObj.name;
        }
        
        let difficultyName = 'Any Difficulty';
        if (difficulty) {
            difficultyName = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
        }
        
        displayQuiz(title, categoryName, difficultyName, numQuestions);
        startTimer();
    } catch (error) {
        loadingContainer.style.display = 'none';
        setupForm.style.display = 'block';
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Failed to generate quiz. Please try again later.';
        setupForm.insertBefore(errorMsg, createQuizBtn.parentNode);
        
        console.error('Error generating quiz:', error);
    }
}

// Fetch quiz data from the Open Trivia Database API
async function fetchQuizData(category, difficulty, numQuestions) {
    let url = `https://opentdb.com/api.php?amount=${numQuestions}&type=multiple`;
    
    if (category) url += `&category=${category}`;
    if (difficulty) url += `&difficulty=${difficulty}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.response_code !== 0) {
        throw new Error('Failed to fetch questions');
    }
    
    quizData = [];
    userAnswers = [];
    
    // Process API response into our quiz format
    data.results.forEach(item => {
        // Combine correct and incorrect answers
        const allOptions = [...item.incorrect_answers, item.correct_answer];
        
        // Shuffle options
        const shuffledOptions = shuffleArray(allOptions);
        
        // Find index of correct answer in shuffled array
        const correctIndex = shuffledOptions.indexOf(item.correct_answer);
        
        quizData.push({
            question: decodeHTML(item.question),
            options: shuffledOptions.map(option => decodeHTML(option)),
            correctAnswer: correctIndex
        });
    });
    
    userAnswers = new Array(quizData.length).fill(null);
}

// Display the quiz UI
function displayQuiz(title, category, difficulty, numQuestions) {
    displayQuizTitle.textContent = title;
    displayCategory.textContent = category;
    displayDifficulty.textContent = difficulty;
    displayNumQuestions.textContent = numQuestions;
    
    loadingContainer.style.display = 'none';
    quizContainer.style.display = 'block';
    
    showQuestion(0);
    updateProgress();
}

// Review quiz answers
function reviewQuiz() {
    resultContainer.style.display = 'none';
    quizContainer.style.display = 'block';
    
    // Disable answer selection during review
    const disableSelection = () => {
        const options = document.querySelectorAll('.option');
        options.forEach(option => {
            option.style.cursor = 'default';
            option.replaceWith(option.cloneNode(true));
        });
        
        // Mark correct and incorrect answers
        const question = quizData[currentQuestionIndex];
        const correctOptionIndex = question.correctAnswer;
        const userAnswer = userAnswers[currentQuestionIndex];
        
        const updatedOptions = document.querySelectorAll('.option');
        
        if (userAnswer === correctOptionIndex) {
            updatedOptions[userAnswer].style.borderColor = 'var(--success)';
            updatedOptions[userAnswer].style.backgroundColor = 'rgba(40, 167, 69, 0.15)';
        } else {
            if (userAnswer !== null) {
                updatedOptions[userAnswer].style.borderColor = 'var(--danger)';
                updatedOptions[userAnswer].style.backgroundColor = 'rgba(220, 53, 69, 0.15)';
            }
            
            updatedOptions[correctOptionIndex].style.borderColor = 'var(--success)';
            updatedOptions[correctOptionIndex].style.backgroundColor = 'rgba(40, 167, 69, 0.15)';
        }
    };
    
    // Show first question
    showQuestion(0);
    
    // Override the showQuestion function during review
    const originalShowQuestion = showQuestion;
    showQuestion = (index) => {
        originalShowQuestion(index);
        disableSelection();
        
        // Change Next button text
        if (index === quizData.length - 1) {
            nextBtn.textContent = 'Finish Review';
        }
    };
    
    // Override nextBtn action
    const originalNextAction = nextBtn.onclick;
    nextBtn.onclick = () => {
        if (currentQuestionIndex < quizData.length - 1) {
            showQuestion(currentQuestionIndex + 1);
        } else {
            // Restore original functions
            showQuestion = originalShowQuestion;
            nextBtn.onclick = originalNextAction;
            
            // Go back to results
            quizContainer.style.display = 'none';
            resultContainer.style.display = 'block';
        }
    };
    
    disableSelection();
}

// Reset the quiz
function resetQuiz() {
    currentQuestionIndex = 0;
    quizData = [];
    userAnswers = [];
    clearInterval(timerInterval);
    
    resultContainer.style.display = 'none';
    setupForm.style.display = 'block';
    
    // Reset form fields
    document.getElementById('quizTitle').value = '';
    document.getElementById('quizCategory').value = '';
    
    // Reset difficulty buttons
    difficultyBtns.forEach(btn => btn.classList.remove('selected'));
    difficultyBtns[0].classList.add('selected');
    difficultyInput.value = '';
    
    // Reset question number to default
    document.getElementById('numQuestions').value = '10';
    
    // Remove any error messages
    const errorMsg = document.querySelector('.error-message');
    if (errorMsg) errorMsg.remove();
    
    // Restore original showQuestion function if modified
    showQuestion = function(index) {
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
    };
    
    // Restore original nextBtn action
    nextBtn.onclick = showNextQuestion;
}

// Helper function to decode HTML entities
function decodeHTML(html) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = html;
    return textarea.value;
}

// Shuffle array function (Fisher-Yates algorithm)
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

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
    
    // Update UI to show selected option
    const options = document.querySelectorAll('.option');
    options.forEach((option, index) => {
        if (index === optionIndex) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
    
    updateProgress();
}

// Update progress bar
function updateProgress() {
    const answeredCount = userAnswers.filter(answer => answer !== null).length;
    const progressPercentage = (answeredCount / quizData.length) * 100;
    progressFill.style.width = `${progressPercentage}%`;
    
    currentQuestionText.textContent = `Question ${currentQuestionIndex + 1} of ${quizData.length}`;
}

// Update navigation buttons
function updateNavButtons() {
    prevBtn.disabled = currentQuestionIndex === 0;
    
    if (currentQuestionIndex === quizData.length - 1) {
        nextBtn.textContent = 'Finish Quiz';
        nextBtn.onclick = finishQuiz;
    } else {
        nextBtn.textContent = 'Next';
        nextBtn.onclick = showNextQuestion;
    }
}

// Show next question
function showNextQuestion() {
    if (currentQuestionIndex < quizData.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    }
}

// Show previous question
function showPrevQuestion() {
    if (currentQuestionIndex > 0) {
        showQuestion(currentQuestionIndex - 1);
    }
}

// Finish the quiz
function finishQuiz() {
    clearInterval(timerInterval);
    
    // Calculate score
    let score = 0;
    quizData.forEach((question, index) => {
        if (userAnswers[index] === question.correctAnswer) {
            score++;
        }
    });
    
    const percentage = Math.round((score / quizData.length) * 100);
    
    // Update result UI
    scoreDisplay.textContent = `${percentage}%`;
    correctAnswers.textContent = score;
    totalQuestions.textContent = quizData.length;
    
    // Show result container
    quizContainer.style.display = 'none';
    resultContainer.style.display = 'block';
}

// Start timer
function startTimer() {
    startTime = new Date();
    timerInterval = setInterval(() => {
        const now = new Date();
        const diff = Math.floor((now - startTime) / 1000);
        
        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;
        
        timeElapsed.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// Initialize the app
init();