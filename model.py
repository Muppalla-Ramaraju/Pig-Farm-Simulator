from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import PigAgent  # Assuming PigAgent is defined in agent.py
import random
import math


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
        self.update_time()  # Call update_time to update the days
        # Rest of your step logic...
        # Update the time
        self.num_days += 1

        # Count the number of pigs in each category
        num_gilts = len([agent for agent in self.schedule.agents if agent.pig_type == "gilt"])
        num_barrows = len([agent for agent in self.schedule.agents if agent.pig_type == "barrow"])
        num_males = len([agent for agent in self.schedule.agents if agent.pig_type == "male"])
        self.num_pigs = num_gilts + num_barrows + num_males

        # Move and feed pigs based on their type
        for agent in self.schedule.agents:
            if agent.pig_type == "gilt":
                agent.move()
                agent.feed_g()
            elif agent.pig_type == "barrow":
                agent.move()
                agent.feed_b()
            elif agent.pig_type == "male":
                agent.move()
                agent.feed_m()

        # Calculate total feed intake
        #total_feed = self.sum_feed_intake(self.schedule.agents)

        self.total_feed_intake = sum(agent.feed_intake for agent in self.schedule.agents)
        print(f"The total feed intake + wastage on day {self.num_days} for {self.num_pigs} pigs is {round(self.total_feed_intake, 4)} kg")

        # Update labels if necessary (you can customize this part)
        for agent in self.schedule.agents:
            agent.label = agent.unique_id
            agent.label_color = "yellow"

        # Stop the simulation at 140 days
        if self.num_days >= 140:
            self.running = False

        # Step the schedule and collect data
        self.schedule.step()
        self.datacollector.collect(self)

    def update_time(self):
        """Update the number of days in the simulation."""
        self.num_days = self.schedule.time  # Use the scheduler's time to set the number of days

    def update_feed_intake(self):
        """Update feed intake for all pigs."""
        for agent in self.schedule.agents:
            if agent.pig_type == "gilt":
                agent.feed_intake_es = 1.053 * agent.ME_intake / agent.ME_content
                agent.feed_intake = 2.755 * (1 - (math.exp(-math.exp(-4.755) * (agent.weight ** 1.214))))
            elif agent.pig_type == "barrow":
                agent.feed_intake_es = 1.053 * agent.ME_intake / agent.ME_content
                agent.feed_intake = 2.88 * (1 - (math.exp(-math.exp(-5.921) * (agent.weight ** 1.512))))
            elif agent.pig_type == "male":
                agent.feed_intake = 1.053 * agent.ME_intake / agent.ME_content

    def sum_feed_intake(self, agents_list):
        """Calculate the total feed intake for a given list of agents."""
        total_feed_intake = 0  # Initialize the result variable
        for agent in agents_list:  # Loop through each pig in the list
            total_feed_intake += agent.feed_intake  # Add the feed intake of the agent
        return total_feed_intake  # Return the result
    
    '''def random_triangular(a, b, c):
        """Return a random value from a triangular distribution."""
        U = random.uniform(0, 1)  # Equivalent to random-float in NetLogo
        if U < (c - a) / (b - a):
            return a + math.sqrt(U * (b - a) * (c - a))
        else:
            return b - math.sqrt((1 - U) * (b - a) * (b - c))'''
    
    def setup_regions(self, num_regions):
        """Set up regions by dividing the grid into the specified number of regions."""
        self.region_boundaries = self.calculate_region_boundaries(num_regions)
        # Example adjustment in the setup_regions method
    
        # Do something with agent, x, and y
        region_numbers = range(1, num_regions + 1)
        
        for boundaries, region_number in zip(self.region_boundaries, region_numbers):
            for cell in self.grid.coord_iter():
                if len(cell) == 2:
                    x, y = cell
                # Do something with x and y
                elif len(cell) == 3:
                    agent, x, y = cell
                if boundaries[0] <= x <= boundaries[1]:
                    # Assuming you have a way to tag a cell with a region number
                    self.grid.place_agent(RegionMarker(region_number), (x, y))  # RegionMarker is a placeholder

    def sell_pig(self):
        """Sell a pig if its weight is above the sell weight."""
        pigs_to_sell = [agent for agent in self.schedule.agents if agent.weight > self.sell_weight]
        if pigs_to_sell:
            pig_to_sell = random.choice(pigs_to_sell)
            if random.uniform(0, 100) < self.selling_rate:
                self.num_sold += 1
                self.schedule.remove(pig_to_sell)
    
    def calculate_region_boundaries(self, num_regions):
        """Calculate boundaries for each region."""
        divisions = self.region_divisions(num_regions)
        return [(divisions[i] + 1, divisions[i + 1] - 1) for i in range(len(divisions) - 1)]
    
    def region_divisions(self, num_regions):
        """Calculate division points for regions."""
        return [int(self.grid.width * n / num_regions) for n in range(num_regions + 1)]
    
    def draw_region_division(self, x):
        """Draw a division line at the given x-coordinate."""
        for y in range(self.grid.height):
            self.grid.place_agent(RegionMarker(self.next_id(), self, None), (x, y))

    def keep_in_region(self, which_region):
        """Keep the agent within the specified region."""
        region_min_x, region_max_x = self.model.region_boundaries[which_region - 1]
        x, y = self.pos

        if x < region_min_x:
            x = region_min_x
        elif x > region_max_x:
            x = region_max_x

        self.model.grid.move_agent(self, (x, y))
    



