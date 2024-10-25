from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import PigAgent  # Assuming PigAgent is defined in agent.py
import random


class PigModel(Model):
    def __init__(self, num_gilts, num_barrows, num_males, init_weight=20, sell_weight=130, width=10, height=10):
        super().__init__()
        self.num_gilts = num_gilts
        self.num_barrows = num_barrows
        self.num_males = num_males
        self.num_pigs = num_gilts + num_barrows + num_males
        self.init_weight = init_weight
        self.sell_weight = sell_weight
        self.total_feed_intake = 0
        self.init_weight_rac = 78
        self.feed_dry_intake = 0
        self.region_boundaries = []  # Corresponds to region-boundaries
        self.daily_feeding = 0
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.num_days = 0
        self.num_sold = 0
       
        


        # Set up regions
        self.setup_regions(5)

        # Create pigs
        self.setup_initial_gilts()
        self.setup_initial_barrows()
        self.setup_initial_males()

        self.datacollector = DataCollector(
            agent_reporters={"Weight": "weight"}
        )

    def setup_regions(self, num_regions):
        """Simulate regions by dividing the grid."""
        region_width = self.grid.width // num_regions
        self.regions = []
        for i in range(num_regions):
            region_start = i * region_width
            region_end = (i + 1) * region_width
            self.regions.append((region_start, region_end))

    def setup_initial_gilts(self):
        """Create the gilts (female pigs) with random initial weights."""
        for i in range(self.num_gilts):
            initial_weight = self.init_weight - 1 + random.uniform(0, 2)
            pig = PigAgent(i, self, "gilt", initial_weight, self.regions[0])
            print(f"(gilt {i}): 'My init-weight is: {round(initial_weight, 4)} Kg'")
            self.grid.place_agent(pig, (self.random.randrange(10), self.random.randrange(10)))
            self.schedule.add(pig)

    def setup_initial_barrows(self):
        """Create the barrows (castrated males) with random initial weights."""
        for i in range(self.num_barrows):
            initial_weight = self.init_weight - 1 + random.uniform(0, 2)
            pig = PigAgent(i + self.num_gilts, self, "barrow", initial_weight, self.regions[1])
            print(f"(barrow {i + self.num_gilts}): 'My init-weight is: {round(initial_weight, 4)} Kg'")
            self.grid.place_agent(pig, (self.random.randrange(10), self.random.randrange(10)))
            self.schedule.add(pig)

    def setup_initial_males(self):
        """Create the males with random initial weights."""
        for i in range(self.num_males):
            initial_weight = self.init_weight - 1 + random.uniform(0, 2)
            pig = PigAgent(i + self.num_gilts + self.num_barrows, self, "male", initial_weight, self.regions[2])
            print(f"(male {i + self.num_gilts + self.num_barrows}): 'My init-weight is: {round(initial_weight, 4)} Kg'")
            self.grid.place_agent(pig, (self.random.randrange(10), self.random.randrange(10)))
            self.schedule.add(pig)

    def step(self):
        self.schedule.step()
        self.num_days += 1
        self.datacollector.collect(self)