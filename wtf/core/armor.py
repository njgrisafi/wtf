'''
wtf.core.armor

Armor Recipes have the following properties:
  * id: the recipe's UUID (Universally Unique Identifier)
  * name: (customizable) armor name
  * description: (customizable) armor description
  * weight.center: weight interval center
  * weight.radius: weight interval radius
    > minimum weight = weight.center - weight.radius
    > maximum weight = weight.center + weight.radius
  * location: location on the body where the armor is worn
  * defense.min.center: minimum defense interval center
  * defense.min.radius: minimum defense interval radius
    > minimum defense.min = defense.min.center - defense.min.radius
    > maximum defense.min = defense.min.center + defense.min.radius
  * defense.max.center: maximum defense interval center
  * defense.max.radius: maximum defense interval radius
    > minimum defense.max = defense.max.center - defense.max.radius
    > maximum defense.max = defense.max.center + defense.max.radius

Armor have the following properties:
  * id: the armor's UUID (Universally Unique Identifier)
  * recipe: the recipe used to generate this armor
  * name: (customizable) armor name
  * description: (customizable) armor description
  * grade: a value from 0.0 to 1.0 that measures the quality of the armor
    > The higher this value, the "better" the armor
'''
from uuid import uuid4
from wtf.core import equipment, util
from wtf.core.errors import NotFoundError, ValidationError


REPO = {'by_id': {}}
REPO_RECIPES = {'by_id': {}}
ARMOR_LOCATIONS = ['head', 'chest', 'hands', 'legs', 'feet']


def create_recipe(**kwargs):
    '''Create an armor recipe.'''
    recipe = equipment.create_recipe(**kwargs)
    defense = kwargs.get('defense', {})
    defense_min = defense.get('min', {})
    defense_max = defense.get('max', {})
    recipe.update({
        'location': kwargs.get('location'),
        'defense': {
            'min': {
                'center': defense_min.get('center', None),
                'radius': defense_min.get('radius', None)
            },
            'max': {
                'center': defense_max.get('center', None),
                'radius': defense_max.get('radius', None)
            }
        }
    })
    return recipe


def create(**kwargs):
    '''Create an armor.'''
    return equipment.create(**kwargs)


def save_recipe(recipe):
    '''Create/update an armor recipe.

    Raises a ValidationError if the recipe is invalid.
    '''
    recipe = recipe.copy()
    if recipe.get('id') is None:
        recipe['id'] = str(uuid4())
    validate_recipe(recipe)
    REPO_RECIPES['by_id'][recipe['id']] = recipe
    return recipe


def save(armor):
    '''Create/update an armor.

    Raises a ValidationError if the armor is invalid.
    '''
    armor = armor.copy()
    if armor.get('id') is None:
        armor['id'] = str(uuid4())
    validate(armor)
    REPO['by_id'][armor['id']] = armor
    return armor


def validate_recipe(recipe):
    '''Validate an armor recipe.

    Raises a ValidationError if the provided recipe is invalid.
    '''
    errors = []
    try:
        equipment.validate_recipe(recipe)
    except ValidationError as error:
        errors += error.errors
    location = recipe.get('location')
    if location is None:
        errors.append('Missing required field: location')
    elif location not in ARMOR_LOCATIONS:
        errors.append('Invalid armor location')
    try:
        equipment.validate_recipe_min_max_field(recipe, 'defense')
    except ValidationError as error:
        errors += error.errors
    if errors:
        raise ValidationError(errors=errors)


def validate(armor):
    '''Validate an armor.

    Raises a ValidationError if the provided armor is invalid.
    '''
    errors = []
    try:
        equipment.validate(armor)
    except ValidationError as error:
        errors += error.errors
    recipe = armor.get('recipe')
    if recipe is None:
        errors.append('Missing required field: recipe')
    else:
        try:
            find_recipe_by_id(recipe)
        except NotFoundError as error:
            errors.append(str(error))
    if errors:
        raise ValidationError(errors=errors)


# pylint: disable=duplicate-code
def find_recipe_by_id(recipe_id):
    '''Find an armor recipe with the provided id.

    Raises a NotFoundError if the recipe could not be found.
    '''
    recipe = REPO_RECIPES['by_id'].get(recipe_id)
    if recipe is None:
        raise NotFoundError('Armor recipe not found')
    return recipe


def find_by_id(armor_id):
    '''Find an armor with the provided id.

    Raises a NotFoundError if the armor could not be found.
    '''
    armor = REPO['by_id'].get(armor_id)
    if armor is None:
        raise NotFoundError('Armor not found')
    return armor


def transform(armor):
    '''Transform an armor's fields.

    The following transformations will be performed:
      - name and description: defaulted to recipe values if None
      - weight: derived from recipe and grade, rounded to 2 decimal places
      - grade: replaced with +0 to +9 form
      - location: set to recipe value
      - defense.min: derived from recipe and grade, rounded to 2 decimal places
      - defense.max: derived from recipe and grade, rounded to 2 decimal places
    '''
    recipe = find_recipe_by_id(armor.get('recipe'))
    grade = armor.get('grade')
    armor = equipment.transform(armor, recipe)
    defense = recipe.get('defense')
    defense_min = util.interval_grade_value(defense.get('min'), grade)
    defense_max = util.interval_grade_value(defense.get('max'), grade)
    armor.update({
        'location': recipe.get('location'),
        'defense': {
            'min': round(defense_min, 2),
            'max': round(defense_max, 2)
        }
    })
    return armor
