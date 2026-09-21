# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose:** Glitchy Guesser is a Streamlit number-guessing game. The app picks a secret number in a range set by the chosen difficulty (Easy 1–20, Normal 1–100, Hard 1–50), the player submits guesses, and the game returns a "Too High"/"Too Low" hint after each one, tracks a running score, and ends when the player either guesses correctly or runs out of attempts.

**Bugs found:**
1. **Inverted hints** — guessing above the secret told the player to go *higher* (and the reverse for guessing below), the exact opposite of correct feedback.
2. **"New Game" permanently broken after a loss** — clicking New Game reset the attempt counter and picked a new secret, but never reset the game's `status` back to `"playing"`, so the app stayed stuck showing "Game over" forever.
3. **Secret silently changed type every other guess** — on even-numbered attempts the code compared the guess against the secret as a *string* instead of an int, which fell back to lexicographic comparison and gave the wrong verdict for multi-digit numbers (e.g. `"9" > "15"` is `True` as strings).
4. **Off-by-one attempts counter** — attempts initialized to `1` instead of `0`, so "Attempts left" was already wrong on the very first render, before any guess was made.

**Fixes applied:**
1. Swapped the hint messages in `check_guess()` (in both the normal and string-fallback comparison branches) so "Too High" says go LOWER and "Too Low" says go HIGHER.
2. Added `st.session_state.status = "playing"` (and cleared `history`) to the `New Game` button handler so the game actually unlocks after a win or loss.
3. Removed the code that converted the secret to a string on even-numbered attempts — `check_guess` is now always called with the raw integer secret.
4. Initialized `attempts` to `0` instead of `1` so the attempts-remaining display is accurate from the start.
5. Refactored `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` out of `app.py` and into `logic_utils.py`, importing them back into `app.py`.
6. Fixed the starter `pytest` tests (they compared the full `(outcome, message)` tuple `check_guess` returns to a bare string) and added 5 new regression tests targeting each of the four bugs above.

## 📸 Demo Walkthrough

1. App loads on Normal difficulty. Secret is hidden; "Attempts left: 8" is shown before any guess is made.
2. User enters a guess of **40** → game returns **"📈 Go HIGHER!"** (the secret is above 40), and the score updates.
3. User enters a guess of **70** → game returns **"📉 Go LOWER!"** (the secret is below 70), and the score updates again.
4. User enters a guess of **55** → game returns **"📈 Go HIGHER!"**, narrowing the range further.
5. User enters a guess of **62**, which matches the secret → game shows **"🎉 Correct!"**, displays balloons, reports the final score, and the "Make a guess" form locks with a "You already won" message.
6. User clicks **"New Game 🔁"** → a new secret is chosen, attempts reset to 0, and the guess form is unlocked and playable again (previously this step was broken — the app stayed stuck on "Game over").

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

Challenge 1 (Advanced Edge-Case Testing) was completed as part of the bug-fix regression suite — see `tests/test_game_logic.py` for tests covering hint-message correctness (not just the outcome label), the attempts-counter off-by-one, secret type consistency across alternating attempts, and the New Game lockup after a loss.

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.9.0
collected 8 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 12%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 25%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 37%]
tests/test_game_logic.py::test_too_high_hint_tells_player_to_go_lower PASSED [ 50%]
tests/test_game_logic.py::test_too_low_hint_tells_player_to_go_higher PASSED [ 62%]
tests/test_game_logic.py::test_attempts_start_at_zero_before_any_guess PASSED [ 75%]
tests/test_game_logic.py::test_secret_stays_numeric_across_multiple_attempts PASSED [ 87%]
tests/test_game_logic.py::test_new_game_unlocks_play_after_a_loss PASSED [100%]

============================== 8 passed in 1.88s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
