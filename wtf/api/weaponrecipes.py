'''
wtf.api.weaponrecipes

Routes and functions for manipulating weapon recipes.
'''
from wtf.api import itemrecipes


def create(**kwargs):
    '''Create a weapon recipe.

    Weapon recipes extend item recipes.

    Weapon recipes have the following extended properties:
        damage: how much damage the weapon can inflict
            min: the minimum amount of damage the weapon can inflict
                center: the center of the weapon's minimum damage interval
                radius: the radius of the weapon's minimum damage interval
            max: the maximum amount of damage the weapon can inflict
                center: the center of the weapon's maximum damage interval
                radius: the radius of the weapon's maximum damage interval
    '''
    recipe = itemrecipes.create(**kwargs)
    damage = kwargs.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    recipe['damage'] = {
        'min': {
            'center': damage_min.get('center', 0),
            'radius': damage_min.get('radius', 0)
        },
        'max': {
            'center': damage_max.get('center', 0),
            'radius': damage_max.get('radius', 0)
        }
    }
    return recipe
