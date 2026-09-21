# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game, it looked normal on the surface — title, sidebar difficulty settings, a text input, and a Submit/New Game/hint checkbox row. But as soon as I started actually playing, the feedback stopped making sense, and once I lost a round the whole app got stuck. Reading through `app.py` turned up several concrete bugs:

- **Hint direction is inverted.** In `check_guess()`, when the guess is greater than the secret, the outcome is labeled `"Too High"` but the message told me to go **higher** (and the reverse for `"Too Low"`). Expected: guessing above the secret tells me to go lower. Actual: guessing above the secret told me to go higher, and vice versa — the exact opposite of correct behavior.
- **"New Game" doesn't actually restart the game.** Clicking New Game resets `attempts` and picks a new `secret`, but never resets `status` back to `"playing"`. Expected: after losing, clicking New Game lets me play again. Actual: once `status` was set to `"lost"`, the app permanently showed "Game over" on every rerun, even after New Game was clicked, because the code checks `status` before anything else and calls `st.stop()`.
- **The secret's type flips between int and string every other guess.** On even-numbered attempts, the code compares my guess against `str(secret)` instead of the integer, which falls into a string-comparison fallback that sorts numbers alphabetically instead of numerically. Expected: guess comparison is always numeric. Actual: on alternating guesses, multi-digit numbers could get the wrong "higher/lower" verdict (e.g. `"9" > "10"` is `True` as strings).
- **Off-by-one on the attempts counter.** `attempts` initializes to `1` instead of `0`, so the very first attempts-remaining display was already wrong before I'd made a single guess.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guessed 1 (secret was higher than 1) | "Go HIGHER" hint | "📉 Go LOWER!" hint shown | none |
| Guessed 100 (secret was lower than 100) | "Go LOWER" hint | "📈 Go HIGHER!" hint shown | none |
| Lost a round (ran out of attempts), then clicked "New Game 🔁" | New round starts, "Make a guess" is playable again | App kept showing "Game over. Start a new game to try again." and stayed stopped, even after New Game was clicked | none (no traceback — silent logic bug in `st.session_state.status` not being reset) |
| On attempt 2 (an even-numbered attempt), guessed a value on the opposite side of a secret like 9 vs. 10 | Correct numeric "higher/lower" hint | Wrong hint due to string comparison of `"9"` vs `"10"` (lexicographic, not numeric) | none |

---

## 2. How did you use AI as a teammate?

I used Claude Code as my AI pair programmer for this whole project — it read the code, proposed fixes, edited the files directly, and drove the browser to test the running app.

**Correct suggestion:** When I reported that the game got permanently stuck on "Game over" after one loss, Claude traced it to the `new_game` block in `app.py`: it reset `attempts` and picked a new `secret`, but never reset `st.session_state.status` back to `"playing"`, so the `st.stop()` check right below it kept firing forever. Claude's fix added `st.session_state.status = "playing"` (and, while it was in there, cleared `history` too for a clean restart). I verified this myself by watching Claude drive the browser through a real lose → click "New Game" → play-again cycle, and later confirmed it again with an automated test (`test_new_game_unlocks_play_after_a_loss`) that forces a loss and asserts the app is playable afterward.

**Incorrect/misleading suggestion:** When Claude wrote the regression test for the secret-type-flip bug, its first draft asserted the hint message equaled `"📈 Go HIGHER!"` (with the emoji included, matching the literal string in `check_guess`). Running `pytest` immediately failed with `AssertionError: assert 'Go HIGHER!' == '📈 Go HIGHER!'` — it turned out Streamlit's `AppTest.warning[...].value` strips the emoji icon since it's rendered as a separate icon, not part of the text value. So the suggestion was technically wrong about what the test API returns, not about the underlying bug fix. I had Claude fix the assertion to compare against `"Go HIGHER!"` without the emoji, reran `pytest`, and confirmed all 8 tests passed. This was a good reminder that even AI-written tests need to actually be run, not just read, before trusting them.

---

## 3. Debugging and testing your fixes

I considered a bug "really fixed" only after two things lined up: (1) reproducing the exact broken behavior live in the browser before the fix, and (2) re-running that same scenario after the fix and seeing the correct result — not just reading the diff and assuming it worked. For every fix (inverted hints, the New Game lockup, the int/string secret flip, and the off-by-one attempts counter), Claude drove the Streamlit app in the browser, opened the "Developer Debug Info" panel to read the actual `secret`/`attempts`/`status` values, submitted guesses, and showed me the before/after hint text and session state directly.

For automated testing, I ran `pytest tests/ -v` and it showed **8 passed** — the 3 original starter tests (once fixed to unpack the `(outcome, message)` tuple `check_guess` actually returns, since they'd been comparing the whole tuple to a bare string) plus 5 new regression tests: two that check the hint *message* text (not just the outcome label) for the too-high/too-low cases, one asserting `attempts` starts at `0`, one that guesses the same value twice in a row against a mocked secret to confirm the hint stays consistent across even/odd attempts, and one that forces a full loss and checks that "New Game" actually unlocks play again.

AI helped design all of these tests. Claude used `streamlit.testing.v1.AppTest` (a Streamlit test harness) to simulate button clicks and text input without a real browser, and `unittest.mock.patch("random.randint", ...)` to pin the secret to a known value so the tests would be deterministic instead of flaky. I wouldn't have known `AppTest` existed on my own — Claude prototyped it in a scratch script first to check the API (how `.button[i].click()` and `.session_state[...]` work) before writing the real test file, which is also how it caught the emoji-stripping issue from the example above.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
