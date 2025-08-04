document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-btn");
  const submitBtn = document.getElementById("submit-btn");
  const nextBtn = document.getElementById("next-btn");
  const restartBtn = document.getElementById("restart-btn");
  const questionContainer = document.getElementById("question-container");
  const resultContainer = document.getElementById("result-container");
  const reviewContainer = document.getElementById("review-container");
  const questionEl = document.getElementById("question");
  const questionCounter = document.getElementById("question-counter");
  const answerButtons = document.getElementById("answer-buttons");
  const scoreText = document.getElementById("score-text");
  const explanationContainer = document.getElementById("explanation-container");
  const explanationText = document.getElementById("explanation-text");
  const reviewList = document.getElementById("review-list");

  let currentQuestionIndex = 0;
  let score = 0;
  let selectedAnswer = null;
  let hasSubmitted = false;
  let shuffledQuestions = [];
  let userAnswers = [];

  const questions = [
    {
      question: "What is one of the most common mistakes people make with passwords?",
      answers: [
        { text: "Using two-factor authentication", correct: false },
        { text: "Changing passwords regularly", correct: false },
        { text: "Creating long and complex passwords", correct: false },
        { text: "Reusing the same password across multiple sites", correct: true },
      ],
      explanation: "Reusing passwords makes all your accounts vulnerable if one gets breached."
    },
    {
      question: "Which of the following is considered a weak password?",
      answers: [
        { text: "h4ppyB1rthd@y", correct: false },
        { text: "12345678", correct: true },
        { text: "likeadeckofcards2048", correct: false },
        { text: "fG8^zL2&hJ0", correct: false },
      ],
      explanation: "Passwords like 12345678 are among the most common and easily guessed."
    },
    {
      question: "Why should you avoid using personal info in your passwords?",
      answers: [
        { text: "It’s too boring", correct: false },
        { text: "It’s too long", correct: false },
        { text: "It’s easy to guess", correct: true },
        { text: "It’s illegal", correct: false },
      ],
      explanation: "Hackers often look for names, birthdays, and pet names in data breaches or social media."
    },
    {
      question: "What is the recommended minimum length for a strong password?",
      answers: [
        { text: "6 characters", correct: false },
        { text: "8 characters", correct: false },
        { text: "10 characters", correct: false },
        { text: "12 characters", correct: true },
      ],
      explanation: "12–16 characters is the widely recommended minimum for password security."
    },
    {
      question: "What is a 'keyboard walk' password?",
      answers: [
        { text: "A phrase from a book", correct: false },
        { text: "A password using keys next to each other", correct: true },
        { text: "A string of random emojis", correct: false },
        { text: "A phrase translated from another language", correct: false },
      ],
      explanation: "Examples like 'qwerty' or 'asdfgh' are called keyboard walks and are easy to guess."
    },
    {
      question: "What is the risk of using the same password on multiple accounts?",
      answers: [
        { text: "You might forget it", correct: false },
        { text: "It makes logging in faster", correct: false },
        { text: "It’s easier to type", correct: false },
        { text: "If one account is breached, others are at risk", correct: true },
      ],
      explanation: "Hackers can use your breached login on other websites—called credential stuffing."
    },
    {
      question: "What is a passkey?",
      answers: [
        { text: "A code stored on paper", correct: false },
        { text: "A recovery email", correct: false },
        { text: "Biometric or device-based authentication method", correct: true },
        { text: "A dictionary word with a number", correct: false },
      ],
      explanation: "Passkeys are modern alternatives to passwords, often using biometrics or hardware."
    },
    {
      question: "What does a password manager help with?",
      answers: [
        { text: "It shares your passwords with others", correct: false },
        { text: "It stores them on your clipboard", correct: false },
        { text: "It securely stores and generates strong passwords", correct: true },
        { text: "It makes all passwords public", correct: false },
      ],
      explanation: "Password managers store your credentials in an encrypted vault and help generate strong passwords."
    },
    {
      question: "What is Multi-Factor Authentication (MFA)?",
      answers: [
        { text: "Using multiple usernames", correct: false },
        { text: "Using both a password and another verification method", correct: true },
        { text: "Typing your password twice", correct: false },
        { text: "Logging in from multiple devices", correct: false },
      ],
      explanation: "MFA protects your account by requiring a second factor like a code or biometric scan."
    },
    {
      question: "Which of these is NOT a good password practice?",
      answers: [
        { text: "Using at least one symbol and one number", correct: false },
        { text: "Generating unique passwords for each account", correct: false },
        { text: "Storing passwords securely in a password manager", correct: false },
        { text: "Using your name and birthday", correct: true },
      ],
      explanation: "Personal information is predictable and commonly guessed by attackers."
    }
  ];


  startBtn.addEventListener("click", startQuiz);
  submitBtn.addEventListener("click", submitAnswer);
  nextBtn.addEventListener("click", handleNext);
  restartBtn.addEventListener("click", startQuiz);

  function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  function startQuiz() {
    startBtn.classList.add("hide");
    resultContainer.classList.add("hide");
    reviewContainer.classList.add("hide");
    questionContainer.classList.remove("hide");
    currentQuestionIndex = 0;
    score = 0;
    hasSubmitted = false;
    userAnswers = [];

    shuffledQuestions = shuffle([...questions]);  // Fisher-Yates shuffle here

    setNextQuestion();
  }

  function setNextQuestion() {
    resetState();
    hasSubmitted = false;
    selectedAnswer = null;

    const question = shuffledQuestions[currentQuestionIndex];
    questionEl.innerText = question.question;
    questionCounter.innerText = `Question ${currentQuestionIndex + 1} of ${shuffledQuestions.length}`;

    question.answers.forEach((answer) => {
      const button = document.createElement("button");
      button.innerText = answer.text;
      button.classList.add("cta_button", "quiz_button");
      button.dataset.correct = answer.correct;
      button.addEventListener("click", () => selectAnswer(button));
      answerButtons.appendChild(button);
    });
  }

  function resetState() {
    submitBtn.disabled = true;
    nextBtn.classList.add("hide");
    explanationContainer.classList.add("hide");
    while (answerButtons.firstChild) {
      answerButtons.removeChild(answerButtons.firstChild);
    }
  }

  function selectAnswer(button) {
    if (hasSubmitted) return;

    selectedAnswer = button;
    submitBtn.disabled = false;

    Array.from(answerButtons.children).forEach(btn => {
      btn.classList.remove("selected");
    });

    button.classList.add("selected");
  }

  function submitAnswer() {
    if (!selectedAnswer || hasSubmitted) return;

    hasSubmitted = true;
    const isCorrect = selectedAnswer.dataset.correct === "true";
    if (isCorrect) score++;

    Array.from(answerButtons.children).forEach((btn) => {
      btn.disabled = true;
      btn.classList.add(btn.dataset.correct === "true" ? "correct" : "wrong");
    });

    const explanation = shuffledQuestions[currentQuestionIndex].explanation;
    explanationText.innerText = explanation;
    explanationContainer.classList.remove("hide");

    userAnswers.push({
      question: shuffledQuestions[currentQuestionIndex].question,
      selected: selectedAnswer.innerText,
      correct: shuffledQuestions[currentQuestionIndex].answers.find(a => a.correct).text,
      explanation: explanation
    });

    submitBtn.disabled = true;
    nextBtn.classList.remove("hide");
  }

  function handleNext() {
    currentQuestionIndex++;
    if (currentQuestionIndex < shuffledQuestions.length) {
      setNextQuestion();
    } else {
      showResult();
    }
  }

  function showResult() {
    questionContainer.classList.add("hide");
    resultContainer.classList.remove("hide");
    reviewContainer.classList.remove("hide");
    scoreText.innerText = `Test score: ${score} out of ${shuffledQuestions.length}.`;

    reviewList.innerHTML = "";
    userAnswers.forEach((item, i) => {
      const section = document.createElement("div");
      section.classList.add("module-section");

      section.innerHTML = `
        <p><strong>Q${i + 1}: ${item.question}</strong></p>
        <p>Your answer: <span class="${item.selected === item.correct ? 'correct' : 'wrong'}">${item.selected}</span></p>
        <p>Correct answer: ${item.correct}</p>
        <p><em>${item.explanation}</em></p>
      `;

      reviewList.appendChild(section);
    });

  }
});
