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
        question: "What is the main goal of a phishing attack?",
        answers: [
        { text: "To speed up computer performance", correct: false },
        { text: "To steal sensitive information like passwords", correct: true },
        { text: "To install software updates", correct: false },
        { text: "To promote legitimate services", correct: false },
        ],
        explanation: "Phishing attacks aim to trick you into revealing sensitive data like passwords or credit card numbers."
    },
    {
        question: "Which of the following is a sign that an email might be a phishing attempt?",
        answers: [
        { text: "An email asking you to 'verify your account immediately'", correct: true },
        { text: "A monthly newsletter from a service you use", correct: false },
        { text: "A birthday greeting from a friend", correct: false },
        { text: "A receipt from a recent online purchase", correct: false },
        ],
        explanation: "Email phishing involves fake emails impersonating trusted companies to trick victims."
    },
    {
        question: "What makes spear phishing more dangerous than regular phishing?",
        answers: [
        { text: "It uses physical mail instead of email", correct: false },
        { text: "It is sent to many random people", correct: false },
        { text: "It targets specific individuals with personalized details", correct: true },
        { text: "It uses QR codes", correct: false },
        ],
        explanation: "Spear phishing is tailored to specific people, using details like names or workplaces to seem more convincing."
    },
    {
        question: "What is 'smishing'?",
        answers: [
        { text: "Phishing using SMS or text messages", correct: true },
        { text: "A scam involving voice calls", correct: false },
        { text: "Using social media to trick people", correct: false },
        { text: "A fake link embedded in a QR code", correct: false },
        ],
        explanation: "Smishing is phishing via SMS messages and often contains fake urgent links or threats."
    },
    {
        question: "Which of the following could be a sign of phishing?",
        answers: [
        { text: "A personal email from a trusted coworker", correct: false },
        { text: "A message pressuring you to act immediately", correct: true },
        { text: "An email from your saved contact list", correct: false },
        { text: "An SMS from a sender called 'gov.sg'", correct: false },
        ],
        explanation: "Phishing often uses urgency or threats to pressure victims into acting quickly without thinking."
    },
    {
        question: "What is an example of a spoofed sender address?",
        answers: [
        { text: "user28ch92oef_fjls3k", correct: false },
        { text: "account.micorsoft.com", correct: false },
        { text: "support@payp4l.com", correct: false },
        { text: "All of the above", correct: true },
        ],
        explanation: "Spoofed addresses mimic real ones with minor changes like swapping letters or adding characters, or they might contain gibberish characters."
    },
    {
        question: "What should you do before clicking a link in an email?",
        answers: [
        { text: "Click quickly to avoid missing out", correct: false },
        { text: "Hover over the link to preview the URL", correct: true },
        { text: "Forward it to a friend", correct: false },
        { text: "Call your bank immediately", correct: false },
        ],
        explanation: "Always hover over links to verify the actual destination before clicking to avoid phishing traps."
    },
    {
        question: "How does clone phishing work?",
        answers: [
        { text: "By stealing cookies from browsers", correct: false },
        { text: "By copying a real email and adding malicious content", correct: true },
        { text: "By hacking your Wi-Fi", correct: false },
        { text: "By sending ads to your email", correct: false },
        ],
        explanation: "Clone phishing copies legitimate emails but modifies them to include malicious links or attachments."
    },
    {
        question: "What is the best action if you receive a suspicious call asking for your bank info?",
        answers: [
        { text: "Give partial info first", correct: false },
        { text: "Hang up and check with the official bank company", correct: true },
        { text: "Press the buttons they tell you to", correct: false },
        { text: "Stay on the line to gather evidence", correct: false },
        ],
        explanation: "Never share information on suspicious calls — always hang up and call the official number yourself."
    },
    {
        question: "Why should you be cautious when scanning random QR codes?",
        answers: [
        { text: "They might contain spoilers", correct: false },
        { text: "They can open a link to harmful websites", correct: true },
        { text: "They rarely work", correct: false },
        { text: "They might play loud sounds", correct: false },
        ],
        explanation: "Attackers use QR codes to redirect you to malicious websites or prompt downloads of harmful apps."
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

    shuffledQuestions = shuffle([...questions]);

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
