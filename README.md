# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes several algorithms beyond basic task listing:

- **Sorting**: Tasks are ordered by due time using a lambda key on `datetime` objects.
- **Filtering**: Tasks can be filtered by pet name or completion status.
- **Recurring tasks**: Marking a daily or weekly task complete automatically
  schedules the next occurrence using `timedelta`.
- **Conflict detection**: The scheduler scans today's tasks and warns when two
  tasks for the same pet overlap in time, based on start time + duration.

  ## Testing PawPal+

Run the full test suite with:

    python -m pytest

The suite covers 27 tests across five areas:

- **Task behavior**: completion status, overdue detection, recurrence (daily/weekly)
- **Pet management**: task addition, pending-task filtering, empty-pet edge cases
- **Owner logic**: multi-pet task flattening, no-pet edge case
- **Scheduler sorting**: chronological ordering, all tasks preserved
- **Scheduler filtering**: by pet name, by completion status, nonexistent pet
- **Conflict detection**: exact overlap, duration overlap, cross-pet (not flagged), no tasks

**Confidence level: ★★★★☆**

The core logic is well-covered. The main gap is that tests run against today's
date, so time-sensitive edge cases (e.g., tasks at midnight) aren't explicitly
tested.

## 📸 Demo

<a href="/app_ui.png" target="_blank">
  <img src='/app_ui.png' title='PawPal App'
       width='' alt='PawPal App' class='center-block' />
</a>

## ✨ Features

- **Add pets and tasks** with species, age, special needs, due time, duration, and priority
- **Smart sorting** — tasks ordered chronologically using `datetime` comparison
- **Priority scheduling** — pending tasks ranked by urgency, then time
- **Recurring tasks** — daily and weekly tasks auto-reschedule on completion using `timedelta`
- **Conflict detection** — warns when two tasks for the same pet overlap in duration
- **Live filters** — filter today's schedule by pet or completion status
- **Overdue alerts** — tasks past their due time are flagged with a red indicator
- **Summary metrics** — see total, completed, and overdue counts at a glance

## 🏗 Architecture

Four core classes in `pawpal_system.py`:

- `Task` — a single care activity with type, time, duration, priority, and recurrence
- `Pet` — holds pet details and a list of tasks
- `Owner` — manages multiple pets and exposes all tasks as a flat list
- `Scheduler` — the logic layer: sorts, filters, detects conflicts, handles recurrence

See `uml_final.png` for the full class diagram.

## 🚀 Running the App
```bash
pip install streamlit
streamlit run app.py
```


## 🧩 Optional Extensions

### Challenge 1 — Smart scheduling algorithms
Two new `Scheduler` methods beyond basic sorting:
- `find_next_available_slot(duration, pet_name)` — scans today's tasks for
  the earliest gap that fits a new task of the given duration
- `smart_prioritize()` — scores tasks by priority, overdue status, and
  recurrence to produce a weighted ranked list

### Challenge 2 — Data persistence
`Owner.save_to_json()` and `Owner.load_from_json()` serialize the full
object graph (owner → pets → tasks) to `data.json` using Python's built-in
`json` module. The app auto-saves on every change and auto-loads on startup.

### Challenge 3 — Priority color coding
Tasks display color-coded priority badges (🔴 Critical → ⚪ Minimal) and
task-type icons (🦮 walk, 🍖 feed, 💊 medicate, ✂️ groom) in the UI.
The schedule view switches to `smart_prioritize()` when filtering for
pending tasks.

### Challenge 4 — Formatted CLI output
`main.py` uses `tabulate` with `rounded_outline` formatting to print a
structured, readable schedule table in the terminal.

### Challenge 5 — Multi-model comparison
See the Prompt Comparison section in `reflection.md` for a side-by-side
analysis of GPT-4o vs Claude on the next-available-slot algorithm.