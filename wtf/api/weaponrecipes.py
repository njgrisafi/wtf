'''
wtf.api.weaponrecipes

Weapon recipes have the following properties:
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


WEAPON_TYPES = ['sword', 'axe', 'mace', 'dagger', 'bow']


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
