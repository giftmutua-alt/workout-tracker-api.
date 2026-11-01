import os
import unittest

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from app import app, db  # noqa: E402
from models import Exercise, Workout, WorkoutExercise  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402


class WorkoutAPITests(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

    def make_workout(self):
        return self.client.post('/workouts', json={'date': '2025-01-06', 'duration_minutes': 30}).get_json()

    def make_exercise(self, name='Squat'):
        return self.client.post('/exercises', json={'name': name, 'category': 'Strength'}).get_json()

    # --- model validations ---
    def test_model_rejects_blank_name(self):
        with self.assertRaises(ValueError):
            Exercise(name='  ', category='Core')

    def test_model_rejects_negative_duration(self):
        with self.assertRaises(ValueError):
            Workout(duration_minutes=-5)

    # --- table constraints ---
    def test_unique_exercise_name(self):
        db.session.add_all([Exercise(name='A', category='x'), Exercise(name='A', category='y')])
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_workout_exercise_needs_measure(self):
        w = Workout(date=__import__('datetime').date(2025, 1, 1), duration_minutes=10)
        e = Exercise(name='B', category='x')
        db.session.add(WorkoutExercise(workout=w, exercise=e))
        with self.assertRaises(IntegrityError):
            db.session.commit()

    # --- endpoints / schema validations ---
    def test_create_and_get_workout(self):
        w = self.make_workout()
        self.assertEqual(self.client.get(f"/workouts/{w['id']}").status_code, 200)
        self.assertEqual(len(self.client.get('/workouts').get_json()), 1)

    def test_workout_schema_rejects_bad_data(self):
        r = self.client.post('/workouts', json={'date': 'nope', 'duration_minutes': 0})
        self.assertEqual(r.status_code, 400)

    def test_add_exercise_to_workout(self):
        w, e = self.make_workout(), self.make_exercise()
        url = f"/workouts/{w['id']}/exercises/{e['id']}/workout_exercises"
        self.assertEqual(self.client.post(url, json={'reps': 10, 'sets': 3}).status_code, 201)
        detail = self.client.get(f"/workouts/{w['id']}").get_json()
        self.assertEqual(detail['workout_exercises'][0]['exercise']['name'], 'Squat')
        self.assertEqual(self.client.post(url, json={'reps': 10, 'sets': 3}).status_code, 409)

    def test_schema_requires_measure(self):
        w, e = self.make_workout(), self.make_exercise()
        url = f"/workouts/{w['id']}/exercises/{e['id']}/workout_exercises"
        self.assertEqual(self.client.post(url, json={'reps': 10}).status_code, 400)

    def test_delete_cascades(self):
        w, e = self.make_workout(), self.make_exercise()
        self.client.post(f"/workouts/{w['id']}/exercises/{e['id']}/workout_exercises", json={'duration_seconds': 30})
        self.assertEqual(self.client.delete(f"/exercises/{e['id']}").status_code, 204)
        self.assertEqual(WorkoutExercise.query.count(), 0)
        self.assertEqual(self.client.delete(f"/workouts/{w['id']}").status_code, 204)
        self.assertEqual(self.client.get(f"/workouts/{w['id']}").status_code, 404)


if __name__ == '__main__':
    unittest.main()