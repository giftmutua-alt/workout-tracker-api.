#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    # Clear tables (children first) so re-running never duplicates data
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    squat = Exercise(name='Squat', category='Strength', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    run = Exercise(name='Running', category='Cardio', equipment_needed=False)
    db.session.add_all([squat, pushup, plank, run])

    w1 = Workout(date=date(2025, 1, 6), duration_minutes=45, notes='Leg day')
    w2 = Workout(date=date(2025, 1, 8), duration_minutes=30, notes='Bodyweight circuit')
    w3 = Workout(date=date(2025, 1, 10), duration_minutes=60)
    db.session.add_all([w1, w2, w3])
    db.session.commit()

    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=w1, exercise=plank, duration_seconds=60),
        WorkoutExercise(workout=w2, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=w2, exercise=plank, duration_seconds=45),
        WorkoutExercise(workout=w3, exercise=run, duration_seconds=1800),
        WorkoutExercise(workout=w3, exercise=squat, reps=8, sets=3),
    ])
    db.session.commit()
    print('Database seeded.')