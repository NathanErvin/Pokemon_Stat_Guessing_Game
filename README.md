# Pokémon Guessing Game

A Pokémon-themed guessing game that challenges players to identify a randomly selected Pokémon using its Pokédex number, base stats, and helpful hints.

Built using **HTML, CSS, and JavaScript**, this project offers an interactive way to test your Pokémon knowledge across all nine generations, including Mega Evolutions.

## How to Play

1. **Select a Generation:** Choose Pokémon from Generations 1–9, all generations combined, or Mega Evolutions.
2. **Enable or Disable Hints:** Decide whether you want additional clues throughout the game.
3. **Start a New Game:** A random Pokémon will be selected from your chosen category.
4. **Make Your Guesses:** Enter the name of a Pokémon you think might be the answer.
5. **Compare Stats:** Use the information displayed after each guess to narrow down the possibilities.
6. **Find the Pokémon:** Correctly identify the mystery Pokémon before running out of guesses!

Players have a maximum of **20 incorrect guesses** to identify the mystery Pokémon.

## Features

### Generation Selection
Choose from multiple Pokémon categories:

- Generations 1–9
- All Generations
- Mega Evolutions

Each category uses its own Pokémon dataset, allowing players to customize the difficulty and scope of their game.

### Pokémon Stat Comparisons
After submitting a valid guess, players can compare their Pokémon against the mystery Pokémon using the following attributes:

| Attribute | Description |
|---|---|
| Pokédex # | National Pokédex number |
| HP | Base health stat |
| Attack | Base physical attack |
| Defense | Base physical defense |
| Sp. Atk | Base special attack |
| Sp. Def | Base special defense |
| Speed | Base speed stat |

These comparisons help players narrow down the possible answers.

### Hint System
An optional hint system provides additional information about the mystery Pokémon as the game progresses.

Hints accumulate throughout the game, allowing players to reference previously revealed clues.

Players looking for an additional challenge can disable regular hints before starting.

### Shiny Pokémon
The game includes a special shiny Pokémon mechanic!

- Each eligible new guess has a **1-in-25 chance** of appearing shiny.
- Shiny encounters provide an additional clue by revealing letters of the mystery Pokémon's name.
- Shiny clues are separate from the standard hint system.

### Interactive Guess History
Every valid guess is displayed in a comparison table, allowing players to review their previous attempts.

New guesses appear at the top of the table, keeping the most recent information easily accessible.

### Game Feedback
The game provides feedback for guesses, tracks remaining attempts, and reveals the mystery Pokémon's information when the game ends.

## Technologies Used

- **HTML5** — Page structure and interface elements
- **CSS3** — Styling, layout, and visual presentation
- **JavaScript** — Game logic, user interactions, and Pokémon comparisons
- **JSON** — Pokémon information, including names, stats, abilities, forms, and sprite references
- **Python** — Separate terminal-based version of the guessing game

The browser game is built using vanilla JavaScript and does not require a front-end framework.

## 📁 Project Structure

```text
pokemon_game/
│
├── index.html          # Main game interface
├── game.css            # Game styling and layout
├── game.js             # Browser game logic
├── code3.py            # Python terminal-based game
│
├── list1.json          # Generation 1 Pokémon
├── list2.json          # Generation 2 Pokémon
├── list3.json          # Generation 3 Pokémon
├── list4.json          # Generation 4 Pokémon
├── list5.json          # Generation 5 Pokémon
├── list6.json          # Generation 6 Pokémon
├── list7.json          # Generation 7 Pokémon
├── list8.json          # Generation 8 Pokémon
├── list9.json          # Generation 9 Pokémon
├── listmega.json       # Mega Evolution Pokémon
│
└── .vscode/            # VS Code configuration
```

## Getting Started

### Prerequisites

To run the browser version, you will need:

- A modern web browser such as Chrome, Firefox, or Edge
- A local development server, such as VS Code Live Server or Python's built-in HTTP server

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

**2. Navigate to the project directory**

```bash
cd YOUR-REPOSITORY
```

**3. Start a local server**

If you have Python installed, run:

```bash
python -m http.server 8000
```

Alternatively, open the project in Visual Studio Code and use the Live Server extension.

**4. Open the game**

Navigate to:

```text
http://localhost:8000
```

You can now select a Pokémon category and begin playing!

**Note:** Running the game through a local server is recommended because the JavaScript uses `fetch()` to load Pokémon data from JSON files.

## Python Version

The repository also contains a separate Python implementation of the Pokémon guessing game.

To run the terminal-based version:

```bash
python code3.py
```

Run this command from the project directory so the Python script can locate the Pokémon JSON files.

## Pokémon Data

Pokémon information is stored locally in JSON files organized by generation.

Each Pokémon entry contains information such as:

- Name and National Pokédex number
- Pokémon type
- Abilities
- Alternate forms and gender variations
- Six base stats
- Normal and shiny sprite URLs

The game loads the appropriate data based on the player's selected generation.

## 🔮 Possible Future Improvements

Potential additions to the project include:

- Additional game modes and difficulty settings
- A score and win/loss tracking system
- Daily Pokémon challenges
- Improved mobile responsiveness
- Additional hint types
- Expanded Pokémon and form support
- Leaderboards and player statistics

## Disclaimer

This is an unofficial, fan-made Pokémon project created for educational and entertainment purposes.

Pokémon and all related names, characters, and imagery are trademarks of Nintendo, Game Freak, and The Pokémon Company.

This project is not affiliated with or endorsed by Nintendo, Game Freak, or The Pokémon Company.

## 👨‍💻 About the Project

This project was developed as a way to combine an interest in Pokémon with practical experience in web development and programming.

It demonstrates the use of JavaScript for interactive gameplay, JSON for structured data management, and HTML/CSS for creating a functional user interface.
