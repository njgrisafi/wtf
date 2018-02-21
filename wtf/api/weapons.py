'''
wtf.api.weapons

Weapons have the following properties:
  * id: the weapon's UUID (Universally Unique Identifier)
  * recipe: the recipe used to generate this weapon
  * name: (customizable) weapon name
  * description: (customizable) weapon description
  * grade: a value from 0.0 to 1.0 that measures the quality of the weapon
    > The higher this value, the "better" the weapon
'''
from uuid import uuid4
import numpy as np
from flask import Blueprint, jsonify
from wtf.api import util, weaponrecipes
from wtf.api.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('weapons', __name__)
REPO = {'by_id': {}}


@BLUEPRINT.route('', methods=['POST'])
def handle_post_request():
    '''Handle weapon POST requests.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/weapons \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "recipe": "..."
        }'
    '''
    body = util.get_json_body()
    weapon = save(create(
        recipe=body.get('recipe')
    ))
    return jsonify({'weapon': transform(weapon)}), 201


@BLUEPRINT.route('/<weapon_id>', methods=['GET'])
def handle_get_request(weapon_id):
    '''Handle weapon GET by id requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/weapons/<id> \
        --write-out "\n"
    '''
    weapon = find_by_id(weapon_id)
    return jsonify({'weapon': transform(weapon)}), 200


def create(**kwargs):
    '''Create a weapon.'''
    return {
        'recipe': kwargs.get('recipe'),
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'grade': kwargs.get('grade', generate_grade())
    }


def generate_grade(probabilities=None):
    '''Generate a random weapon grade.'''
    if probabilities is None:
        probabilities = grade_probabilities()
    choices = np.arange(0.0, 1.0, 0.1) + np.random.uniform(0.0, 0.1)
    return np.random.choice(choices, p=probabilities)


def grade_probabilities():
    '''Get weapon grade probabilities.'''
    dist = [pow(10, i) for i in range(10, 0, -1)]
    total = sum(dist)
    return [i / total for i in dist]


def transform(weapon):
    '''Transform weapon fields.

    The following transformations will be performed:
      * name and description: defaulted to recipe values if None
      * grade: replaced with +0 to +9 form
      * weight: derived from recipe and grade, rounded to 2 decimal places
      * damage.min: derived from recipe and grade, rounded to 2 decimal places
      * damage.max: derived from recipe and grade, rounded to 2 decimal places
    '''
    weapon = weapon.copy()
    recipe = weaponrecipes.find_by_id(weapon.get('recipe'))
    if not weapon.get('name'):
        weapon['name'] = recipe.get('name')
    if not weapon.get('description'):
        weapon['description'] = recipe.get('description')
    grade = weapon.get('grade')
    weapon['grade'] = '+%s' % int(grade * 10)
    weight = util.interval_grade_value(
        recipe.get('weight'),
        grade,
        correlation='-'
    )
    weapon['weight'] = round(weight, 2)
    damage = recipe.get('damage')
    damage_min = util.interval_grade_value(damage.get('min'), grade)
    damage_max = util.interval_grade_value(damage.get('max'), grade)
    weapon['damage'] = {
        'min': round(damage_min, 2),
        'max': round(damage_max, 2)
    }
    return weapon


def save(weapon):
    '''Persist a weapon.

    If the weapon already exists, it will be updated; otherwise, it will be
        created.

    Raises a ValidationError if the weapon is invalid.
    '''
    weapon = weapon.copy()
    if weapon.get('id') is None:
        weapon['id'] = str(uuid4())
    validate(weapon)
    REPO.get('by_id')[weapon.get('id')] = weapon
    return weapon


def validate(weapon):
    '''Validate a weapon.

    Raises a ValidationError if the provided weapon is invalid.
    '''
    errors = []
    weapon_id = weapon.get('id')
    recipe = weapon.get('recipe')
    grade = weapon.get('grade')
    if weapon_id is None:
        errors.append('Missing required field: id')
    if recipe is None:
        errors.append('Missing required field: recipe')
    else:
        try:
            weaponrecipes.find_by_id(recipe)
        except NotFoundError as error:
            errors.append(str(error))
    if grade is None:
        errors.append('Missing required field: grade')
    elif not 0 < grade < 1:
        errors.append('Weapon grade must be between 0.0 and 1.0')
    if errors:
        raise ValidationError(errors=errors)


def find_by_id(weapon_id):
    '''Find a weapon with the provided id.

    Raises a NotFoundError if the weapon could not be found.
    '''
    weapon = REPO.get('by_id').get(weapon_id)
    if weapon is None:
        raise NotFoundError('Weapon not found')
    return weapon
