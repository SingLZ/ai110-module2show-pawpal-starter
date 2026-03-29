# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I designed four classes: Owner (holds user info and a list of pets), Pet (stores animal details and any special care needs), Task (represents a single care action with a type, time, duration, and priority), and Scheduler (the central logic class that manages and prioritizes tasks for an owner). The relationships flow from Owner → Pet → Task, with Scheduler operating across all tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Design did not change during implementation.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers due time (tasks sorted chronologically), priority (1 = most urgent first), and today's date (only shows tasks due today). Priority was chosen as the primary sort key because a high-priority overdue medication matters more than a low-priority walk at the same time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler doesn't check for time conflicts — two tasks can overlap. This is a reasonable tradeoff because for a pet care app, the user is the one executing tasks and can adapt.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I use AI tools for debugging test and also for readability. I think the more specific the prompts are the more helpful the ai gets.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Copilot generated get_all_tasks() using a nested loop with instead of a list comprehension, and I did not accept that. I verified the output was identical by running main.py and checking the task count matched.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The four tests above cover task completion state change, task count growth, overdue detection logic, and date filtering in the scheduler. These matter because the scheduler's correctness depends entirely on these building blocks being reliable.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

★★★★☆ — the happy paths and most edge cases are covered. The main gap is
that tests use `datetime.now()`, making them fragile near midnight. Given
more time I would add `freezegun` to pin time to a fixed value, and test
the Streamlit session state behavior with `st.testing`.


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The separation between `pawpal_system.py` and `app.py` worked well from the
start. Because all logic lived in the backend, I could verify every feature
in `main.py` before touching the UI, and every method was independently
testable. That boundary also made it easy to identify when Copilot was
putting logic in the wrong place.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add a persistent data layer (even just JSON file storage) so the
schedule survives a page refresh. Right now all data lives in
`st.session_state` and is lost when the browser tab closes. I would also
redesign `Task` to store a `Pet` reference instead of just `pet_name: str`,
which would make filtering cleaner and eliminate the `next(p for p in ...)` 
lookups scattered through the code.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI is a fast and capable
*implementer* but a poor *architect*. Copilot could generate a sorting
function or a test stub in seconds, but it had no opinion about whether
conflict detection belonged in `Task`, `Pet`, or `Scheduler` — and putting
it in the wrong place would have made the code harder to test and maintain.
Every structural decision required human judgment. The AI amplified my
output; it didn't replace my thinking.


## Prompt Comparison: OpenAI GPT-4o vs Claude

**Task given to both models:**
"Write a Python method for a Scheduler class that, given a duration in minutes
and a pet name, finds the next available time slot in that pet's schedule today
with no conflicts."

---

**GPT-4o approach** (summarized):
Returned a solution using a `while` loop that incremented a `candidate` time
by 15-minute steps and checked each against all existing tasks. It worked, but
the step-based search meant it could miss a slot that started mid-increment,
and the loop had no clear upper bound — it would run indefinitely if the day
was fully booked.

**Claude approach** (summarized):
Returned a solution that sorted existing tasks first, then walked the sorted
list once looking for a gap large enough to fit the new task. It returned
immediately when a gap was found, and naturally terminated at the end of the
task list. No loop with an arbitrary step size, no infinite-loop risk.

---

**Verdict:**
Claude's version was more algorithmically sound — O(n log n) for the sort
then O(n) for the scan, compared to GPT-4o's potentially unbounded step loop.
Claude's version was also easier to reason about: "find a gap in a sorted
list" is a clearer mental model than "keep guessing times until one works."

The GPT-4o version had better inline comments explaining each step, which
would have been helpful for a less experienced reader. In practice I used
Claude's algorithm with GPT-4o's commenting style — the most useful output
came from combining both, not picking one wholesale.

**Key insight:** Neither model got the edge case right on the first try —
both assumed the pet had at least one existing task. I added the "no existing
tasks → return `search_from` immediately" branch myself after noticing the
gap. AI suggestions still require human review of edge cases.
