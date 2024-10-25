# agent.py

from mesa import Agent

class PigAgent(Agent):
    def __init__(self, unique_id, model, pig_type, init_weight, region):
        super().__init__(unique_id, model)
        
        self.pig_type = pig_type  # 'gilt', 'barrow', or 'male'
        self.weight = init_weight
        self.region = region  # Corresponds to patches-own region
        self.feed_intake = 0
        self.energy_requirements = 0
        self.weight_gain = 0
        self.BPm = self.weight * 0.18  # Whole-body protein mass
        self.BLm = self.weight * 0.03  # Whole-body lipid mass
        self.Ash = 0
        self.Wat = 0
        self.ME_intake = 0
        self.ME_intake_rac = 0
        self.Prd = 0  # Pd
        self.Prd_1 = 0
        self.Pd_max = 0
        self.maximum_Pd = 0
        self.maximum_pd_after_pd_max_start_decline = 0
        self.BP_at_Pd_max = 0
        self.BP_at_maturity = 0
        self.Rate_constant = 0
        self.Lid = 0
        self.feed_intake_es = 0
        self.LCT = 0
        self.Minimum_space_for_maximum_ME_intake = 0
        self.Fraction_of_ME_intake = 0
        self.maximum_daily_feed_intake = 0
        self.standard_maintenance_ME_requirements = 0
        self.ME_requirements_for_thermogenesis = 0
        self.Maintenance_ME_requirements = 0
        self.Gut_fill = 0
        self.init_Gut_fill = 0
        self.EBW = 0
        self.init_BLm_BPm = 0
        self.PBT = 0
        self.fat_free_lean = 0
        self.final_weight = 0
        self.Pd_by_energy_int = 0

    def step(self):
        """Simulate one step in the agent's life (feeding, growing, etc.)."""
        self.feed()
        self.gain_weight()

    def feed(self):
        """Simulate the pig feeding."""
        if self.pig_type == "gilt":
            self.feed_intake = self.weight * 0.05  # Simplified feed intake logic
        elif self.pig_type == "barrow":
            self.feed_intake = self.weight * 0.06
        elif self.pig_type == "male":
            self.feed_intake = self.weight * 0.07

    def gain_weight(self):
        """Calculate weight gain based on feed intake and energy requirements."""
        # Simplified weight gain logic for now
        self.weight_gain = self.feed_intake * 0.1
        self.weight += self.weight_gain

        # Adjust body composition
        self.BPm += self.weight_gain * 0.18  # Protein mass adjustment
        self.BLm += self.weight_gain * 0.03  # Lipid mass adjustment

        # If the pig exceeds the sell weight, remove it from the simulation
        if self.weight >= self.model.sell_weight:
            self.model.schedule.remove(self)