document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
        }
    });
    
    // Track and testimonial slider functionality
    const track = document.getElementById("testimonialTrack");
    const dots = document.querySelectorAll(".dot");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    let currentIndex = 0;
    const totalSlides = dots.length;

    function updateSlider(index) {
        track.style.transform = `translateX(-${index * 100}%)`;
        dots.forEach((dot) => dot.classList.remove("active"));
        dots[index].classList.add("active");
    }

    nextBtn.addEventListener("click", () => {
        currentIndex = (currentIndex + 1) % totalSlides;
        updateSlider(currentIndex);
    });

    prevBtn.addEventListener("click", () => {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateSlider(currentIndex);
    });

    dots.forEach((dot) => {
        dot.addEventListener("click", () => {
            const index = parseInt(dot.getAttribute("data-index"));
            currentIndex = index;
            updateSlider(index);
        });
    });

    // Quiz options animation
    const quizOptions = document.querySelectorAll(".quiz-option");

    quizOptions.forEach((option) => {
        option.addEventListener("click", function () {
            // Remove selected class from all options
            quizOptions.forEach((opt) => opt.classList.remove("selected"));
            // Add selected class to clicked option
            this.classList.add("selected");
            this.style.borderColor = "#4a6bff";
            this.style.backgroundColor = "rgba(74, 107, 255, 0.2)";
        });
    });

    // Create particles dynamically
    function createParticles() {
        const aiParticles = document.querySelector(".ai-particles");
        if (aiParticles) {
            for (let i = 0; i < 15; i++) {
                const particle = document.createElement("div");
                particle.classList.add("particle");

                // Random position and animation
                const x = Math.random() * 300 - 150;
                const y = Math.random() * 300 - 150;
                const delay = Math.random() * 10;

                particle.style.setProperty("--x", `${x}px`);
                particle.style.setProperty("--y", `${y}px`);
                particle.style.animationDelay = `${delay}s`;

                aiParticles.appendChild(particle);
            }
        }
    }

    // Quiz data and functionality
    const quizData = [
        {
            question: "Which planet has the most moons?",
            options: ["Jupiter", "Saturn", "Uranus", "Neptune"],
            correct: 0
        },
        {
            question: "Which language is used for AI?",
            options: ["Java", "Python", "C++", "Ruby"],
            correct: 1
        },
        {
            question: "What is the capital of France?",
            options: ["London", "Berlin", "Paris", "Madrid"],
            correct: 2
        },
        {
            question: "Which element has the chemical symbol 'O'?",
            options: ["Oxygen", "Gold", "Osmium", "Oganesson"],
            correct: 0
        },
        {
            question: "Who painted the Mona Lisa?",
            options: ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo"],
            correct: 1
        }
    ];

    let currentQuestion = 0;
    let userAnswers = new Array(quizData.length).fill(-1);

    // Initialize Quiz
    function initQuiz() {
        loadQuestion();
        attachEventListeners();
    }

    // Load Question
    function loadQuestion() {
        const quizContent = document.getElementById('quiz-content');
        if (!quizContent) return;
        
        const question = quizData[currentQuestion];

        quizContent.innerHTML = `
<div class="quiz-question">${question.question}</div>
<div class="quiz-options">
    ${question.options.map((option, index) => `
        <div class="quiz-option ${userAnswers[currentQuestion] === index ? 'selected' : ''}" data-index="${index}">
            ${String.fromCharCode(65 + index)}. ${option}
        </div>
    `).join('')}
</div>
<div class="quiz-progress">
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
    </div>
    <div class="quiz-nav">
        <button id="prev-btn" class="btn btn-outline">Previous</button>
        <span id="question-counter">Question ${currentQuestion + 1}/${quizData.length}</span>
        <button id="next-btn" class="btn btn-primary">${currentQuestion === quizData.length - 1 ? 'Submit' : 'Next'}</button>
    </div>
</div>
`;

        updateProgress();
        attachEventListeners();
    }

    // Attach event listeners to newly added elements
    function attachEventListeners() {
        // Add click event to options
        document.querySelectorAll('.quiz-option').forEach(option => {
            option.addEventListener('click', selectAnswer);
        });

        // Add event listeners for navigation buttons
        const nextButton = document.getElementById('next-btn');
        const prevButton = document.getElementById('prev-btn');
        
        if (nextButton) {
            nextButton.addEventListener('click', nextQuestion);
        }
        
        if (prevButton) {
            prevButton.addEventListener('click', prevQuestion);
        }
    }

    // Select Answer
    function selectAnswer(e) {
        document.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
        e.target.classList.add('selected');
        userAnswers[currentQuestion] = parseInt(e.target.getAttribute('data-index'));
    }

    // Next Question
    function nextQuestion() {
        if (currentQuestion < quizData.length - 1) {
            currentQuestion++;
            const quizContent = document.getElementById('quiz-content');
            quizContent.classList.add('question-transition');
            setTimeout(() => {
                loadQuestion();
                quizContent.classList.remove('question-transition');
            }, 300);
        } else {
            showResults();
        }
    }

    // Previous Question
    function prevQuestion() {
        if (currentQuestion > 0) {
            currentQuestion--;
            const quizContent = document.getElementById('quiz-content');
            quizContent.classList.add('question-transition');
            setTimeout(() => {
                loadQuestion();
                quizContent.classList.remove('question-transition');
            }, 300);
        }
    }

    // Update Progress
    function updateProgress() {
        const questionCounter = document.getElementById('question-counter');
        const progressFill = document.getElementById('progress-fill');
        
        if (questionCounter) {
            questionCounter.textContent = `Question ${currentQuestion + 1}/${quizData.length}`;
        }
        
        if (progressFill) {
            const progress = ((currentQuestion + 1) / quizData.length) * 100;
            progressFill.style.width = `${progress}%`;
        }
    }

    // Show Results
    function showResults() {
        const correctAnswers = userAnswers.filter((answer, index) => answer === quizData[index].correct).length;
        const score = Math.round((correctAnswers / quizData.length) * 100);

        const quizContent = document.getElementById('quiz-content');
        quizContent.innerHTML = `
<div class="result-wrapper">
    <div class="congrats-heading">🎉 Congrats! 🎉</div>
    
    <div class="result-score">${score}%</div>
    <div class="result-summary">You got ${correctAnswers} out of ${quizData.length} questions correct.</div>
    <button id="restart-btn" class="result-btn">🔁 Restart Quiz</button>
</div>
`;

        document.getElementById('restart-btn').addEventListener('click', restartQuiz);
    }

    // Restart Quiz
    function restartQuiz() {
        currentQuestion = 0;
        userAnswers = new Array(quizData.length).fill(-1);
        loadQuestion();
    }

    // Initialize on load
    createParticles();
    initQuiz();
}); 