const codeBlock = document.getElementById("codeBlock");
const optionsEl = document.getElementById("options");
const scoreEl = document.getElementById("score");
const progressEl = document.getElementById("progress");
const progressBar = document.getElementById("progressBar");
const feedbackEl = document.getElementById("feedback");
const nextBtn = document.getElementById("nextBtn");
const restartBtn = document.getElementById("restartBtn");
const questionView = document.getElementById("questionView");
const endView = document.getElementById("endView");
const finalScoreEl = document.getElementById("finalScore");

let questions = [];
let currentIndex = 0;
let score = 0;
let selected = false;

async function loadQuestions() {
    try {
        questions = await fetchQuestions();
        restartGame();
    } catch (error) {
        codeBlock.textContent = "Unable to load questions. Please refresh and try again.";
        feedbackEl.textContent = error.message;
    }
}

async function fetchQuestions() {
    const endpoints = ["/api", "/api/questions"];

    for (const endpoint of endpoints) {
        const response = await fetch(endpoint, {
            headers: { Accept: "application/json" },
        });

        const contentType = response.headers.get("content-type") || "";

        if (response.ok && contentType.includes("application/json")) {
            return response.json();
        }
    }

    throw new Error("Question API returned HTML instead of JSON. On Vercel, make sure /api routes to /api/index.py.");
}

function restartGame() {
    currentIndex = 0;
    score = 0;
    selected = false;
    questionView.classList.remove("hidden");
    endView.classList.add("hidden");
    renderQuestion();
}

function renderQuestion() {
    if (currentIndex >= questions.length) {
        showEndScreen();
        return;
    }

    selected = false;
    const question = questions[currentIndex];
    codeBlock.textContent = question.code;
    optionsEl.innerHTML = "";
    feedbackEl.textContent = "";
    nextBtn.disabled = true;
    nextBtn.textContent = currentIndex === questions.length - 1 ? "Finish game" : "Next question";

    question.options.forEach((option, index) => {
        const button = document.createElement("button");
        button.className = "option-btn";
        button.type = "button";
        button.textContent = option;
        button.addEventListener("click", () => selectAnswer(index));
        optionsEl.appendChild(button);
    });

    updateStats();
}

function selectAnswer(index) {
    if (selected) {
        return;
    }

    selected = true;
    const question = questions[currentIndex];
    const buttons = [...optionsEl.querySelectorAll(".option-btn")];
    const isCorrect = index === question.correct;

    if (isCorrect) {
        score += 1;
        feedbackEl.textContent = "Correct fix selected.";
    } else {
        feedbackEl.textContent = "Not quite. The green answer is the correct fix.";
    }

    buttons.forEach((button, buttonIndex) => {
        button.disabled = true;

        if (buttonIndex === question.correct) {
            button.classList.add("correct");
        }

        if (buttonIndex === index && !isCorrect) {
            button.classList.add("wrong");
        }
    });

    nextBtn.disabled = false;
    updateStats();
}

function updateStats() {
    scoreEl.textContent = `Score: ${score}`;
    progressEl.textContent = `${Math.min(currentIndex + 1, questions.length)}/${questions.length}`;
    progressBar.style.width = `${questions.length ? ((currentIndex + Number(selected)) / questions.length) * 100 : 0}%`;
}

function showEndScreen() {
    questionView.classList.add("hidden");
    endView.classList.remove("hidden");
    progressEl.textContent = `${questions.length}/${questions.length}`;
    progressBar.style.width = "100%";
    finalScoreEl.textContent = `Final score: ${score}/${questions.length}`;
}

nextBtn.addEventListener("click", () => {
    currentIndex += 1;
    renderQuestion();
});

restartBtn.addEventListener("click", restartGame);

loadQuestions();
