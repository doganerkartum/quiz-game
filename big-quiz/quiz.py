# quiz.py — Pygame Zero (pgzrun)
# Run: pgzrun quiz.py  (or: python -X utf8 -m pgzero quiz.py)
#
# NOTE for IDEs:
# Pygame Zero injects globals like `screen` and `clock` at runtime via `pgzrun`.
# Static analyzers may show 'unresolved reference' warnings for them — this is normal.

import pgzrun
import pygame
from typing import TYPE_CHECKING, Any
from pgzero.builtins import Rect  # 'screen' provided at runtime

if TYPE_CHECKING:
    screen: Any
    clock: Any

# ------------- Window / Theme -------------
WIDTH, HEIGHT = 900, 600
COL = {
    "bg": (18, 20, 24),
    "panel": (28, 31, 38),
    "shadow": (10, 10, 12),
    "brand": (90, 200, 250),
    "panel2": (38, 42, 50),
    "answer": (60, 66, 78),
    "answer_hover": (85, 130, 255),
    "answer_text": (240, 244, 248),
    "timer_bar": (255, 90, 120),
    "ok": (80, 210, 120),
    "bad": (230, 90, 90),
    "muted": (150, 158, 168),
    "white": (255, 255, 255),
    "green": (65, 190, 120),
    "red": (230, 90, 90),
}

# ------------- Layout -------------
PADDING = 28
CONTENT_W = WIDTH - PADDING * 2
TOP_H = 70
QUESTION_H = 120
ANS_H = 66
GAP = 18

top_bar = Rect((PADDING, PADDING), (CONTENT_W, TOP_H))
q_box   = Rect((PADDING, top_bar.bottom + GAP), (CONTENT_W, QUESTION_H))
grid_y  = q_box.bottom + GAP
a_boxes = [
    Rect((PADDING,                         grid_y),               (CONTENT_W//2 - GAP//2, ANS_H)),
    Rect((PADDING + CONTENT_W//2 + GAP//2, grid_y),               (CONTENT_W//2 - GAP//2, ANS_H)),
    Rect((PADDING,                         grid_y + ANS_H + GAP), (CONTENT_W//2 - GAP//2, ANS_H)),
    Rect((PADDING + CONTENT_W//2 + GAP//2, grid_y + ANS_H + GAP), (CONTENT_W//2 - GAP//2, ANS_H)),
]
FOOTER_H = 44
footer = Rect((PADDING, a_boxes[-1].bottom + GAP), (CONTENT_W, FOOTER_H))

# ------------- Data -------------
questions = [
    ["What is the capital of France?", "London", "Berlin", "Paris", "Tokyo", 3],
    ["2 + 2 = ?", "3", "4", "5", "6", 2],
    ["Color of the sky?", "Blue", "Green", "Red", "Yellow", 1],
    ["Python is a ...", "Snake", "Language", "Both", "Neither", 3],
    ["Which is even?", "7", "9", "11", "12", 4],
]

# answers_log item:
# { "q": str, "opts":[A,B,C,D], "correct":int, "chosen":int|0, "is_ok":bool }
answers_log = []

# ------------- State -------------
score = 0
q_index = 0
time_total = 12.0
time_left = float(time_total)
hover_idx = 0

# phases: "start" -> "playing" -> ("advancing"/"finishing") -> "results"
phase = "start"
feedback = None            # "ok"/"bad"/None
flash_timer = 0.0          # seconds for green/red overlay

# start screen pulse
pulse_t = 0.0

# ------------- Helpers -------------
def rounded_rect(rect: Rect, color, radius=12, surface=None):
    surf = surface or screen.surface
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_shadow(rect: Rect, offset=3):
    r = Rect((rect.x+offset, rect.y+offset), rect.size)
    pygame.draw.rect(screen.surface, COL["shadow"], r, border_radius=14)

def text(s, size, color, center=None, topleft=None, bold=False):
    font = pygame.font.SysFont("segoe ui", size, bold=bold)
    surf = font.render(s, True, color)
    rect = surf.get_rect()
    if center: rect.center = center
    if topleft: rect.topleft = topleft
    screen.surface.blit(surf, rect)
    return rect

def current_question():
    return questions[q_index]

def set_phase(s):
    global phase
    phase = s

# ------------- Flow -------------
def reset_quiz():
    global score, q_index, time_left, feedback, flash_timer, answers_log
    answers_log = []
    score = 0
    q_index = 0
    time_left = float(time_total)
    feedback = None
    flash_timer = 0.0
    set_phase("start")

def start_game():
    global time_left, feedback, flash_timer
    answers_log.clear()
    time_left = float(time_total)
    feedback = None
    flash_timer = 0.0
    set_phase("playing")

def record_answer(chosen_idx, is_ok):
    q = current_question()
    answers_log.append({
        "q": q[0],
        "opts": [q[1], q[2], q[3], q[4]],
        "correct": q[5],
        "chosen": chosen_idx,
        "is_ok": is_ok,
    })

def go_flash_and_schedule(last_question: bool):
    global flash_timer
    flash_timer = 0.6
    set_phase("finishing" if last_question else "advancing")

def correct_answer(chosen_idx):
    global score, feedback
    score += 1
    feedback = "ok"
    record_answer(chosen_idx, True)
    go_flash_and_schedule(q_index == len(questions) - 1)

def wrong_or_timeout(chosen_idx=0):
    global feedback
    feedback = "bad"
    record_answer(chosen_idx, False)
    go_flash_and_schedule(q_index == len(questions) - 1)

def next_question():
    global q_index, time_left, feedback
    feedback = None
    q_index += 1
    time_left = float(time_total)
    set_phase("playing")

# ------------- Start Screen -------------
def draw_start_screen():
    screen.fill(COL["bg"])

    # title panel
    panel = Rect((WIDTH//2 - 360, HEIGHT//2 - 180), (720, 300))
    draw_shadow(panel)
    rounded_rect(panel, COL["panel"])

    # title
    text("WELCOME TO", 26, COL["muted"], center=(panel.centerx, panel.y + 60))
    text("BIG QUIZ", 48, COL["white"], center=(panel.centerx, panel.y + 110), bold=True)


    # pulse alpha between 90..180
    import math
    alpha = int(90 + 90 * (0.5 + 0.5 * math.sin(pulse_t)))
    hint_surf = pygame.Surface((panel.width, 40), pygame.SRCALPHA)
    hint_color = (*COL["brand"], alpha)
    font = pygame.font.SysFont("segoe ui", 22)

    # colored underline bar
    pygame.draw.rect(hint_surf, hint_color, (panel.width//2 - 140, 36, 280, 3), border_radius=2)
    screen.surface.blit(hint_surf, (panel.x, panel.y + 135))


    # Start button
    btn = Rect((panel.centerx - 100, panel.bottom - 80), (200, 44))
    rounded_rect(btn, COL["brand"])
    text("Start Game", 24, COL["bg"], center=btn.center)
    globals()["_start_btn"] = btn

# ------------- Results Page -------------
def draw_results_page():
    screen.fill(COL["bg"])
    draw_shadow(top_bar)
    rounded_rect(top_bar, COL["panel"])
    text("RESULTS", 30, COL["white"],
         topleft=(top_bar.x+16, top_bar.y + (top_bar.height-30)//2), bold=True)
    text(f"Score: {score}/{len(answers_log)}", 22, COL["muted"],
         topleft=(top_bar.right-220, top_bar.y + (top_bar.height-22)//2))

    list_rect = Rect((PADDING, top_bar.bottom + GAP), (CONTENT_W, HEIGHT - top_bar.bottom - GAP*3 - 56))
    rounded_rect(list_rect, COL["panel"])

    y = list_rect.y + 16
    for i, rec in enumerate(answers_log, start=1):
        ok = rec["is_ok"]
        color = COL["green"] if ok else COL["red"]
        text(f"{i}. {rec['q']}", 22, COL["white"], topleft=(list_rect.x+16, y)); y += 26
        chosen_idx = rec["chosen"]
        chosen_txt = "(timeout)" if chosen_idx == 0 else rec["opts"][chosen_idx-1]
        text(f"Your answer: {chosen_txt}", 20, color, topleft=(list_rect.x+32, y)); y += 22
        if not ok:
            correct_txt = rec["opts"][rec["correct"]-1]
            text(f"Correct answer: {correct_txt}", 20, COL["muted"], topleft=(list_rect.x+32, y)); y += 22
        pygame.draw.line(screen.surface, COL["panel2"], (list_rect.x+16, y+6), (list_rect.right-16, y+6)); y += 16
        if y > list_rect.bottom - 40: break

    # Buttons: Play Again (go to start)
    btn = Rect((WIDTH//2 - 220, HEIGHT - 64), (200, 44))
    rounded_rect(btn, COL["brand"])
    text("Play Again", 24, COL["bg"], center=btn.center)
    globals()["_replay_btn"] = btn

    # Or start new round immediately
    btn2 = Rect((WIDTH//2 + 20, HEIGHT - 64), (200, 44))
    rounded_rect(btn2, COL["panel2"])
    text("New Round", 24, COL["white"], center=btn2.center)
    globals()["_newround_btn"] = btn2

# ------------- Top/Question/Answers UI -------------
def draw_top_bar_aligned():
    draw_shadow(top_bar)
    rounded_rect(top_bar, COL["panel"])
    title_rect = text("BIG QUIZ", 30, COL["white"],
                      topleft=(top_bar.x+16, top_bar.y + (top_bar.height-30)//2), bold=True)
    score_rect = text(f"Score: {score}", 22, COL["muted"],
                      topleft=(top_bar.right-120, top_bar.y + (top_bar.height-22)//2))
    left = title_rect.right + 24
    right = score_rect.left - 16
    if right > left:
        bar_y = top_bar.y + (top_bar.height-10)//2
        total_w = right - left
        progress = (q_index) / len(questions)
        pygame.draw.rect(screen.surface, COL["panel2"], (left, bar_y, total_w, 10), border_radius=6)
        pygame.draw.rect(screen.surface, COL["brand"],  (left, bar_y, int(total_w*progress), 10), border_radius=6)

def draw():
    if phase == "start":
        draw_start_screen()
        return
    if phase == "results":
        draw_results_page()
        return

    screen.fill(COL["bg"])
    draw_top_bar_aligned()

    # question card
    draw_shadow(q_box)
    rounded_rect(q_box, COL["panel"])
    q = current_question()
    text(q[0], 26, COL["white"], topleft=(q_box.x+20, q_box.y+18))

    # timer
    inner_w = q_box.width - 40
    bar_w = int((time_left / time_total) * inner_w)
    pygame.draw.rect(screen.surface, COL["panel2"], (q_box.x+20, q_box.bottom-26, inner_w, 8), border_radius=4)
    pygame.draw.rect(screen.surface, COL["timer_bar"], (q_box.x+20, q_box.bottom-26, max(0, bar_w), 8), border_radius=4)

    # answers
    for i, box in enumerate(a_boxes, start=1):
        c = COL["answer_hover"] if i == hover_idx else COL["answer"]
        draw_shadow(box); rounded_rect(box, c)
        txt_col = COL["white"] if i == hover_idx else COL["answer_text"]
        text(q[i], 24, txt_col, topleft=(box.x+16, box.y+18))

    # footer
    rounded_rect(footer, COL["panel2"], radius=10)
    text(f"Q {q_index+1}/{len(questions)}", 18, COL["muted"],
         topleft=(footer.x+12, footer.y + (FOOTER_H-18)//2))
    text("Click an answer before time runs out", 18, COL["muted"],
         topleft=(footer.right-360, footer.y + (FOOTER_H-18)//2))

    # flash overlay while transitioning
    if feedback:
        glow = COL["ok"] if feedback == "ok" else COL["bad"]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*glow, 110))
        screen.surface.blit(overlay, (0, 0))

# ------------- Input -------------
def on_mouse_move(pos):
    if phase != "playing":
        return
    global hover_idx
    hover_idx = 0
    for i, box in enumerate(a_boxes, start=1):
        if box.collidepoint(pos):
            hover_idx = i; break

def on_mouse_down(pos):
    if phase == "start":
        # Start button
        if "_start_btn" in globals() and globals()["_start_btn"].collidepoint(pos):
            start_game()
        return

    if phase == "results":
        # Play Again -> go back to start screen
        if "_replay_btn" in globals() and globals()["_replay_btn"].collidepoint(pos):
            reset_quiz()
            return
        # New Round -> start immediately (keep same questions order)
        if "_newround_btn" in globals() and globals()["_newround_btn"].collidepoint(pos):
            # reset counters but keep phase to playing
            global score, q_index, time_left, feedback, flash_timer
            score = 0
            q_index = 0
            time_left = float(time_total)
            feedback = None
            flash_timer = 0.0
            set_phase("playing")
            answers_log.clear()
            return
        return

    # playing
    if phase != "playing" or time_left <= 0 or feedback:
        return
    for i, box in enumerate(a_boxes, start=1):
        if box.collidepoint(pos):
            if i == current_question()[5]:
                correct_answer(i)
            else:
                wrong_or_timeout(i)
            break

# ------------- Update / Timers -------------
def tick():
    global time_left, flash_timer, feedback, phase, pulse_t

    # start screen pulse
    if phase == "start":
        pulse_t += 0.05
        return

    # timer while playing
    if phase == "playing" and not feedback:
        time_left = max(0.0, time_left - 0.05)
        if time_left <= 0:
            wrong_or_timeout(0)

    # flash countdown and transitions
    if flash_timer > 0.0:
        flash_timer = max(0.0, flash_timer - 0.05)
        if flash_timer == 0.0:
            if phase == "advancing":
                feedback = None
                next_question()
            elif phase == "finishing":
                feedback = None
                set_phase("results")

clock.schedule_interval(tick, 0.05)

pgzrun.go()
