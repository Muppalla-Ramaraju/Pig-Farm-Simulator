# agent.py

from mesa import Agent
import random
import math

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
        # Call log_info() to print details for debugging or analysis
        #self.log_info()

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
    
    def move(self):
        """Simulate the movement of the pig agent, keeping it within its assigned region."""
        # Save the current region of the pig
        current_region = self.region

        # Random movement logic
        self.random.random_rotation(30)  # Turn randomly to the right
        self.random.random_rotation(-30)  # Turn randomly to the left
        self.advance(0.4)  # Move forward a small step

        # Ensure the pig stays within the bounds of its region
        self.keep_in_region(current_region)

        # Check for boundary conditions on the y-coordinate
        if self.pos[1] > self.model.grid.height - 1:
            self.model.grid.move_agent(self, (self.pos[0], self.model.grid.height - 1))
        elif self.pos[1] < 0:
            self.model.grid.move_agent(self, (self.pos[0], 0))

    def feed_g(self, stochastic_weight_gain):
        # Calculate base weight gain using the given formula
        base_weight_gain = -0.0477 * self.weight ** 2 + 8.8503 * self.weight + 485.17

        # Check for stochastic weight gain
        if stochastic_weight_gain:
            # Deviation from -20 to 20
            deviation = random.triangular(-20, 0, 20)
            self.weight_gain = base_weight_gain + deviation
        else:
            self.weight_gain = base_weight_gain

        # Pd-max is the maximum value of Pd curve
        self.Pd_max = 149.9799
        self.BP_at_Pd_max = 11.3016  # (Kg) Based on simulation (average of 10 times)
        self.weight += self.weight_gain / 1000  # Convert weight gain to kg

        # BP-at-maturity and Rate constant calculations
        self.BP_at_maturity = 2.7182 * self.BP_at_Pd_max  # (Kg)
        self.Rate_constant = 2.7182 * self.Pd_max / (self.BP_at_maturity * 1000)

        # ME intake calculation (Kcal/day)
        self.ME_intake = 10967 * (1 - math.exp(-math.exp(-3.803) * self.weight ** 0.9072))

        # Protein deposition (Pd) calculation (g/day)
        self.Prd = 137 * (0.7066 + 0.013289 * self.weight - 0.0001312 * self.weight ** 2 + 2.8627 * self.weight ** 3 * 10 ** -7)

        # Update body protein mass (BPm)
        self.BPm += self.Prd / 1000  # Convert Pd from g to kg

        # Maximum Pd after Pd-max starts to decline
        self.maximum_pd_after_pd_max_start_decline = self.BPm * 1000 * self.Rate_constant * math.log(self.BP_at_maturity / self.BPm)

        # Other body composition calculations
        self.Ash = 0.189 * self.BPm
        self.Wat = (4.322 + 0.0044 * self.Pd_max) * (self.BPm ** 0.855)  # Assuming P = BPm
        self.LCT = 17.9 - (0.0375 * self.weight)
        self.Minimum_space_for_maximum_ME_intake = 0.0336 * self.weight ** 0.667

        # Fraction of ME intake
        T = 20  # Placeholder for environmental temperature
        self.fraction_of_ME_intake = 1 - 0.012914 * (T - (self.LCT + 3)) - 0.001179 * (T - (self.LCT + 3)) ** 2

        # Maximum daily feed intake (g/day)
        self.maximum_daily_feed_intake = 111 * (self.weight ** 0.803) * (1.00 + 0.025 * (self.LCT - T))

        # Standard maintenance ME requirements (Kcal/day)
        self.standard_maintenance_ME_requirements = 197 * self.weight ** 0.60

        # ME requirements for thermogenesis (Kcal/day)
        self.ME_requirements_for_thermogenesis = 0.07425 * (self.LCT - T) * self.standard_maintenance_ME_requirements

        # Maintenance ME requirements
        if T < self.LCT:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements + self.ME_requirements_for_thermogenesis
        else:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements

        # Lipid deposition (Ld) calculation (g/day)
        self.Lid = (self.ME_intake - self.Maintenance_ME_requirements - (self.Prd * 10.6)) / 12.5

        # Update body lipid mass (BLm)
        self.BLm += self.Lid / 1000  # Convert Ld from g to kg

        # Calculate EBW (Empty Body Weight)
        self.EBW = self.BPm + self.BLm + self.Wat + self.Ash

        # Gut fill calculation
        self.Gut_fill = 0.3043 * self.EBW ** 0.5977

        # Probe backfat thickness (PBT) calculation
        self.PBT = -5 + (12.3 * self.BLm / self.BPm) + (0.13 * self.BPm)

        # Pd by energy intake calculation (g/day)
        adjustment = 0.001
        self.Pd_by_energy_int = (30 + (21 + 20 * math.exp(-0.021 * self.weight))
                                * (self.ME_intake - (1.3 * self.Maintenance_ME_requirements))
                                * (self.Pd_max / 125) * (1 + 0.015 * (20 - T))) * adjustment

        # Adjust maximum Pd
        if self.Prd > self.Prd_1:
            self.maximum_Pd = self.Pd_max
        else:
            self.maximum_Pd = self.maximum_pd_after_pd_max_start_decline

        # Update Prd_1 for the next step
        self.Prd_1 = self.Prd

        # Check if Ractopamine (RAC) is used
        if self.model.RAC:
            self.feed_rac()  # Call a separate method to handle RAC feeding
    
    def feed_b(self, stochastic_weight_gain):
        # Calculate base weight gain using the given formula
        base_weight_gain = -0.0765 * self.weight ** 2 + 14.162 * self.weight + 291.23

        # Check for stochastic weight gain
        if stochastic_weight_gain:
            # Generate deviation using random triangular distribution
            deviation = random.triangular(-20, 0, 20)
            self.weight_gain = base_weight_gain + deviation
        else:
            self.weight_gain = base_weight_gain

        # Pd-max and other constants
        self.Pd_max = 145.3477
        self.BP_at_Pd_max = 10.2483  # (Kg)
        self.weight += self.weight_gain / 1000  # Convert weight gain to kg

        # BP-at-maturity and Rate constant calculations
        self.BP_at_maturity = 2.7182 * self.BP_at_Pd_max
        self.Rate_constant = 2.7182 * self.Pd_max / (self.BP_at_maturity * 1000)

        # ME intake calculation (Kcal/day)
        self.ME_intake = 10447 * (1 - math.exp(-math.exp(-4.283) * self.weight ** 1.0843))

        # Protein deposition (Pd) calculation (g/day)
        self.Prd = 133 * (0.7078 + 0.013764 * self.weight - 0.00014211 * self.weight ** 2 + 3.2698 * self.weight ** 3 * 10 ** -7)

        # Update body protein mass (BPm)
        self.BPm += self.Prd / 1000

        # Maximum Pd after Pd-max starts to decline
        self.maximum_pd_after_pd_max_start_decline = self.BPm * 1000 * self.Rate_constant * math.log(self.BP_at_maturity / self.BPm)

        # Calculate Ash and Wat
        self.Ash = 0.189 * self.BPm
        self.Wat = (4.322 + 0.0044 * self.Pd_max) * (self.BPm ** 0.855)

        # Update feed intake
        self.update_feed_intake()

        # Calculate Lower Critical Temperature (LCT)
        self.LCT = 17.9 - (0.0375 * self.weight)
        self.Minimum_space_for_maximum_ME_intake = 0.0336 * self.weight ** 0.667

        # Calculate fraction of ME intake
        T = 20  # Placeholder for environmental temperature
        self.fraction_of_ME_intake = 1 - 0.012914 * (T - (self.LCT + 3)) - 0.001179 * (T - (self.LCT + 3)) ** 2

        # Maximum daily feed intake (g/day)
        self.maximum_daily_feed_intake = 111 * (self.weight ** 0.803) * (1.00 + 0.025 * (self.LCT - T))

        # Standard maintenance ME requirements (Kcal/day)
        self.standard_maintenance_ME_requirements = 197 * self.weight ** 0.60

        # ME requirements for thermogenesis (Kcal/day)
        self.ME_requirements_for_thermogenesis = 0.07425 * (self.LCT - T) * self.standard_maintenance_ME_requirements

        # Calculate Maintenance ME requirements
        if T < self.LCT:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements + self.ME_requirements_for_thermogenesis
        else:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements

        # Lipid deposition (Ld) calculation (g/day)
        self.Lid = (self.ME_intake - self.Maintenance_ME_requirements - (self.Prd * 10.6)) / 12.5

        # Update body lipid mass (BLm)
        self.BLm += self.Lid / 1000

        # Calculate EBW (Empty Body Weight)
        self.EBW = self.BPm + self.BLm + self.Wat + self.Ash

        # Gut fill calculation
        self.Gut_fill = 0.3043 * self.EBW ** 0.5977

        # Probe backfat thickness (PBT) calculation
        self.PBT = -5 + (12.3 * self.BLm / self.BPm) + (0.13 * self.BPm)

        # Pd by energy intake calculation (g/day)
        adjustment = 0.001
        self.Pd_by_energy_int = (30 + (21 + 20 * math.exp(-0.021 * self.weight))
                                * (self.ME_intake - (1.3 * self.Maintenance_ME_requirements))
                                * (self.Pd_max / 125) * (1 + 0.015 * (20 - T))) * adjustment

        # Adjust maximum Pd
        if self.Prd > self.Prd_1:
            self.maximum_Pd = self.Pd_max
        else:
            self.maximum_Pd = self.maximum_pd_after_pd_max_start_decline

        # Update Prd_1 for the next step
        self.Prd_1 = self.Prd

        # Check if Ractopamine (RAC) is used
        if self.model.RAC:
            self.feed_rac()  # Call a separate method to handle RAC feeding
    
    def feed_m(self, stochastic_weight_gain):
        """Simulates feeding behavior for male pigs."""

        # Calculate base weight gain using the provided equation
        base_weight_gain = -0.0603 * self.weight ** 2 + 12.043 * self.weight + 335.44 - 20

        # Determine weight gain, considering stochastic variation if applicable
        if stochastic_weight_gain:
            deviation = random.triangular(-20, 0, 20)  # Random triangular deviation
            self.weight_gain = base_weight_gain + deviation
        else:
            self.weight_gain = base_weight_gain

        # Update the weight (convert from g to kg)
        self.weight += self.weight_gain / 1000

        # Pd-max and related constants
        self.Pd_max = 165.5064
        self.BP_at_Pd_max = 13.6612
        self.BP_at_maturity = 2.7182 * self.BP_at_Pd_max
        self.Rate_constant = 2.7182 * self.Pd_max / (self.BP_at_maturity * 1000)

        # ME intake calculation (Kcal/day)
        self.ME_intake = 10638 * (1 - math.exp(-math.exp(-3.803) * self.weight ** 0.9072))

        # Protein deposition (Pd) calculation (g/day)
        self.Prd = 151 * (0.6558 + 0.012740 * self.weight - 0.00010390 * self.weight ** 2 + 1.64001 * self.weight ** 3 * 10 ** -7)

        # Update body protein mass (BPm)
        self.BPm += self.Prd / 1000

        # Maximum Pd after Pd-max starts to decline
        self.maximum_pd_after_pd_max_start_decline = self.BPm * 1000 * self.Rate_constant * math.log(self.BP_at_maturity / self.BPm)

        # Calculate Ash and Wat
        self.Ash = 0.189 * self.BPm
        self.Wat = (4.322 + 0.0044 * self.Pd_max) * (self.BPm ** 0.855)

        # Update feed intake
        self.update_feed_intake()

        # Calculate Lower Critical Temperature (LCT)
        self.LCT = 17.9 - (0.0375 * self.weight)
        self.Minimum_space_for_maximum_ME_intake = 0.0336 * self.weight ** 0.667

        # Placeholder for environmental temperature
        T = 20  # Adjust as needed
        self.fraction_of_ME_intake = 1 - 0.012914 * (T - (self.LCT + 3)) - 0.001179 * (T - (self.LCT + 3)) ** 2

        # Maximum daily feed intake (g/day)
        self.maximum_daily_feed_intake = 111 * (self.weight ** 0.803) * (1.00 + 0.025 * (self.LCT - T))

        # Standard maintenance ME requirements (Kcal/day)
        self.standard_maintenance_ME_requirements = 197 * self.weight ** 0.60

        # ME requirements for thermogenesis (Kcal/day)
        self.ME_requirements_for_thermogenesis = 0.07425 * (self.LCT - T) * self.standard_maintenance_ME_requirements

        # Calculate maintenance ME requirements
        if T < self.LCT:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements + self.ME_requirements_for_thermogenesis
        else:
            self.Maintenance_ME_requirements = self.standard_maintenance_ME_requirements

        # Lipid deposition (Ld) calculation (g/day)
        self.Lid = (self.ME_intake - self.Maintenance_ME_requirements - (self.Prd * 10.6)) / 12.5

        # Update body lipid mass (BLm)
        self.BLm += self.Lid / 1000

        # Calculate Empty Body Weight (EBW)
        self.EBW = self.BPm + self.BLm + self.Wat + self.Ash

        # Gut fill calculation
        self.Gut_fill = 0.3043 * self.EBW ** 0.5977

        # Probe backfat thickness (PBT) calculation
        self.PBT = -5 + (12.3 * self.BLm / self.BPm) + (0.13 * self.BPm)

        # Pd as determined by energy intake (g/day)
        adjustment = 0.001
        self.Pd_by_energy_int = (30 + (21 + 20 * math.exp(-0.021 * self.weight)) * 
                                (self.ME_intake - (1.3 * self.Maintenance_ME_requirements)) * 
                                (self.Pd_max / 125) * (1 + 0.015 * (20 - T))) * adjustment

        # Adjust maximum Pd based on conditions
        if self.Prd > self.Prd_1:
            self.maximum_Pd = self.Pd_max
        else:
            self.maximum_Pd = self.maximum_pd_after_pd_max_start_decline

        # Update Prd_1 for the next step
        self.Prd_1 = self.Prd

        # Check if the pig should be sold
        if self.weight > self.model.sell_weight:
            self.final_weight = self.weight
            self.fat_free_lean = (62.073 + 0.0308 * self.final_weight - 
                                1.0101 * self.PBT + 0.00774 * (self.PBT ** 2))
            self.sell_pig()  # Assuming there's a sell_pig method
    
    def feed_rac(self):
        """Simulates the effects of feeding Ractopamine (RAC) to pigs."""
        if self.RAC_day < 28:
            if self.weight > self.init_weight_rac:
                # Calculate Body Weight Gain from Ractopamine (BWG-rac)
                self.BWG_rac = self.weight - self.init_weight_rac

                # Calculate the proportional reduction in ME intake (MEIR) - Eq. 8-32
                self.MEIR = (-0.191263 + (0.019013 * self.BWG_rac) - 
                            (0.000443 * self.BWG_rac ** 2) + 
                            (0.000003539 * self.BWG_rac ** 3))

                # Estimate ME intake with Ractopamine (ME-intake-rac) - Eq. 8-33
                self.ME_intake_rac = ((1 - (self.MEIR * (self.RAC_level / 20) ** 0.7)) 
                                    * self.ME_intake)

                # Mean relative increase in RAC-induced Protein Deposition (Pd) - Eq. 8-34
                self.increase_Pd_rac = 0.33 * ((self.RAC_level / 20) ** 0.33)

                # Mean relative RAC-induced Pd adjusted for BWG-rac - Eq. 8-35
                self.Pd_rac_W = (1.73 + (0.00776 * self.BWG_rac) - 
                                (0.00205 * self.BWG_rac ** 2) + 
                                (0.000017 * self.BWG_rac ** 3) + 
                                (((0.1 * self.RAC_level) - 1) * (self.BWG_rac * 0.001875)))

                # RAC-induced Pd adjusted for RAC-day - Eq. 8-36
                self.Pd_rac_d = (1.714 + (0.01457 * self.RAC_day) - 
                                (0.00361 * self.RAC_day ** 2) + 
                                (0.000055 * self.RAC_day ** 3))

                # RAC-induced lean tissue gain - Eq. 8-38
                self.RAC_lean_tissue_gain = self.Pd_rac_W / 0.2

                # Adjusted Probe Backfat Thickness (PBT) with RAC effects - Eq. 8-39
                self.rac_PBT = self.PBT * (1 + 0.05 * self.RAC_day / 10) * ((self.RAC_level / 20) ** 0.7)

                # Increment the RAC-day counter
                self.RAC_day += 1

    def calculate_sid_amino_acids(self):
        """Calculate SID Amino Acids based on SID-lys."""
        self.Arg = self.SID_lys * 0.457
        self.His = self.SID_lys * 0.344
        self.Ile = self.SID_lys * 0.522
        self.Leu = self.SID_lys * 1.007
        self.Met = self.SID_lys * 0.289
        self.Meth_cys = self.SID_lys * 0.564
        self.Phe = self.SID_lys * 0.597
        self.Phe_tyr = self.SID_lys * 0.938
        self.Thr = self.SID_lys * 0.603
        self.Trp = self.SID_lys * 0.171
        self.Val = self.SID_lys * 0.649
        self.Nit = self.SID_lys * 2.148

    def calculate_minerals(self):
        """Calculate mineral requirements based on weight."""
        self.Sodium = -2.5588 + 1.1335 * math.log(self.weight)
        self.Chlorine = -2.0706 + 0.9068 * math.log(self.weight)
        self.Magnesium = -1.0353 + 0.4534 * math.log(self.weight)
        self.Potassium = -0.4591 + 1.0774 * math.log(self.weight)
        self.Copper = -0.8705 + 1.9286 * math.log(self.weight)
        self.Iodine = -0.3624 + 0.1587 * math.log(self.weight)
        self.Iron = 34.357 + 15.904 * math.log(self.weight)
        self.Manganese = -5.1766 + 2.2669 * math.log(self.weight)
        self.Selenium = -0.0924 + 0.1048 * math.log(self.weight)
        self.Zinc = -70.251 + 43.634 * math.log(self.weight)

    def calculate_vitamins(self):
        """Calculate vitamin requirements based on weight."""
        self.Vit_A = -3364.8 + 1473.5 * math.log(self.weight)
        self.Vit_D3 = -388.24 + 170.02 * math.log(self.weight)
        self.Vit_E = -28.471 + 12.468 * math.log(self.weight)
        self.Vit_K = -1.2941 + 0.5667 * math.log(self.weight)
        self.Biotin = -0.1294 + 0.0567 * math.log(self.weight)
        self.Choline = -0.7765 + 0.34 * math.log(self.weight)
        self.Folacin = -0.7765 + 0.34 * math.log(self.weight)
        self.Niacin = -77.649 + 34.004 * math.log(self.weight)
        self.Pantothenic_acid = -12.202 + 6.6304 * math.log(self.weight)
        self.Riboflavin = -2.2184 + 1.615 * math.log(self.weight)
        self.Thiamin = -2.5883 + 1.1335 * math.log(self.weight)
        self.Vit_B6 = -2.5883 + 1.1335 * math.log(self.weight)
        self.Vit_B12 = 16.64 + (-0.852) * math.log(self.weight)
        self.Linoleic_acid = -2.5883 + 1.1335 * math.log(self.weight)

    # In agent.py
def log_info(self):
    """Log detailed information about the pig."""
    print(f"Hi, it's day {self.model.num_days} ******************************************************************************************************************************************")
    print(f"My weight is: {round(self.weight, 4)} kg")
    print(f"My ME intake + wastage is: {round(self.ME_intake, 4)} kcal/day")
    print(f"My Pd is: {round(self.Prd, 4)} g/day")
    print(f"My LD is: {round(self.Lid, 4)} g/day")
    print(f"My BP is: {round(self.BPm, 4)} kg")
    print(f"My BL is: {round(self.BLm, 4)} kg")
    print(f"My Water is: {round(self.Wat, 4)} kg")
    print(f"My Ash is: {round(self.Ash, 4)} kg")
    print(f"My maintenance-ME-requirements is: {round(self.maintenance_ME_requirements, 4)} g/day")
    print(f"My feed intake + wastage is: {round(self.feed_intake, 4)} kg")
    if self.pig_type == "male":
        print(f"RAC-day: {self.RAC_day}")
    print("\n")