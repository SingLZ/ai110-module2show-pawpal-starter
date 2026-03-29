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