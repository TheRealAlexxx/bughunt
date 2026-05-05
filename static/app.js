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
const leaderboardForm = document.getElementById("leaderboardForm");
const playerNameInput = document.getElementById("playerName");
const submitScoreBtn = document.getElementById("submitScoreBtn");
const leaderboardMessageEl = document.getElementById("leaderboardMessage");
const leaderboardListEl = document.getElementById("leaderboardList");

let questions = [];
let currentIndex = 0;
let score = 0;
let selected = false;
let scoreSaved = false;

function errorMessageFromPayload(payload, fallback) {
    if (!payload) {
        return fallback;
    }
    if (typeof payload === "string") {
        return payload;
    }
    if (typeof payload.error === "string") {
        return payload.error;
    }
    if (payload.error && typeof payload.error.message === "string") {
        return payload.error.message;
    }
    if (typeof payload.message === "string") {
        return payload.message;
    }
    return fallback;
}

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
    scoreSaved = false;
    leaderboardMessageEl.textContent = "";
    submitScoreBtn.disabled = false;
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
    loadLeaderboard();
}

function renderLeaderboard(entries) {
    leaderboardListEl.innerHTML = "";
    if (!entries.length) {
        const li = document.createElement("li");
        li.textContent = "No scores yet. Be the first one on the board.";
        leaderboardListEl.appendChild(li);
        return;
    }

    entries.forEach((entry) => {
        const li = document.createElement("li");
        li.textContent = `${entry.name} - ${entry.score}`;
        leaderboardListEl.appendChild(li);
    });
}

async function loadLeaderboard() {
    try {
        const response = await fetch("/api/leaderboard", {
            headers: { Accept: "application/json" },
        });
        const contentType = response.headers.get("content-type") || "";
        const payload = contentType.includes("application/json") ? await response.json() : null;
        if (!response.ok) {
            throw new Error(errorMessageFromPayload(payload, "Failed to load leaderboard."));
        }
        const leaderboard = payload;
        renderLeaderboard(Array.isArray(leaderboard) ? leaderboard : []);
    } catch (_error) {
        renderLeaderboard([]);
        leaderboardMessageEl.textContent = "Leaderboard unavailable right now.";
    }
}

async function submitScore(event) {
    event.preventDefault();
    if (scoreSaved) {
        leaderboardMessageEl.textContent = "Score already saved for this run.";
        return;
    }

    const name = playerNameInput.value.trim();
    if (!name) {
        leaderboardMessageEl.textContent = "Enter your name first.";
        return;
    }

    submitScoreBtn.disabled = true;
    leaderboardMessageEl.textContent = "Saving score...";

    try {
        const response = await fetch("/api/leaderboard", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({ name, score }),
        });
        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await response.json() : null;
        if (!response.ok) {
            throw new Error(errorMessageFromPayload(data, "Unable to save score."));
        }

        scoreSaved = true;
        leaderboardMessageEl.textContent = "Score saved.";
        renderLeaderboard(Array.isArray(data.leaderboard) ? data.leaderboard : []);
    } catch (error) {
        submitScoreBtn.disabled = false;
        leaderboardMessageEl.textContent = error.message;
    }
}

nextBtn.addEventListener("click", () => {
    currentIndex += 1;
    renderQuestion();
});

restartBtn.addEventListener("click", restartGame);
leaderboardForm.addEventListener("submit", submitScore);

loadQuestions();
