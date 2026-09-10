# Schema — PitStop

## Core objects

### Assignment
Purpose: A homework, lesson, or learning task.
Fields:
- id: pitstop.assignment.<uuid>
- student_id
- topic
- content
- status
- progress
- receipt_id

### PracticeSet
Purpose: Generated practice questions or exercises.
Fields:
- id
- assignment_id
- questions
- difficulty
- completed

### Explanation
Purpose: Step-by-step explanation or tutoring response.
Fields:
- id
- assignment_id
- content
- sources
- confidence
- receipt_id

## Status values
- not_started
- in_progress
- completed
- needs_review

## IDs
pitstop.assignment.<uuid>
pitstop.practice.<uuid>

## Events
- pitstop.assignment.created
- pitstop.practice.generated
- pitstop.progress.updated
- pitstop.explanation.provided

## Permissions
- Student viewing own work: user_read
- Teacher/admin actions: operator_approval_required
- Storing sensitive student data: strict review

## Data retention
Progress and explanations kept with receipts. Sensitive student data minimized.