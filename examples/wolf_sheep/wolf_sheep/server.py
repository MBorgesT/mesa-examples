import mesa

from wolf_sheep.agents import Wolf, MadWolf, Sheep, GrassPatch, Tree, Bear
from wolf_sheep.model import WolfSheep


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Sheep:
        portrayal["Shape"] = "wolf_sheep/resources/sheep.png"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    elif type(agent) is Wolf:
        portrayal["Shape"] = "wolf_sheep/resources/wolf.png"
        # https://icons8.com/web-app/36821/German-Shepherd
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"
        
    elif type(agent) is Bear:
        portrayal["Shape"] = "wolf_sheep/resources/bear.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 3
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is MadWolf:
        portrayal["Shape"] = "wolf_sheep/resources/mad_wolf.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 3
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is GrassPatch:
        if agent.fully_grown:
            portrayal["Color"] = ["#00CC00", "#00CC00", "#00CC00"]
        else:
            portrayal["Color"] = ["#adebad", "#adebad", "#adebad"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif type(agent) is Tree:
        if agent.fully_grown:
            portrayal["Color"] = ["#015401", "#015401", "#015401"]
        else:
            portrayal["Color"] = ["#adebad", "#adebad", "#adebad"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(wolf_sheep_portrayal, 20, 20, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Wolves", "Color": "#AA0000"},
        {"Label": "Bears", "Color": "#8c5600"},
        {"Label": "MadWolves", "Color": "#440000"},
        {"Label": "Sheep", "Color": "#666666"},
        {"Label": "Grass", "Color": "#00CC00"},
        {"Label": "Tree", "Color": "#015401"},
    ]
)

model_params = {
    # The following line is an example to showcase StaticText.
    "title": mesa.visualization.StaticText("Parameters:"),
    "grass": mesa.visualization.Checkbox("Grass Enabled", True),
    "tree": mesa.visualization.Checkbox("Tree Enabled", True),
    "sheep": mesa.visualization.Checkbox("Sheep Enabled", True),
    "wolf": mesa.visualization.Checkbox("Wolf Enabled", True),
    "mad_wolf": mesa.visualization.Checkbox("Mad Wolf Enabled", True),
    "bear": mesa.visualization.Checkbox("Bear Enabled", True),
    "grass_regrowth_time": mesa.visualization.Slider("Grass Regrowth Time", 20, 1, 50),
    "tree_regrowth_time": mesa.visualization.Slider("Tree Regrowth Time", 40, 1, 100),
    "initial_sheep": mesa.visualization.Slider(
        "Initial Sheep Population", 100, 10, 300
    ),
    "sheep_reproduce": mesa.visualization.Slider(
        "Sheep Reproduction Rate", 0.04, 0.01, 1.0, 0.01
    ),
    "initial_wolves": mesa.visualization.Slider("Initial Wolf Population", 50, 10, 300),
    "wolf_reproduce": mesa.visualization.Slider(
        "Wolf Reproduction Rate",
        0.05,
        0.01,
        1.0,
        0.01,
        description="The rate at which wolf agents reproduce.",
    ),
    "wolf_gain_from_food": mesa.visualization.Slider(
        "Wolf Gain From Food Rate", 20, 1, 50
    ),
    "initial_bears": mesa.visualization.Slider("Initial Bear Population", 15, 5, 150),
    "bear_reproduce": mesa.visualization.Slider(
        "Bear Reproduction Rate",
        0.03,
        0.01,
        1.0,
        0.01,
        description="The rate at which bear agents reproduce.",
    ),
    "bear_gain_from_food": mesa.visualization.Slider(
        "Bear Gain From Food Rate", 10, 1, 25
    ),
    "sheep_gain_from_grass": mesa.visualization.Slider("Sheep Gain From Grass", 4, 1, 10),
    "sheep_gain_from_tree": mesa.visualization.Slider("Sheep Gain From Tree", 8, 1, 20),
    "mad_wolf_chance": mesa.visualization.Slider("Chance For Wolf To Turn Mad", 0.05, 0, 0.2, 0.01),
}

server = mesa.visualization.ModularServer(
    WolfSheep, [canvas_element, chart_element], "Wolf Sheep Predation", model_params
)
server.port = 8521
