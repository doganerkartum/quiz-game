# Quiz Game 🎯

A small quiz game built with **Python** using **Pygame Zero**.

This project was created as a practice project to learn:
- basic game loops
- simple UI handling
- user input
- game states (start screen, gameplay, results screen)

---

## 🛠 Technologies Used

- Python 3
- Pygame
- Pygame Zero (`pgzero`)

---

## ▶️ How to Run

Make sure you have Python installed, then install the required libraries:
```
pip install pygame pgzero
```

Run the game from the project root:
```
pgzrun big-quiz/quiz.py
```

On Windows, if you get encoding errors, you can use:
```
python -X utf8 -m pgzero big-quiz/quiz.py
```

🧠 IDE Note (Why you may see red underlines)

Pygame Zero’s runner (pgzrun) injects globals like screen and clock at runtime.
Static analyzers can’t see them, so your IDE may show “unresolved reference” warnings. That’s normal; the game still runs fine from the terminal.

If you want to silence the IDE warnings, add this to the top of quiz.py:
```
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    screen: Any
    clock: Any
```
