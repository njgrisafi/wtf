'''
wtf.api.weaponrecipes

Routes and functions for manipulating weapon recipes.
'''


def create(**kwargs):
    '''Create a weapon recipe.

    Weapon recipes have the following properties:
        name: the name of the weapon
        description: a description of the weapon
        weight: how much the weapon weighs
            center: the center of the weapon's weight interval
            radius: the radius of the weapon's weight interval
        damage: how much damage the weapon can inflict
            min: the minimum amount of damage the weapon can inflict
                center: the center of the weapon's minimum damage interval
                radius: the radius of the weapon's minimum damage interval
            max: the maximum amount of damage the weapon can inflict
                center: the center of the weapon's maximum damage interval
                radius: the radius of the weapon's maximum damage interval
    '''
    name = kwargs.get('name')
    description = kwargs.get('description')
    weight = kwargs.get('weight', {})
    damage = kwargs.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    return {
        'name': name,
        'description': description,
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
