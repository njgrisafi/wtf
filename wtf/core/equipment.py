'''
wtf.core.equipment

Equipment Recipes have the following properties:
  * id: the recipe's UUID (Universally Unique Identifier)
  * name: (customizable) equipment name
  * description: (customizable) equipment description
  * weight.center: weight interval center
  * weight.radius: weight interval radius
    > minimum weight = weight.center - weight.radius
    > maximum weight = weight.center + weight.radius

Equipment have the following properties:
  * id: the equipment's UUID (Universally Unique Identifier)
  * recipe: the recipe used to generate this equipment
  * name: (customizable) equipment name
  * description: (customizable) equipment description
  * grade: a value from 0.0 to 1.0 that measures the quality of the equipment
    > The higher this value, the "better" the equipment
'''
import numpy as np
from wtf.core import util
from wtf.core.errors import ValidationError


def create_recipe(**kwargs):
    '''Create an equipment recipe.'''
    weight = kwargs.get('weight', {})
    return {
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'weight': {
            'center': weight.get('center', None),
            'radius': weight.get('radius', None)
        }
    }


def create(**kwargs):
    '''Create a piece of equipment.'''
    return {
        'recipe': kwargs.get('recipe'),
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'grade': kwargs.get('grade', generate_grade())
    }


def generate_grade(probabilities=None):
    '''Generate a random equipment grade.'''
    if probabilities is None:
        probabilities = grade_probabilities()
    choices = np.arange(0.0, 1.0, 0.1) + np.random.uniform(0.0, 0.1)
    return np.random.choice(choices, p=probabilities)


def grade_probabilities():
    '''Get equipment grade probabilities.'''
    dist = [pow(10, i) for i in range(10, 0, -1)]
    total = sum(dist)
    return [i / total for i in dist]


def validate_recipe(recipe):
    '''Validate an equipment recipe.

    Raises a ValidationError if the provided recipe is invalid.
    '''
    errors = []
    if recipe.get('id') is None:
        errors.append('Missing required field: id')
    if recipe.get('name') is None:
        errors.append('Missing required field: name')
    if recipe.get('description') is None:
        errors.append('Missing required field: description')
    weight = recipe.get('weight', {})
    weight_center = weight.get('center')
    weight_radius = weight.get('radius')
    if None in [weight_center, weight_radius]:
        if weight_center is None:
            errors.append('Missing required field: weight.center')
        if weight_radius is None:
            errors.append('Missing required field: weight.radius')
    elif weight_center - weight_radius < 0:
        errors.append('Weight must be >= 0')
    if errors:
        raise ValidationError(errors=errors)


def validate_recipe_min_max_field(recipe, field_name):
    '''Validate a field in an equipment recipe with a min/max value.

    Raises a ValidationError if the field with the provided name is invalid.
    '''
    errors = []
    field = recipe.get(field_name, {})
    field_min = field.get('min', {})
    field_min_center = field_min.get('center')
    field_min_radius = field_min.get('radius')
    if None in [field_min_center, field_min_radius]:
        if field_min_center is None:
            errors.append('Missing required field: %s.min.center' % field_name)
        if field_min_radius is None:
            errors.append('Missing required field: %s.min.radius' % field_name)
    elif field_min_center - field_min_radius <= 0:
        errors.append('Min %s must be > 0' % field_name)
    field_max = field.get('max', {})
    field_max_center = field_max.get('center')
    field_max_radius = field_max.get('radius')
    if None in [field_max_center, field_max_radius]:
        if field_max_center is None:
            errors.append('Missing required field: %s.max.center' % field_name)
        if field_max_radius is None:
            errors.append('Missing required field: %s.max.radius' % field_name)
    elif field_max_center - field_max_radius <= 0:
        errors.append('Max %s must be > 0' % field_name)
    min_lte_max = (
        None not in [
            field_min_center,
            field_min_radius,
            field_max_center,
            field_max_radius
        ]
        and (
            field_max_center < field_min_center
            or util.interval_intersect(field_min, field_max) is not None
        )
    )
    if min_lte_max:
        error = 'Min {0} must be <= max {0} for all values'.format(field_name)
        errors.append(error)
    if errors:
        raise ValidationError(errors=errors)


def validate(equipment):
    '''Validate a piece of equipment.

    Raises a ValidationError if the provided equipment is invalid.
    '''
    errors = []
    if equipment.get('id') is None:
        errors.append('Missing required field: id')
    grade = equipment.get('grade')
    if grade is None:
        errors.append('Missing required field: grade')
    elif not 0 < grade < 1:
        errors.append('Equipment grade must be >= 0.0 and <= 1.0')
    if errors:
        raise ValidationError(errors=errors)


def transform(equipment, recipe):
    '''Transform a piece of eqiupment's fields.

    The following transformations will be performed:
      - name and description: defaulted to recipe values if None
      - weight: derived from recipe and grade, rounded to 2 decimal places
      - grade: replaced with +0 to +9 form
    '''
    equipment = equipment.copy()
    name = equipment.get('name') or recipe.get('name')
    description = equipment.get('description') or recipe.get('description')
    grade = equipment.get('grade', 0.0)
    weight = util.interval_grade_value(recipe.get('weight', {}), (1 - grade))
    equipment.update({
        'name': name,
        'description': description,
        'grade': '+%s' % int(grade * 10),
        'weight': round(weight, 2)
    })
    return equipment
