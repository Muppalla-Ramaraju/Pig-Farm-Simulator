from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import PigAgent
import random
import math
import pandas as pd



class PigModel(Model):
    def __init__(self, num_gilts, num_barrows, num_males, init_weight=20, sell_weight=130, ME_content=3000, width=20, height=20, num_regions=5, RAC=True):
        super().__init__()
        self.ME_content = ME_content
        self.num_gilts = num_gilts
        self.num_barrows = num_barrows
        self.num_males = num_males
        self.num_pigs = num_gilts + num_barrows + num_males
        self.init_weight = init_weight
        self.sell_weight = sell_weight
        self.total_feed_intake = 0
        self.init_weight_rac = 78
        self.feed_dry_intake = 0
        self.daily_feeding = 0
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.num_days = 0
        self.num_sold = 0
        self.RAC = RAC


        # Tracked agents for plotting
        self.tracked_agents = {"gilt": None, "barrow": None, "male": None}
        self.tracked_data = {key: [] for key in self.tracked_agents}

        # Calculate region width based on the number of regions
        self.region_width = width // num_regions

        # Set up data collection
        # Set up data collection
        self.datacollector = DataCollector(
            agent_reporters={
                "Weight": "weight",
                "Weight Gain": "weight_gain",
                "Pd": "Prd",
                "Ld": "Lid",
                "ME Intake": "ME_intake",
                "Feed Intake": "feed_intake",
                "SID Lys": "SID_lys",
                "Maintenance ME": "Maintenance_ME_requirements",
                "PBT": "PBT"
            }
        )

        # Initialize pigs in regions and assign tracked agents
        self.setup_pigs_in_regions(num_regions)
        self.assign_tracked_agents()

    def assign_tracked_agents(self):
        """Randomly pick one gilt, one barrow, and one male for tracking."""
        gilts = [agent for agent in self.schedule.agents if agent.pig_type == "gilt"]
        barrows = [agent for agent in self.schedule.agents if agent.pig_type == "barrow"]
        males = [agent for agent in self.schedule.agents if agent.pig_type == "male"]

        self.tracked_agents["gilt"] = random.choice(gilts) if gilts else None
        self.tracked_agents["barrow"] = random.choice(barrows) if barrows else None
        self.tracked_agents["male"] = random.choice(males) if males else None

    def setup_pigs_in_regions(self, num_regions):
        """Create gilts, barrows, and males in each of the specified regions."""
        for region in range(num_regions):
            region_start = region * self.region_width
            region_end = region_start + self.region_width - 1

            # Distribute gilts, barrows, and males in the region
            self.add_pigs("gilt", self.num_gilts // num_regions, region_start, region_end)
            self.add_pigs("barrow", self.num_barrows // num_regions, region_start, region_end)
            self.add_pigs("male", self.num_males // num_regions, region_start, region_end)

    def add_pigs(self, pig_type, num_pigs, region_start, region_end):
        """Add pigs of a specific type to a designated region on the grid."""
        for _ in range(num_pigs):
            initial_weight = self.init_weight - 1 + random.uniform(0, 2)
            # Pass `region` as a tuple containing region boundaries (region_start, region_end)
            pig = PigAgent(self.schedule.get_agent_count(), self, pig_type, initial_weight, region=(region_start, region_end))
            x = random.randint(region_start, region_end)
            y = random.randint(0, self.grid.height - 1)
            self.grid.place_agent(pig, (x, y))
            self.schedule.add(pig)
            print(f"({pig_type}): 'My init-weight is: {round(initial_weight, 4)} Kg' in region ({region_start}, {region_end})")

    def step(self):
        """Advance the model by one step."""
        self.num_days += 1

        # Move and feed pigs
        for agent in self.schedule.agents:
            agent.move()
            if agent.pig_type == "gilt":
                agent.feed_g(stochastic_weight_gain=False)
            elif agent.pig_type == "barrow":
                agent.feed_b(stochastic_weight_gain=False)
            elif agent.pig_type == "male":
                agent.feed_m(stochastic_weight_gain=False)

        # Collect data for tracked agents
        for gender, agent in self.tracked_agents.items():
            if agent:
                self.tracked_data[gender].append({
                    "Day": self.num_days,
                    "Weight": agent.weight,
                    "Weight Gain": agent.weight_gain,
                    "Pd": agent.Prd,
                    "Ld": agent.Lid,
                    "ME Intake": agent.ME_intake,
                    "Feed Intake": agent.feed_intake,
                    "SID Lys": agent.SID_lys,
                    "Maintenance ME": agent.Maintenance_ME_requirements,
                    "PBT": agent.PBT
                })

        # Step schedule and collect data
        self.schedule.step()
        self.datacollector.collect(self)

        # Stop simulation after a set number of days
        if self.num_days >= 140:
            self.running = False

    '''def update_feed_intake(self):
        """Update feed intake for all pigs."""
        for agent in self.schedule.agents:
            if agent.pig_type == "gilt":
                agent.feed_intake_es = 1.053 * agent.ME_intake / agent.ME_content
                agent.feed_intake = 2.755 * (1 - (math.exp(-math.exp(-4.755) * (agent.weight ** 1.214))))
            elif agent.pig_type == "barrow":
                agent.feed_intake_es = 1.053 * agent.ME_intake / agent.ME_content
                agent.feed_intake = 2.88 * (1 - (math.exp(-math.exp(-5.921) * (agent.weight ** 1.512))))
            elif agent.pig_type == "male":
                agent.feed_intake = 1.053 * agent.ME_intake / agent.ME_content'''

    '''def update_feed_intake(self):
        """Update feed intake based on pig type and weight."""
        if self.pig_type == "gilt":
            self.feed_intake_es = 1.053 * self.ME_intake / self.model.ME_content  # Assuming `ME_content` is a model attribute
            self.feed_intake = 2.755 * (1 - (math.exp(-math.exp(-4.755) * (self.weight ** 1.214))))
        elif self.pig_type == "barrow":
            self.feed_intake_es = 1.053 * self.ME_intake / self.model.ME_content
            self.feed_intake = 2.88 * (1 - (math.exp(-math.exp(-5.921) * (self.weight ** 1.512))))
        elif self.pig_type == "male":
            self.feed_intake = 1.053 * self.ME_intake / self.model.ME_content'''

    def sum_feed_intake(self, agents_list):
        """Calculate the total feed intake for a given list of agents."""
        return sum(agent.feed_intake for agent in agents_list)
    
    def save_tracked_data(self, filename="tracked_agents_data.csv"):
        """Save tracked data to a CSV file."""
        all_data = []
        for gender, records in self.tracked_data.items():
            for record in records:
                record["Gender"] = gender
                all_data.append(record)

        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        print(f"Tracked data saved to {filename}")