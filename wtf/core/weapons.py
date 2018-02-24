'''
wtf.core.weapons

Weapon Recipes have the following properties:
  * id: the recipe's UUID (Universally Unique Identifier)
  * name: (customizable) weapon name
  * description: (customizable) weapon description
  * weight.center: weight interval center
  * weight.radius: weight interval radius
    > minimum weight = weight.center - weight.radius
    > maximum weight = weight.center + weight.radius
  * type: weapon type
  * handedness: whether the weapon is one-handed or two-handed
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
from wtf.core import equipment, util
from wtf.core.errors import NotFoundError, ValidationError


REPO_RECIPES = {'by_id': {}}
REPO = {'by_id': {}}
WEAPON_TYPES = ['sword', 'axe', 'mace', 'dagger', 'bow']


def create_recipe(**kwargs):
    '''Create a weapon recipe.'''
    recipe = equipment.create_recipe(**kwargs)
    damage = kwargs.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    recipe.update({
        'type': kwargs.get('type'),
        'handedness': kwargs.get('handedness', 1),
        'damage': {
            'min': {
                'center': damage_min.get('center', None),
                'radius': damage_min.get('radius', None)
            },
            'max': {
                'center': damage_max.get('center', None),
                'radius': damage_max.get('radius', None)
            }
        }
    })
    return recipe


def create(**kwargs):
    '''Create a weapon.'''
    return equipment.create(**kwargs)


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
    try:
        equipment.validate_recipe(recipe)
    except ValidationError as error:
        errors += error.errors
    weapon_type = recipe.get('type')
    if weapon_type is None:
        errors.append('Missing required field: type')
    elif weapon_type not in WEAPON_TYPES:
        errors.append('Invalid weapon type')
    handedness = recipe.get('handedness')
    if handedness is None:
        errors.append('Missing required field: handedness')
    elif handedness not in [1, 2]:
        errors.append('Handedness must be either 1 or 2')
    try:
        equipment.validate_recipe_min_max_field(recipe, 'damage')
    except ValidationError as error:
        errors += error.errors
    if errors:
        raise ValidationError(errors=errors)


def validate(weapon):
    '''Validate a weapon.

    Raises a ValidationError if the provided weapon is invalid.
    '''
    errors = []
    try:
        equipment.validate(weapon)
    except ValidationError as error:
        errors += error.errors
    recipe = weapon.get('recipe')
    if recipe is None:
        errors.append('Missing required field: recipe')
    else:
        try:
            find_recipe_by_id(recipe)
        except NotFoundError as error:
            errors.append(str(error))
    if errors:
        raise ValidationError(errors=errors)


def find_recipe_by_id(recipe_id):
    '''Find a weapon recipe with the provided id.

    Raises a NotFoundError if the recipe could not be found.
    '''
    recipe = REPO_RECIPES['by_id'].get(recipe_id)
    if recipe is None:
        raise NotFoundError('Weapon recipe not found')
    return recipe


def find_by_id(weapon_id):
    '''Find a weapon with the provided id.

    Raises a NotFoundError if the weapon could not be found.
    '''
    weapon = REPO['by_id'].get(weapon_id)
    if weapon is None:
        raise NotFoundError('Weapon not found')
    return weapon


def transform(weapon):
    '''Transform a weapon's fields.

    The following transformations will be performed:
      - name and description: defaulted to recipe values if None
      - weight: derived from recipe and grade, rounded to 2 decimal places
      - grade: replaced with +0 to +9 form
      - type: set to recipe value
      - handedness: set to recipe value
      - damage.min: derived from recipe and grade, rounded to 2 decimal places
      - damage.max: derived from recipe and grade, rounded to 2 decimal places
    '''
    recipe = find_recipe_by_id(weapon.get('recipe'))
    grade = weapon.get('grade')
    weapon = equipment.transform(weapon, recipe)
    damage = recipe.get('damage')
    damage_min = util.interval_grade_value(damage.get('min'), grade)
    damage_max = util.interval_grade_value(damage.get('max'), grade)
    weapon.update({
        'type': recipe.get('type'),
        'handedness': recipe.get('handedness'),
        'damage': {
            'min': round(damage_min, 2),
            'max': round(damage_max, 2)
        }
    })
    return weapon
