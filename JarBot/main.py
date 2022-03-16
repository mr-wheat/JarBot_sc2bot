"""JarBot """

# Standard Lib Imports
import os
import random

# Third Party Imports
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game

# Sc2 IDs
from sc2.ids.unit_typeid import UnitTypeId
unit_type = {
    "scv": UnitTypeId.SCV,
    "cc": UnitTypeId.COMMANDCENTER,
    "supply": UnitTypeId.SUPPLYDEPOT
}

class JarBot(BotAI):
    """
    Governs the Bot's behavior through the python_sc2 API.
    """
    async def on_step(self, iteration: int):
        print(f"The iteration is {iteration}")

        if self.townhalls:
            # thus we have command center
            command_center = self.townhalls.random

            # Train workers logic
            if command_center.is_idle and self.can_afford(UnitTypeId.SCV):
                command_center.train(unit_type["scv"])

            # Build Logic: First Supply Depot. One Supply Depot is required to unlock next set of buildings
            elif not self.structures(unit_type["supply"]) and self.already_pending(unit_type["supply"]) == 0:
                if self.can_afford(unit_type["supply"]):
                    await self.build(unit_type["supply"], near = command_center)

            # Build Logic: 1st Barrack

            
            # Build Logic: Supply Handling Past 1st Supply Depot
            elif self.structures(unit_type["supply"]).amount < 5:
                if self.can_afford(unit_type["supply"]):
                    target_supply = self.structures(unit_type["supply"]).closest_to(self.enemy_start_locations[0])
                    supply_position = target_supply.position.towards(self.enemy_start_locations[0], random.randrange(8, 15))
                    await self.build(unit_type["supply"], near = supply_position)
        else:
            # We currently do not have any bases
            if self.can_afford(unit_type["cc"]):
                await self.expand_now()

# Tuple Containing Info to launch an SCII Instance with the Bot
run_game(
    maps.get("OxideLE"),
    [Bot(Race.Terran, JarBot()),
    Computer(Race.Zerg, Difficulty.Easy)],
    realtime = False
)