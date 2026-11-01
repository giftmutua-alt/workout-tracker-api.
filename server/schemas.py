from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='name must be 1-100 characters.'),
    )
    category = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50, error='category must be 1-50 characters.'),
    )
    equipment_needed = fields.Bool(load_default=False)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1, error='duration_minutes must be at least 1.'),
    )
    notes = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=500, error='notes must be 500 characters or fewer.'),
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(load_default=None, allow_none=True, strict=True,
                      validate=validate.Range(min=1, error='reps must be at least 1.'))
    sets = fields.Int(load_default=None, allow_none=True, strict=True,
                      validate=validate.Range(min=1, error='sets must be at least 1.'))
    duration_seconds = fields.Int(load_default=None, allow_none=True, strict=True,
                                  validate=validate.Range(min=1, error='duration_seconds must be at least 1.'))

    # Read-only nested data used in responses
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)

    @validates_schema
    def validate_measure(self, data, **kwargs):
        """Require reps+sets, or a duration (mirrors the DB check constraint)."""
        has_reps_sets = data.get('reps') is not None and data.get('sets') is not None
        has_duration = data.get('duration_seconds') is not None
        if not (has_reps_sets or has_duration):
            raise ValidationError(
                'Provide both reps and sets, or duration_seconds.', field_name='_schema'
            )


class WorkoutDetailSchema(WorkoutSchema):
    """Workout plus its exercises, including reps/sets/duration."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True, exclude=('workout',)
    )


class ExerciseDetailSchema(ExerciseSchema):
    """Exercise plus the workouts it appears in."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True, exclude=('exercise',)
    )