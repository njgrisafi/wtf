'''
wtf.api.itemrecipes

Routes and functions for manipulating item recipes.
'''


def create(**kwargs):
    '''Create a item recipe.

    Item recipes have the following properties:
        name: the name of the item
        description: a description of the item
        weight: how much the item weighs
            center: the center of the item's weight interval
            radius: the radius of the item's weight interval
    '''
    weight = kwargs.get('weight', {})
    return {
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'weight': {
            'center': weight.get('center', 0),
            'radius': weight.get('radius', 0)
        }
    }
