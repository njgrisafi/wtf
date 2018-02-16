'''
wtf.api.weaponrecipes

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
'''
from uuid import uuid4
from flask import Blueprint, jsonify, request
from wtf.api import util
from wtf.api.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('weapon-recipes', __name__)
REPO = {'by_id': {}}
WEAPON_TYPES = ['sword', 'axe', 'mace', 'dagger', 'bow']


@BLUEPRINT.route('', methods=['POST'])
def handle_post_request():
    '''Handle weapon recipe POST requests.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/weapon-recipes \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "type": "...",
            "name": "...",
            "description": "...",
            "handedness": ...,
            "weight": {
                "center": ...,
                "radius": ...
            },
            "damage": {
                "min": {
                    "center": ...,
                    "radius": ...
                },
                "max": {
                    "center": ...,
                    "radius": ...
                }
            }
        }'
    '''
    util.validate_request(content_type='application/json')
    body = request.get_json(silent=True) or {}
    weight = body.get('weight', {})
    damage = body.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    recipe = save(create(
        type=body.get('type'),
        name=body.get('name'),
        description=body.get('description'),
        handedness=body.get('handedness'),
        weight=dict(center=weight.get('center'), radius=weight.get('radius')),
        damage=dict(
            min=dict(
                center=damage_min.get('center'),
                radius=damage_min.get('radius')
            ),
            max=dict(
                center=damage_max.get('center'),
                radius=damage_max.get('radius')
            )
        )
    ))
    return jsonify(recipe), 201


@BLUEPRINT.route('/<recipe_id>', methods=['GET'])
def handle_get_by_id_request(recipe_id):
    '''Handle weapon recipe GET by id requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/weapon-recipes/<id> \
        --write-out "\n"
    '''
    recipe = find_by_id(recipe_id)
    return jsonify({'recipe': recipe}), 200


def save(recipe):
    '''Persist a weapon recipe.

    If the recipe already exists, it will be updated; otherwise, it will be
        created.

    Raises a ValidationError if the recipe is invalid.
    '''
    recipe = recipe.copy()
    validate(recipe)
    if recipe.get('id') is None:
        recipe['id'] = uuid4()
    REPO.get('by_id')[recipe.get('id')] = recipe
    return recipe


def validate(recipe):
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
        validate_weight(recipe)
    except ValidationError as error:
        errors += error.errors
    try:
        validate_damage(recipe)
    except ValidationError as error:
        errors += error.errors
    if errors:
        raise ValidationError(errors=errors)


def validate_weight(recipe):
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


def validate_damage(recipe):
    '''Validate a weapon recipe's damage fields.

    Raises a ValidationError if the recipe's damage fields are invalid.
    '''
    errors = []
    damage = recipe.get('damage', {})
    damage_min = damage.get('min', {})
    damage_min_center = damage_min.get('center')
    damage_min_radius = damage_min.get('radius')
    damage_max = damage.get('max', {})
    damage_max_center = damage_max.get('center')
    damage_max_radius = damage_max.get('radius')
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


def find_by_id(recipe_id):
    '''Find a weapon recipe with the provided id.

    Raises a NotFoundError if the recipe could not be found.
    '''
    recipe = REPO.get('by_id').get(recipe_id)
    if recipe is None:
        raise NotFoundError('Weapon recipe not found')
    return recipe


def create(**kwargs):
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
