'''
wtf.api.weapons

Weapons have the following properties:
  * recipe: the recipe used to generate this weapon
  * name: (customizable) weapon name
  * description: (customizable) weapon description
  * grade: a value from 0.0 to 1.0 that measures the quality of the weapon
    > The higher this value, the "better" the weapon
'''

def create(**kwargs):
    '''Create a weapon'''
    return {
        'recipe': kwargs.get('recipe'),
        'type': kwargs.get('type'),
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'grade': kwargs.get('grade', 0.0)
    }
