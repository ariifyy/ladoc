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
        question: "Which of the following URLs is most likely a phishing attempt?",
        answers: [
        { text: "https://accounts.google.com/login", correct: false },
        { text: "https://secure-login-google.com/account", correct: true },
        { text: "https://www.google.com/securelogin", correct: false },
        { text: "https://mail.google.com/login", correct: false }
        ],
        explanation: "Phishing URLs often mimic real domains but slightly alter or add words. 'secure-login-google.com' is not owned by Google."
    },
    {
        question: "You see this link in an email: https://www.paypa1.com/login (note the character '1'). What type of attack is this?",
        answers: [
        { text: "Homograph attack", correct: true },
        { text: "Typosquatting", correct: false },
        { text: "Clickjacking", correct: false },
        { text: "Man-in-the-middle", correct: false }
        ],
        explanation: "Homograph attacks use lookalike characters (like '1' instead of 'l') to trick users into clicking malicious links."
    },
    {
        question: "Which part of the URL below is the actual domain?\n\nhttps://login.secure.facebook.com.evilsite.ru/login",
        answers: [
        { text: "secure.facebook.com", correct: false },
        { text: "facebook.com", correct: false },
        { text: "evilsite.ru", correct: true },
        { text: "login.secure.facebook.com", correct: false }
        ],
        explanation: "The actual domain is the last part before the TLD — 'evilsite.ru'. The rest is subdomain trickery."
    },
    {
        question: "What is a common tactic used in shortened URLs (e.g., bit.ly/abalskdjf)?",
        answers: [
        { text: "To hide the true destination of a link", correct: true },
        { text: "To show the site's SSL certificate", correct: false },
        { text: "To prevent phishing", correct: false },
        { text: "To extend the link length", correct: false }
        ],
        explanation: "Shortened URLs can obscure the final destination, making it easier for attackers to trick users."
    },
    {
        question: "Which of the following is a safe step when receiving a suspicious link?",
        answers: [
        { text: "Click it quickly to avoid missing out", correct: false },
        { text: "Hover over the link to preview the real destination", correct: true },
        { text: "Forward it to others to ask if it's safe", correct: false },
        { text: "Paste it directly in the address bar", correct: false }
        ],
        explanation: "Hovering reveals the actual URL and can help you spot mismatches or fake domains."
    },
    {
        question: "True or False: A padlock icon in the address bar means the website is completely safe.",
        answers: [
        { text: "True", correct: false },
        { text: "False", correct: true }
        ],
        explanation: "The padlock only shows the site uses HTTPS; it doesn’t guarantee the site is legitimate."
    },
    {
        question: "Which tool would best help reveal where this shortened URL goes: https://bit.ly/3gU2zK9?",
        answers: [
        { text: "unshorten.me", correct: true },
        { text: "Wikipedia", correct: false },
        { text: "Facebook", correct: false },
        { text: "Google Translate", correct: false }
        ],
        explanation: "Use URL unshortening tools like unshorten.me to preview the real destination before clicking."
    },
    {
        question: "What is a sign that a URL might be unsafe or suspicious?",
        answers: [
        { text: "It uses many hyphens or random letters in the domain", correct: true },
        { text: "It loads slowly", correct: false },
        { text: "It uses capital letters", correct: false },
        { text: "It’s hosted in another country", correct: false }
        ],
        explanation: "Attackers often register odd-looking domains to mimic legitimate sites with hyphens or typos."
    },
    {
        question: "You receive an email saying: 'Your bank account is locked! Visit secure-yourbank.com now.' What should you do?",
        answers: [
        { text: "Click the link and enter your info", correct: false },
        { text: "Search for your bank's official site separately and check your account there", correct: true },
        { text: "Reply to the email to verify your bank account", correct: false },
        { text: "Ignore it, it's definitely fake", correct: false }
        ],
        explanation: "Don't trust links in unsolicited messages—go directly to the official site through search or bookmarks."
    },
    {
        question: "Which of the following is a legitimate reason to use a URL scanner like VirusTotal?",
        answers: [
        { text: "To analyze suspicious links before visiting them", correct: true },
        { text: "To find coupons online", correct: false },
        { text: "To speed up your internet", correct: false },
        { text: "To update your antivirus", correct: false }
        ],
        explanation: "URL scanners like VirusTotal help detect threats such as malware or phishing in links."
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
