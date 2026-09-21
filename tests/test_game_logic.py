from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from logic_utils import check_guess


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Bug fix regression tests ---

def test_too_high_hint_tells_player_to_go_lower():
    # Regression test: hint direction used to be inverted. Guessing above
    # the secret must tell the player to go LOWER, never HIGHER.
    outcome, message = check_guess(60, 50)
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_hint_tells_player_to_go_higher():
    # Regression test: hint direction used to be inverted. Guessing below
    # the secret must tell the player to go HIGHER, never LOWER.
    outcome, message = check_guess(40, 50)
    assert "HIGHER" in message
    assert "LOWER" not in message


def test_attempts_start_at_zero_before_any_guess():
    # Regression test: st.session_state.attempts used to initialize to 1,
    # undercounting "Attempts left" before the player had guessed at all.
    with patch("random.randint", return_value=50):
        at = AppTest.from_file("app.py")
        at.run()
        assert at.session_state["attempts"] == 0


def test_secret_stays_numeric_across_multiple_attempts():
    # Regression test: the secret used to be converted to a string on every
    # even-numbered attempt, causing lexicographic (wrong) comparisons for
    # multi-digit numbers, e.g. "9" > "15" is True as strings. Guessing 9
    # against secret 15 must say "Go HIGHER!" on every attempt, not just odd ones.
    with patch("random.randint", return_value=15):
        at = AppTest.from_file("app.py")
        at.run()

        at.text_input[0].input("9")
        at.button[0].click().run()
        assert at.warning[-1].value == "Go HIGHER!"

        at.text_input[0].input("9")
        at.button[0].click().run()
        assert at.warning[-1].value == "Go HIGHER!"


def test_new_game_unlocks_play_after_a_loss():
    # Regression test: "New Game" used to reset attempts/secret but never
    # reset status back to "playing", so the app stayed permanently stuck
    # on "Game over" after any loss.
    with patch("random.randint", return_value=50):
        at = AppTest.from_file("app.py")
        at.run()

        attempt_limit = 8
        for _ in range(attempt_limit):
            at.text_input[0].input("1")
            at.button[0].click().run()

        assert at.session_state["status"] == "lost"

        at.button[1].click().run()

        assert at.session_state["status"] == "playing"
        assert at.session_state["attempts"] == 0
        assert len(at.error) == 0
