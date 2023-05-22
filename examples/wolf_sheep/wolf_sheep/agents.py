import mesa
import random 
from wolf_sheep.random_walk import RandomWalker


class Sheep(RandomWalker):
    """
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy

    def step(self):
        """
        A model step. Move, then eat grass and reproduce.
        """
        self.random_move()
        living = True

        if self.model.grass or self.model.tree:
            # Reduce energy
            self.energy -= 1

        if self.model.grass:
            # If there is grass available, eat it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            
            grass_patch_list = [obj for obj in this_cell if isinstance(obj, GrassPatch)]
            if len(grass_patch_list) > 0:
                grass_patch = grass_patch_list[0]
                if grass_patch.fully_grown:
                    self.energy += self.model.sheep_gain_from_grass
                    grass_patch.fully_grown = False

        if self.model.tree:
            # If there is tree available, eat it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            tree_list = [obj for obj in this_cell if isinstance(obj, Tree)]
            if len(tree_list) > 0:
                tree = tree_list[0]
                if tree.fully_grown:
                    self.energy += self.model.sheep_gain_from_tree
                    tree.fully_grown = False

        if (self.model.grass or self.model.tree) and self.energy < 0:
            # Death
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            living = False

        if living and self.random.random() < self.model.sheep_reproduce:
            # Create a new sheep:
            if self.model.grass or self.model.tree:
                self.energy /= 2
            lamb = Sheep(
                self.model.next_id(), self.pos, self.model, self.moore, self.energy
            )
            self.model.grid.place_agent(lamb, self.pos)
            self.model.schedule.add(lamb)


class Wolf(RandomWalker):
    """
    A wolf that walks around, reproduces (asexually) and eats sheep.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, mad_wolf, mad_chance, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.mad_wolf = mad_wolf
        self.mad_chance = mad_chance
        self.energy = energy

    def step(self):
        self.random_move()
        self.energy -= 1

        # If there are sheep present, eat one
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.model.wolf_gain_from_food

            # Kill the sheep
            self.model.grid.remove_agent(sheep_to_eat)
            self.model.schedule.remove(sheep_to_eat)

        # Turn mad
        if self.mad_wolf and random.uniform(0, 1) < self.mad_chance:
            mad_w = MadWolf(self.model.next_id(), self.pos, self.model, self.moore, self.energy / 4)
            self.model.grid.place_agent(mad_w, mad_w.pos)
            self.model.schedule.add(mad_w)

            # Dies
            self.energy = 0

        # Death or reproduction
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        else:
            if self.random.random() < self.model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(
                    self.model.next_id(), self.pos, self.model, self.moore, self.mad_wolf, self.mad_chance, self.energy
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)
                

class MadWolf(RandomWalker):
    """
    A mad wolf that walks around, eats healthy wolves.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy

    def step(self):
        self.random_move()
        self.energy -= 1

        # If there are healthy wolves present, eat one
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        healthy_wolves = [obj for obj in this_cell if isinstance(obj, Wolf)]
        if len(healthy_wolves) > 0:
            wolf_to_eat = self.random.choice(healthy_wolves)

            # Kill the wolf
            self.model.grid.remove_agent(wolf_to_eat)
            self.model.schedule.remove(wolf_to_eat)

        # Death
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


class Bear(RandomWalker):
    """
    A bear that walks around, reproduces (asexually) and eats sheep and wolves.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy

    def step(self):
        self.random_move()
        self.energy -= 1

	    # CHANGE THIS TO BE ONE WOLF OR ONE SHEEP IN THE CASE THERE ARE TWO

        # If there are sheep or wolf present, eat one
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        wolf = [obj for obj in this_cell if isinstance(obj, Wolf)]
        mad_wolf = [obj for obj in this_cell if isinstance(obj, MadWolf)]
        
        if len(sheep) > 0:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.model.wolf_gain_from_food

            # Kill the sheep
            self.model.grid.remove_agent(sheep_to_eat)
            self.model.schedule.remove(sheep_to_eat)

	# If there are wolves present, eat one
        if len(wolf) > 0:
            wolf_to_eat = self.random.choice(wolf)
            self.energy += self.model.bear_gain_from_food

            # Kill the wolf
            self.model.grid.remove_agent(wolf_to_eat)
            self.model.schedule.remove(wolf_to_eat)

        if len(mad_wolf) > 0:
            mad_wolf_to_eat = self.random.choice(mad_wolf)

            # Kill the mad wolf
            self.model.grid.remove_agent(mad_wolf_to_eat)
            self.model.schedule.remove(mad_wolf_to_eat)

            # Dies by eating the mad wolf
            self.energy = -1

        # Death or reproduction
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        else:
            if self.random.random() < self.model.bear_reproduce:
                # Create a new bear cub
                self.energy /= 2
                cub = Bear(
                    self.model.next_id(), self.pos, self.model, self.moore, self.energy
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)


class GrassPatch(mesa.Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1


class Tree(mesa.Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.tree_regrowth_time
            else:
                self.countdown -= 1
