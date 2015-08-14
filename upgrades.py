"""
A file for storing all of the Hero's upgrades.
"""

upgrades = {}


def upgrade(func):
    """
    Wrap a function with the general upgrade code.

    * fully heal the hero
    * reset the hero's motion
    * add the upgrade to hero.upgrades

    also, add the upgrade to the upgrades dict so that
    it can be called in the Upgrade screen
    """

    func_name = func.__name__.replace('_', ' ')

    def new_func(hero):
        hero.full_heal()
        hero.reset_motion()
        hero.upgrades.append(func_name)
        func(hero)

    upgrades[func_name] = new_func

    return new_func

@upgrade
def double_jump(hero):
    hero.can_doublejump = True

@upgrade
def melee_increase(hero):
    hero.melee_damage_multiplier = 2

@upgrade
def bomb_increase(hero):
    hero.max_bombs = 5
    hero.bomb_refill_requirement = 1

@upgrade
def speed_bonus(hero):
    hero.base_speed += 4
    hero.actual_speed = hero.base_speed

@upgrade
def long_arms(hero):
    hero.melee_range_multiplier = 1.5
    hero.weapon_pickup_range *= 2

@upgrade
def speed_boost_on_kill(hero):
    hero.speed_boost_on_kill = True

@upgrade
def no_fall_damage(hero):
    hero.take_falldamage = False
