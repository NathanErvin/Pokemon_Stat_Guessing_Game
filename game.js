// --- Core state ---
let selectedGen = "";
let currentPokemon = {};
let guessedPokemon = []; // valid, first-time guesses only
let maxGuesses = 20;
let hintsAllowed = true;
let incorrectGuesses = 0;
let hintHistory = []; // stacked hints

// Shiny system (unique-only, sequential letter reveals)
let shinyUniqueSet = new Set(); // names (lowercase) that have already triggered shiny
let shinyLetterIndex = -1; // index into answer's letters

// simple in-memory caches
window.__genCache = {}; // { "Gen 1": [...], ... }
window.__allCache = null; // combined list1..list9

// --- DOM ready ---
window.addEventListener("DOMContentLoaded", () => {
  const genSelect = document.getElementById("generation");
  const startBtn = document.getElementById("start");
  const guessInput = document.getElementById("guess");
  const guessBtn = document.getElementById("guess-btn");
  const hintToggle = document.getElementById("toggle-hints");

  hintToggle.addEventListener("change", () => {
    hintsAllowed = hintToggle.checked;
    applyHintsLayout(); // hide/show sidebar + recenter
  });

  startBtn.addEventListener("click", async () => {
    selectedGen = genSelect.value.trim();
    if (!selectedGen) {
      setFeedback("Please select a list to start (e.g., Gen 1 or All).");
      return;
    }
    await startNewGame(selectedGen);
  });

  guessBtn.addEventListener("click", makeGuess);
  guessInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") makeGuess();
  });

  // initial layout
  applyHintsLayout();
});

// --- Layout toggle (hide sidebar & recenter when hints disabled) ---
function applyHintsLayout() {
  const layout = document.querySelector(".layout");
  if (!layout) return;
  layout.classList.toggle("no-hints", !hintsAllowed);
}

// --- Utilities ---
function setFeedback(msg) {
  document.getElementById("feedback").innerText = msg;
}

function formatPokemonDetails(p) {
  if (!p) return "";
  const parts = [
    `Name: ${p.Name}`,
    `Pokedex #: ${p["Pokedex #"]}`,
    `Type: ${p.Type ?? "Unknown"}`,
    `Abilities: ${p.Abilities ?? "Unknown"}`,
    `Forms: ${p.Forms ?? "None"}  |  Gender Var.: ${p["Gender Var."] ?? "No"}`,
    `Base Stats — HP: ${p.HP}, Atk: ${p.Attack}, Def: ${p.Defense}, SpA: ${p["Sp. Atk"]}, SpD: ${p["Sp. Def"]}, Spe: ${p.Speed}`,
  ];
  return parts.join("\n");
}

function showDetails(text) {
  const el = document.getElementById("details");
  el.innerText = text || "";
  el.style.display = text ? "block" : "none";
}

function capitalize(s) {
  if (!s) return s;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// --- Hints UI (stacking) ---
function resetHintsUI() {
  hintHistory = [];
  renderHints();
}

function addHint(text, { shiny = false } = {}) {
  if (!text) return;
  if (!shiny && !hintsAllowed) return; // normal hints respect toggle; shiny do not

  if (!hintHistory.includes(text)) {
    hintHistory.push(text);
    renderHints();
  }
}

function renderHints() {
  const ul = document.getElementById("hints-list");
  if (!ul) return;
  ul.innerHTML = "";
  for (const h of hintHistory) {
    const li = document.createElement("li");
    if (h.startsWith("✨ Shiny!")) li.classList.add("shiny");
    li.textContent = h;
    ul.appendChild(li);
  }
}

// --- Data loading ---
const GEN_TO_FILES = {
  All: [
    "list1.json",
    "list2.json",
    "list3.json",
    "list4.json",
    "list5.json",
    "list6.json",
    "list7.json",
    "list8.json",
    "list9.json",
  ],
  "Gen 1": ["list1.json"],
  "Gen 2": ["list2.json"],
  "Gen 3": ["list3.json"],
  "Gen 4": ["list4.json"],
  "Gen 5": ["list5.json"],
  "Gen 6": ["list6.json"],
  "Gen 7": ["list7.json"],
  "Gen 8": ["list8.json"],
  "Gen 9": ["list9.json"],
  Mega: ["listmega.json"],
};

async function loadFiles(files) {
  const all = [];
  for (const f of files) {
    try {
      const res = await fetch(f);
      if (!res.ok) throw new Error(`Failed to fetch ${f}`);
      const data = await res.json();
      if (Array.isArray(data)) all.push(...data);
    } catch (err) {
      console.error(err);
    }
  }
  return all;
}

async function ensureGenCache(gen) {
  if (!window.__genCache[gen]) {
    const files = GEN_TO_FILES[gen] || [];
    window.__genCache[gen] = await loadFiles(files);
  }
  return window.__genCache[gen];
}

async function ensureAllCache() {
  if (!window.__allCache) {
    window.__allCache = await loadFiles(GEN_TO_FILES["All"]);
  }
  return window.__allCache;
}

// --- Game lifecycle ---
async function startNewGame(gen) {
  // Reset UI/state
  guessedPokemon = [];
  incorrectGuesses = 0;
  shinyUniqueSet = new Set();
  shinyLetterIndex = -1;

  setFeedback("Loading Pokémon…");
  showDetails("");
  resetHintsUI();
  applyHintsLayout();

  const tbody = document.getElementById("guesses");
  if (tbody) tbody.innerHTML = "";
  const table = document.getElementById("comparison-table");
  if (table) table.style.display = "none";

  const pool = await ensureGenCache(gen);
  if (!pool.length) {
    setFeedback("No Pokémon data found for this selection.");
    return;
  }

  // Preload global list for spell-check (All)
  await ensureAllCache();

  // select answer
  currentPokemon = pool[Math.floor(Math.random() * pool.length)];

  setFeedback("Game started! Make a guess.");
}

// --- Guess flow ---
function makeGuess() {
  const input = document.getElementById("guess");
  const raw = input.value.trim();
  const guess = raw.toLowerCase();
  if (!guess) return;

  const pool = window.__genCache[selectedGen] || [];
  const inGen = pool.find((p) => (p.Name || "").toLowerCase() === guess);

  // Not in current gen? Check global existence
  if (!inGen) {
    const all = window.__allCache || [];
    const existsGlobally = all.find(
      (p) => (p.Name || "").toLowerCase() === guess
    );

    if (existsGlobally) {
      setFeedback(
        `${capitalize(
          guess
        )} exists, but not in "${selectedGen}". That guess doesn’t count.`
      );
      input.value = "";
      return; // no shiny roll
    } else {
      const suggestions = getCloseMatches(
        guess,
        all.map((p) => p.Name),
        5
      );
      if (suggestions.length) {
        setFeedback(
          `"${raw}" isn’t a known Pokémon. Did you mean: ${suggestions.join(
            ", "
          )} ?`
        );
      } else {
        setFeedback(`"${raw}" isn’t a known Pokémon.`);
      }
      input.value = "";
      return; // no shiny roll
    }
  }

  // Valid in current gen from here onward

  // Repeated valid guess? No stacking, no shiny roll, no row
  if (guessedPokemon.includes(guess)) {
    setFeedback(
      `You already guessed "${capitalize(
        guess
      )}". Repeats don’t count and won’t roll shiny.`
    );
    input.value = "";
    return;
  }

  // New valid guess — determine shiny first so we can set the row image
  const shinyThisGuess = rollShiny(); // 1 in 25

  // If shiny triggers and this Pokémon hasn't triggered shiny before, reveal next letter
  if (shinyThisGuess && !shinyUniqueSet.has(guess)) {
    shinyUniqueSet.add(guess);
    revealNextAnswerLetter(); // adds shiny hint line
  }

  // Record the guess (after we've used the name for shiny uniqueness)
  guessedPokemon.push(guess);

  // Win?
  if (currentPokemon && guess === (currentPokemon.Name || "").toLowerCase()) {
    setFeedback(`Correct! The Pokémon was ${currentPokemon.Name}.`);
    showDetails(formatPokemonDetails(currentPokemon));
    // ⬇️ FIX: insert winning row at TOP
    addGuessToTable(guess, { shiny: shinyThisGuess }, { prepend: true });
    input.value = "";
    return;
  }

  // Not correct — consume a guess
  incorrectGuesses++;
  if (incorrectGuesses >= maxGuesses) {
    setFeedback("You ran out of guesses. Game over!");
    const d = `The Pokémon was ${
      currentPokemon.Name
    }.\n\n${formatPokemonDetails(currentPokemon)}`;
    showDetails(d);
  } else {
    setFeedback(
      `Incorrect! ${maxGuesses - incorrectGuesses} guesses remaining.`
    );
    if (hintsAllowed && incorrectGuesses % 5 === 0) {
      const hint = getHint(); // returns a single hint line
      addHint(hint); // append to history
    }
  }

  // Add row (shiny or normal image) — NEW GUESSES GO ON TOP
  addGuessToTable(guess, { shiny: shinyThisGuess }, { prepend: true });
  input.value = "";
}

// --- Shiny helpers ---
function rollShiny() {
  return Math.floor(Math.random() * 25) === 0;
}

function revealNextAnswerLetter() {
  const letters = getAnswerLetters();
  if (!letters.length) return;
  shinyLetterIndex = Math.min(shinyLetterIndex + 1, letters.length - 1);
  const letter = letters[shinyLetterIndex];
  addHint(`✨ Shiny! Letter ${shinyLetterIndex + 1}: ${letter}`, {
    shiny: true,
  });
}

function getAnswerLetters() {
  const raw = (currentPokemon.Name || "").toUpperCase();
  return Array.from(raw).filter((ch) => ch >= "A" && ch <= "Z");
}

// --- Image helpers (prefer high-res HOME when available) ---
function preferHighRes(url) {
  if (!url) return null;
  return url.includes("/home-thumb/")
    ? url.replace("/home-thumb/", "/home/")
    : url;
}

// --- Persistent guess list with larger image next to name (PREPEND rows) ---
function addGuessToTable(
  guess,
  { shiny = false } = {},
  { prepend = false } = {}
) {
  const table = document.getElementById("comparison-table");
  const tbody = document.getElementById("guesses");
  if (!table || !tbody) return;

  // Show table on first valid-in-gen guess
  table.style.display = "";

  const genPool = window.__genCache[selectedGen] || [];
  const guessedPkmn = genPool.find(
    (p) => (p.Name || "").toLowerCase() === guess
  );

  const row = document.createElement("tr");

  // Name cell with thumbnail
  const nameTd = document.createElement("td");
  nameTd.classList.add("name-cell");

  const baseUrl = guessedPkmn.Image || guessedPkmn.image || null;
  const shinyUrl = guessedPkmn.Shiny || guessedPkmn.shiny || null;

  const primary =
    shiny && shinyUrl ? preferHighRes(shinyUrl) : preferHighRes(baseUrl);
  const fallback1 = shiny && shinyUrl ? shinyUrl : baseUrl;
  const fallback2 = shiny && baseUrl ? baseUrl : shinyUrl;

  if (primary || fallback1 || fallback2) {
    const img = document.createElement("img");
    img.className = "pkmn-thumb";
    img.alt = guessedPkmn.Name || "pokemon";
    img.decoding = "async";
    img.loading = "lazy";

    const candidates = [primary, fallback1, fallback2].filter(Boolean);
    let idx = 0;
    const setNext = () => {
      if (idx >= candidates.length) {
        img.style.display = "none";
        return;
      }
      img.src = candidates[idx++];
    };
    img.onerror = setNext;
    setNext();

    nameTd.appendChild(img);
  }

  const nameSpan = document.createElement("span");
  nameSpan.textContent = guessedPkmn.Name + (shiny ? " ★" : "");
  nameTd.appendChild(nameSpan);
  row.appendChild(nameTd);

  // Stat cells with arrows (kept single-line by CSS no-wrap)
  [
    "Pokedex #",
    "HP",
    "Attack",
    "Defense",
    "Sp. Atk",
    "Sp. Def",
    "Speed",
  ].forEach((label) => {
    const td = document.createElement("td");
    td.classList.add("stat-cell");
    const g = guessedPkmn[label];
    const a = currentPokemon[label];

    if (typeof g === "number" && typeof a === "number") {
      let indicator = "eq";
      let text = `${g} =`;
      if (g < a) {
        indicator = "up";
        text = `${g} ↑`;
      } else if (g > a) {
        indicator = "down";
        text = `${g} ↓`;
      }
      td.textContent = text;
      td.setAttribute("data-indicator", indicator);
    } else {
      td.textContent = g ?? "";
    }
    row.appendChild(td);
  });

  // PREPEND newest row on top
  if (prepend && tbody.firstChild) {
    tbody.insertBefore(row, tbody.firstChild);
  } else {
    tbody.appendChild(row);
  }
}

// --- Hints (stacked; Forms shows actual value) ---
function getHint() {
  if (!currentPokemon) return "";
  if (incorrectGuesses === 5) {
    const forms =
      currentPokemon.Forms &&
      String(currentPokemon.Forms).trim().toLowerCase() !== "none"
        ? String(currentPokemon.Forms)
        : "None";
    return `Forms: ${forms}`;
  } else if (incorrectGuesses === 10) {
    const gd = genderChecker(currentPokemon) ? "Yes" : "No";
    return `Gender Differences: ${gd}`;
  } else if (incorrectGuesses === 15) {
    return `Abilities: ${currentPokemon.Abilities ?? "Unknown"}`;
  } else if (incorrectGuesses === 20) {
    return `Type: ${currentPokemon.Type ?? "Unknown"}`;
  }
  return "";
}

function genderChecker(p) {
  return (
    p && p["Gender Var."] && String(p["Gender Var."]).toLowerCase() === "yes"
  );
}

// --- Spell-check helpers (Levenshtein) ---
function levenshtein(a, b) {
  a = a.toLowerCase();
  b = b.toLowerCase();
  const m = a.length,
    n = b.length;
  if (m === 0) return n;
  if (n === 0) return m;
  const dp = new Array(n + 1);
  for (let j = 0; j <= n; j++) dp[j] = j;
  for (let i = 1; i <= m; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= n; j++) {
      const temp = dp[j];
      if (a[i - 1] === b[j - 1]) {
        dp[j] = prev;
      } else {
        dp[j] = Math.min(prev + 1, dp[j] + 1, dp[j - 1] + 1);
      }
      prev = temp;
    }
  }
  return dp[n];
}

function getCloseMatches(word, candidates, n = 5) {
  const len = word.length;
  const threshold = len <= 5 ? 1 : len <= 8 ? 2 : 3;
  const scored = [];
  for (const c of candidates) {
    const d = levenshtein(word, String(c).toLowerCase());
    if (d <= threshold) scored.push({ name: c, d });
  }
  scored.sort((a, b) => a.d - b.d || a.name.localeCompare(b.name));
  return scored.slice(0, n).map((s) => s.name);
}