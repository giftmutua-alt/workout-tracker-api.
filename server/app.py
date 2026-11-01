import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    ExerciseSchema, ExerciseDetailSchema,
    WorkoutSchema, WorkoutDetailSchema,
    WorkoutExerciseSchema,
)

app = Flask(__name__)
# DATABASE_URI can be overridden (the tests use an in-memory database)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()
workout_exercise_schema = WorkoutExerciseSchema()


def error(message, status):
    return jsonify({'error': message}), status


@app.errorhandler(ValidationError)
def handle_schema_error(err):
    return jsonify({'errors': err.messages}), 400


@app.errorhandler(ValueError)
def handle_model_error(err):
    # Raised by @validates methods in the models
    return jsonify({'error': str(err)}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    # Raised when a database constraint is violated
    db.session.rollback()
    return jsonify({'error': 'Database constraint violated.', 'detail': str(err.orig)}), 409


@app.route('/')
def index():
    return jsonify({'message': 'Workout API'})


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    return jsonify(workouts_schema.dump(Workout.query.all())), 200


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error(f'Workout {id} not found.', 404)
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error(f'Workout {id} not found.', 404)
    db.session.delete(workout)  # cascades to its WorkoutExercises
    db.session.commit()
    return '', 204


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.all())), 200


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error(f'Exercise {id} not found.', 404)
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = exercise_schema.load(request.get_json(silent=True) or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error(f'Exercise {id} not found.', 404)
    db.session.delete(exercise)  # cascades to its WorkoutExercises
    db.session.commit()
    return '', 204


# ---------- Adding an exercise to a workout ----------

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
           methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error(f'Workout {workout_id} not found.', 404)
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error(f'Exercise {exercise_id} not found.', 404)

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)