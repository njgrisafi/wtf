'''
wtf.core.weapons

Weapon recipes have the following properties:
  * id: the recipe's UUID (Universally Unique Identifier)
  * type: weapon type
  * name: (customizable) weapon name
  * description: (customizable) weapon description
  * handedness: whether the weapon is one-handed or two-handed
  * weight.center: weight interval center
  * weight.radius: weight interval radius
    > minimum weight = weight.center - weight.radius
    > maximum weight = weight.center + weight.radius
  * damage.min.center: minimum damage interval center
  * damage.min.radius: minimum damage interval radius
    > minimum damage.min = damage.min.center - damage.min.radius
    > maximum damage.min = damage.min.center + damage.min.radius
  * damage.max.center: maximum damage interval center
  * damage.max.radius: maximum damage interval radius
    > minimum damage.max = damage.max.center - damage.max.radius
    > maximum damage.max = damage.max.center + damage.max.radius

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
from wtf.core import util
from wtf.core.errors import NotFoundError, ValidationError


REPO_RECIPES = {'by_id': {}}
REPO = {'by_id': {}}
WEAPON_TYPES = ['sword', 'axe', 'mace', 'dagger', 'bow']


def create_recipe(**kwargs):
    '''Create a weapon recipe.'''
    weight = kwargs.get('weight', {})
    damage = kwargs.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    return {
        'type': kwargs.get('type'),
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'handedness': kwargs.get('handedness', 1),
        'weight': {
            'center': weight.get('center', 0),
            'radius': weight.get('radius', 0)
        },
        'damage': {
            'min': {
                'center': damage_min.get('center', 0),
                'radius': damage_min.get('radius', 0)
            },
            'max': {
                'center': damage_max.get('center', 0),
                'radius': damage_max.get('radius', 0)
            }
        }
    }


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


def save_recipe(recipe):
    '''Create/update a weapon recipe.

    Raises a ValidationError if the recipe is invalid.
    '''
    recipe = recipe.copy()
    if recipe.get('id') is None:
        recipe['id'] = str(uuid4())
    validate_recipe(recipe)
    REPO_RECIPES.get('by_id')[recipe.get('id')] = recipe
    return recipe


def save(weapon):
    '''Create/update a weapon.

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


def validate_recipe(recipe):
    '''Validate a weapon recipe.

    Raises a ValidationError if the provided recipe is invalid.
    '''
    errors = []
    weapon_type = recipe.get('type')
    name = recipe.get('name')
    description = recipe.get('description')
    handedness = recipe.get('handedness')
    if weapon_type is None:
        errors.append('Missing required field: type')
    elif weapon_type not in WEAPON_TYPES:
        errors.append('Invalid weapon type')
    if not name:
        errors.append('Missing required field: name')
    if not description:
        errors.append('Missing required field: description')
    if handedness is None:
        errors.append('Missing required field: handedness')
    elif handedness not in [1, 2]:
        errors.append('Handedness must be either 1 or 2')
    try:
        validate_recipe_weight(recipe)
    except ValidationError as error:
        errors += error.errors
    try:
        validate_recipe_damage(recipe)
    except ValidationError as error:
        errors += error.errors
    if errors:
        raise ValidationError(errors=errors)


def validate_recipe_weight(recipe):
    '''Validate a weapon recipe's weight fields.

    Raises a ValidationError if the recipe's weight fields are invalid.
    '''
    errors = []
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


def validate_recipe_damage(recipe):
    '''Validate a weapon recipe's damage fields.

    Raises a ValidationError if the recipe's damage fields are invalid.
    '''
    errors = []
    recipe_id = recipe.get('id')
    damage = recipe.get('damage', {})
    damage_min = damage.get('min', {})
    damage_min_center = damage_min.get('center')
    damage_min_radius = damage_min.get('radius')
    damage_max = damage.get('max', {})
    damage_max_center = damage_max.get('center')
    damage_max_radius = damage_max.get('radius')
    if recipe_id is None:
        errors.append('Missing required field: id')
    if None in [damage_min_center, damage_min_radius]:
        if damage_min_center is None:
            errors.append('Missing required field: damage.min.center')
        if damage_min_radius is None:
            errors.append('Missing required field: damage.min.radius')
    elif damage_min_center - damage_min_radius <= 0:
        errors.append('Min damage must be > 0')
    if None in [damage_max_center, damage_max_radius]:
        if damage_max_center is None:
            errors.append('Missing required field: damage.max.center')
        if damage_max_radius is None:
            errors.append('Missing required field: damage.max.radius')
    elif damage_max_center - damage_max_radius <= 0:
        errors.append('Max damage must be > 0')
    if (
            None not in [
                damage_min_center,
                damage_min_radius,
                damage_max_center,
                damage_max_radius
            ]
            and (
                damage_max_center < damage_min_center
                or util.interval_intersect(damage_min, damage_max) is not None
            )
        ):
        errors.append('Min damage must always be less than max damage')
    if errors:
        raise ValidationError(errors=errors)


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
            find_recipe_by_id(recipe)
        except NotFoundError as error:
            errors.append(str(error))
    if grade is None:
        errors.append('Missing required field: grade')
    elif not 0 < grade < 1:
        errors.append('Weapon grade must be between 0.0 and 1.0')
    if errors:
        raise ValidationError(errors=errors)


def find_recipe_by_id(recipe_id):
    '''Find a weapon recipe with the provided id.

    Raises a NotFoundError if the recipe could not be found.
    '''
    recipe = REPO_RECIPES.get('by_id').get(recipe_id)
    if recipe is None:
        raise NotFoundError('Weapon recipe not found')
    return recipe


def find_by_id(weapon_id):
    '''Find a weapon with the provided id.

    Raises a NotFoundError if the weapon could not be found.
    '''
    weapon = REPO.get('by_id').get(weapon_id)
    if weapon is None:
        raise NotFoundError('Weapon not found')
    return weapon


def transform(weapon):
    '''Transform weapon fields.

    The following transformations will be performed:
      * type: set to recipe value
      * name and description: defaulted to recipe values if None
      * handedness: set to recipe value
      * grade: replaced with +0 to +9 form
      * weight: derived from recipe and grade, rounded to 2 decimal places
      * damage.min: derived from recipe and grade, rounded to 2 decimal places
      * damage.max: derived from recipe and grade, rounded to 2 decimal places
    '''
    weapon = weapon.copy()
    recipe = find_recipe_by_id(weapon.get('recipe'))
    weapon['type'] = recipe.get('type')
    weapon['handedness'] = recipe.get('handedness')
    if not weapon.get('name'):
        weapon['name'] = recipe.get('name')
    if not weapon.get('description'):
        weapon['description'] = recipe.get('description')
    grade = weapon.get('grade')
    weapon['grade'] = '+%s' % int(grade * 10)
    weight = util.interval_grade_value(recipe.get('weight'), (1 - grade))
    weapon['weight'] = round(weight, 2)
    damage = recipe.get('damage')
    damage_min = util.interval_grade_value(damage.get('min'), grade)
    damage_max = util.interval_grade_value(damage.get('max'), grade)
    weapon['damage'] = {
        'min': round(damage_min, 2),
        'max': round(damage_max, 2)
    }
    return weapon
