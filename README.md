# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend for a workout tracking app used by personal trainers.
Trainers can create workouts and reusable exercises, then attach exercises to workouts with
reps/sets or a duration.

## Installation

```bash
pipenv install
pipenv shell
cd server
flask db init            # only the first time
flask db migrate -m "create tables"
flask db upgrade head
python seed.py
```

Set `FLASK_APP=app.py` if the `flask` command can't find the app (`export FLASK_APP=app.py`).

## Run

```bash
cd server
flask run -p 5555     # or: python app.py
```

Run the tests with `python -m unittest test_app.py` from `server/`.

## Data model

- **Exercise**: `name` (unique), `category`, `equipment_needed`
- **Workout**: `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join): `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show a workout with its exercises, including reps/sets/duration |
| POST | `/workouts` | Create a workout (`date` as YYYY-MM-DD, `duration_minutes`, optional `notes`) |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show an exercise and the workouts it appears in |
| POST | `/exercises` | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with `reps` + `sets`, or `duration_seconds` |

Errors return JSON: `400` for validation failures, `404` for missing records, `409` for
constraint violations (e.g. adding the same exercise to a workout twice).

## Validations

- **Table constraints**: unique exercise name; non-blank name/category; positive duration/reps/sets;
  a WorkoutExercise needs reps+sets or a duration; unique (workout, exercise) pair.
- **Model validations** (`@validates`): non-empty strings, positive integers, notes length.
- **Schema validations** (Marshmallow): length and range checks, date format, and a schema-level
  check that reps+sets or duration is provided.