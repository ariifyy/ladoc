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
      question: "Which password is the most secure?",
      answers: [
        { text: "12345678", correct: false },
        { text: "password123", correct: false },
        { text: "L$d!9g@2#kZ", correct: true },
        { text: "letmein", correct: false },
      ],
      explanation: "A strong password uses uppercase, lowercase, numbers, and symbols, making it much harder to guess or brute-force."
    },
    {
      question: "How often should you change your password?",
      answers: [
        { text: "Never", correct: false },
        { text: "Every 90 days or when compromised", correct: true },
        { text: "Once a week", correct: false },
        { text: "Only when logging in from new devices", correct: false },
      ],
      explanation: "Regular password changes reduce the risk of long-term breaches. 90 days is standard in most security policies."
    },
    {
      question: "What’s a good practice for creating a strong password?",
      answers: [
        { text: "Use pet names or birthdays", correct: false },
        { text: "Use dictionary words", correct: false },
        { text: "Use a mix of letters, numbers, symbols", correct: true },
        { text: "Use your username", correct: false },
      ],
      explanation: "Avoid predictable info. Mixing character types increases entropy and makes it harder to guess."
    },
    {
      question: "What is the benefit of a password manager?",
      answers: [
        { text: "Stores passwords insecurely", correct: false },
        { text: "Helps reuse one password everywhere", correct: false },
        { text: "Helps generate and store complex passwords safely", correct: true },
        { text: "Makes passwords public", correct: false },
      ],
      explanation: "A password manager stores strong, unique passwords in an encrypted vault, so you don't have to remember them."
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
      button.classList.add("cta_button");
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
      const li = document.createElement("li");
      li.innerHTML = `
        <strong>Q${i + 1}: ${item.question}</strong><br/>
        Your answer: <span class="${item.selected === item.correct ? 'correct' : 'wrong'}">${item.selected}</span><br/>
        Correct answer: ${item.correct}<br/>
        <em>${item.explanation}</em>
      `;
      reviewList.appendChild(li);
    });
  }
});
