"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""
import numpy as np

import mesa

from wolf_sheep.scheduler import RandomActivationByTypeFiltered
from wolf_sheep.agents import Sheep, Wolf, MadWolf, GrassPatch, Tree, Bear


class WolfSheep(mesa.Model):
    """
    Wolf-Sheep Predation Model
    """

    height = 20
    width = 20

    initial_sheep = 100
    initial_wolves = 50

    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    wolf_gain_from_food = 20

    grass = False
    tree = False
    sheep = False
    wolf = False
    mad_wolf = False
    bear = False

    grass_regrowth_time = 30
    tree_regrowth_time = 60
    sheep_gain_from_grass = 4
    sheep_gain_from_tree = 8
    
    initial_bears = 30
    bear_gain_from_food = 20
    bear_reproduce = 0.03

    mad_wolf_chance = 0.05

    verbose = False  # Print-monitoring

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        width=20,
        height=20,
        initial_sheep=100,
        initial_wolves=50,
        sheep_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass=False,
        tree=False,
        sheep=False,
        wolf=False,
        mad_wolf=False,
        bear=False,
        grass_regrowth_time=30,
        tree_regrowth_time=60,
        sheep_gain_from_grass=4,
        sheep_gain_from_tree=8,
        bear_gain_from_food = 20,
        bear_reproduce = 0.03,
        initial_bears = 30,
        mad_wolf_chance=0.05
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_grass: Energy sheep gain from grass, if enabled.
        """
        super().__init__()
        # Set parameters
        self.width = width
        self.height = height
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.tree = tree
        self.sheep = sheep
        self.wolf = wolf
        self.mad_wolf = mad_wolf
        self.bear = bear
        self.grass_regrowth_time = grass_regrowth_time
        self.tree_regrowth_time = tree_regrowth_time
        self.sheep_gain_from_grass = sheep_gain_from_grass
        self.sheep_gain_from_tree = sheep_gain_from_tree
        
        self.initial_bears = initial_bears
        self.bear_gain_from_food = bear_gain_from_food
        self.bear_reproduce = bear_reproduce
        
        self.mad_wolf_chance = mad_wolf_chance

        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.datacollector = mesa.DataCollector(
            {
                "Wolves": lambda m: m.schedule.get_type_count(Wolf),
                "Bears": lambda m: m.schedule.get_type_count(Bear),
                "ZombieWolves": lambda m: m.schedule.get_type_count(MadWolf),
                "Sheep": lambda m: m.schedule.get_type_count(Sheep),
                "Grass": lambda m: m.schedule.get_type_count(
                    GrassPatch, lambda x: x.fully_grown
                ),
                "Tree": lambda m: m.schedule.get_type_count(
                    Tree, lambda x: x.fully_grown
                ),
            }
        )

        # Create sheep:
        if self.sheep:
            for i in range(self.initial_sheep):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                energy = self.random.randrange(2 * self.sheep_gain_from_grass)
                sheep = Sheep(self.next_id(), (x, y), self, True, energy)
                self.grid.place_agent(sheep, (x, y))
                self.schedule.add(sheep)

        # Create wolves
        if self.wolf:
            for i in range(self.initial_wolves):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                energy = self.random.randrange(2 * self.wolf_gain_from_food)
                wolf = Wolf(self.next_id(), (x, y), self, True, mad_wolf, mad_wolf_chance, energy)
                self.grid.place_agent(wolf, (x, y))
                self.schedule.add(wolf)
            
        # Create bears
        if self.bear:
            for i in range(self.initial_bears):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                energy = self.random.randrange(2 * self.bear_gain_from_food)
                bear = Bear(self.next_id(), (x, y), self, True, energy)
                self.grid.place_agent(bear, (x, y))
                self.schedule.add(bear)

        if self.grass and self.tree:
            # Alternates between tree and grass on generation
            for agent, x, y in self.grid.coord_iter():
                
                result = np.random.choice(['grass', 'tree'])
                fully_grown = self.random.choice([True, False])
                if result == 'grass':
                    if fully_grown:
                        countdown = self.grass_regrowth_time
                    else:
                        countdown = self.random.randrange(self.grass_regrowth_time)

                    patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                    self.grid.place_agent(patch, (x, y))
                    self.schedule.add(patch)
                elif result == 'tree':
                    if fully_grown:
                        countdown = self.tree_regrowth_time
                    else:
                        countdown = self.random.randrange(self.tree_regrowth_time)

                    patch = Tree(self.next_id(), (x, y), self, fully_grown, countdown)
                    self.grid.place_agent(patch, (x, y))
                    self.schedule.add(patch)
                else:
                    raise Exception("This shouldn't happen :|")

        else:
            # Create grass patches
            if self.grass:
                for agent, x, y in self.grid.coord_iter():
                    fully_grown = self.random.choice([True, False])

                    if fully_grown:
                        countdown = self.grass_regrowth_time
                    else:
                        countdown = self.random.randrange(self.grass_regrowth_time)

                    patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                    self.grid.place_agent(patch, (x, y))
                    self.schedule.add(patch)

            # Create trees
            elif self.tree:
                for agent, x, y in self.grid.coord_iter():
                    fully_grown = self.random.choice([True, False])

                    if fully_grown:
                        countdown = self.tree_regrowth_time
                    else:
                        countdown = self.random.randrange(self.tree_regrowth_time)

                    patch = Tree(self.next_id(), (x, y), self, fully_grown, countdown)
                    self.grid.place_agent(patch, (x, y))
                    self.schedule.add(patch)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_type_count(Wolf),
                    self.schedule.get_type_count(MadWolf),
                    self.schedule.get_type_count(Sheep),
                    self.schedule.get_type_count(Bear),
                    self.schedule.get_type_count(GrassPatch, lambda x: x.fully_grown),
                    self.schedule.get_type_count(Tree, lambda x: x.fully_grown),
                ]
            )

    def run_model(self, step_count=200):
        if self.verbose:
            print("Initial number wolves: ", self.schedule.get_type_count(Wolf))
            print("Initial number mad wolves: ", self.schedule.get_type_count(MadWolf))
            print("Initial number sheep: ", self.schedule.get_type_count(Sheep))
            print("Initial number bears: ", self.schedule.get_type_count(Bear))
            print(
                "Initial number grass: ",
                self.schedule.get_type_count(GrassPatch, lambda x: x.fully_grown),
            )
            print(
                "Initial number tree: ",
                self.schedule.get_type_count(Tree, lambda x: x.fully_grown),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print("Final number wolves: ", self.schedule.get_type_count(Wolf))
            print("Final number mad wolves: ", self.schedule.get_type_count(MadWolf))
            print("Final number sheep: ", self.schedule.get_type_count(Sheep))
            print("Final number bears: ", self.schedule.get_type_count(Bear))
            print(
                "Final number grass: ",
                self.schedule.get_type_count(GrassPatch, lambda x: x.fully_grown),
            )
            print(
                "Final number tree: ",
                self.schedule.get_type_count(Tree, lambda x: x.fully_grown),
            )
