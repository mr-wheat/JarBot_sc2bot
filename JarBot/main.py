"""JarBot"""

# Standard Lib Imports
import os
import random
import configparser
from matplotlib.pyplot import close 

# Third Party Imports
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.bot_ai import BotAI
from sc2.data import Alert, Difficulty, Race
from sc2.main import run_game
from sc2.position import Point2, Point3
from sc2.constants import *

# Sc2 IDs
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId

# Config Based Info (will move at later date)
unit_type = {
    "scv": UnitTypeId.SCV,
    "cc": UnitTypeId.COMMANDCENTER,
    "supply": UnitTypeId.SUPPLYDEPOT,
    "marine": UnitTypeId.MARINE,
    "rax": UnitTypeId.BARRACKS
}


class JarBot(BotAI):
    """
    Governs the Bot's behavior through the python_sc2 API. Currently Bot Employs a "swarm" tactic.
    """
    def __init__(self):
        self.attack_groups = set()


    async def on_step(self, iteration: int):
        desired_rax_count = round(1 + ((iteration * iteration) / (1100 + 100 * iteration)))
        print(f"The iteration is {iteration}, desired rax count: {desired_rax_count}")
        await self.distribute_workers() 
        supply_remaining = self.supply_cap - self.supply_used
        

        if self.townhalls:
            # thus we have command center
            command_center = self.townhalls.random
            rax_placement_posistion = None

            for rax in self.structures(unit_type["rax"]).ready.idle:
                if self.supply_cap != 200: # max supply
                    if not self.can_afford(unit_type["marine"]):
                        break
                    rax.train(unit_type["marine"])

            # Train workers logic
            if command_center.is_idle and self.can_afford(UnitTypeId.SCV) and self.units(unit_type["scv"]).amount <= 16 * self.townhalls.amount:
                command_center.train(unit_type["scv"])
                

            # Build Logic: First Supply Depot. One Supply Depot is required to unlock next set of buildings
            elif self.structures(unit_type["supply"]).amount == 0 and self.already_pending(unit_type["supply"]) == 0:
                if self.can_afford(unit_type["supply"]):
                    await self.build(unit_type["supply"], near = command_center)


            # Build Logic: Supply Handling Past 1st Supply Depot
            elif (self.structures(unit_type["supply"]).amount >= 1 and supply_remaining <= 4) and not self.already_pending(unit_type["supply"]):
                if self.can_afford(unit_type["supply"]):
                    target_supply = self.structures(unit_type["supply"]).closest_to(self.start_location)
                    supply_position = target_supply.position.towards(self.start_location, random.randrange(8, 15))
                    await self.build(unit_type["supply"], near = supply_position)


            if self.structures(unit_type["supply"]).ready.exists and self.can_afford(unit_type["rax"]) and not self.already_pending(unit_type['rax']):
                if self.structures(unit_type["rax"]).amount + self.already_pending(unit_type["rax"]) > desired_rax_count:
                    return
                worker = self.worker_en_route_to_build
                if rax_placement_posistion == None:
                    rax_placement_posistion = self.main_base_ramp.barracks_correct_placement
                else:
                    target_rax = self.structures(unit_type["rax"]).closest_to(self.start_location)
                    rax_placement_posistion = target_rax.position.towards(self.start_location, random.randrange(8, 15))
                if worker and rax_placement_posistion: #Worker and Placement of Barrack was Found
                    await self.build(unit_type['rax'], near = rax_placement_posistion)





        else:
            # We currently do not have any bases
            if self.can_afford(unit_type["cc"]):
                await self.expand_now()
        
        #for scv in self.workers.idle:
            #closest_min_patch = self.mineral_field.closest_to(scv)
            #scv.gather(closest_min_patch.position)
            #await self.distribute_workers()
            # closestCC = self.townhalls.ready.closest_to(scv.position)
            # await self.do(scv.gather(self.state.mineral_field.closest_to(closestCC))) 
        
        if self.alert(Alert.MineralsExhausted): # When minerals begin to run out, expand
            if self.can_afford(unit_type["cc"]):
                await self.expand_now()


        # attacking logic
        if self.units(unit_type["marine"]).amount >= 30:
            if self.enemy_units:
                for marine in self.units(unit_type["marine"]).idle:
                    marine.attack(random.choice(self.enemy_units))
        
            elif self.enemy_structures:
                for marine in self.units(unit_type["marine"]).idle:
                    marine.attack(random.choice(self.enemy_structures))

            # otherwise attack enemy starting position
            else:
                for marine in self.units(unit_type["marine"]).idle:
                    marine.attack(self.enemy_start_locations[0])

        
       
def main():
# Command containing Info to launch an SCII Instance with the Bot
    run_game(
        maps.get("OxideLE"),
        [Bot(Race.Terran, JarBot()),
        Computer(Race.Zerg, Difficulty.Easy)],
        realtime = False
    )   

if __name__ == "__main__":
    main();