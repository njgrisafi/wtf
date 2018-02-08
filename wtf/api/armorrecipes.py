'''
wtf.api.armorrecipes

Routes and functions for manipulating armor recipes.
'''
from wtf.api import itemrecipes


def create(**kwargs):
    '''Create a armor recipe.

    Armor recipes extend item recipes.

    Armor recipes have the following extended properties:
        defense: how much damage the armor can defend against
            min: the minimum amount of damage the armor can defend against
                center: the center of the armor's minimum defense interval
                radius: the radius of the armor's minimum defense interval
            max: the maximum amount of damage the armor can defend against
                center: the center of the armor's maximum defense interval
                radius: the radius of the armor's maximum defense interval
    '''
    recipe = itemrecipes.create(**kwargs)
    defense = kwargs.get('defense', {})
    defense_min = defense.get('min', {})
    defense_max = defense.get('max', {})
    recipe['defense'] = {
        'min': {
            'center': defense_min.get('center', 0),
            'radius': defense_min.get('radius', 0)
        },
        'max': {
            'center': defense_max.get('center', 0),
            'radius': defense_max.get('radius', 0)
        }
    }
    return recipe
