import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import random
import math

#Individual pig agent characteristics in agent class
class PigAgent:
    def __init__(self, breed, region, x, y, initial_weight=20):
        # Basic properties
        self.breed = breed  # 'gilt', 'barrow', or 'male'
        self.region = region
        self.x = x
        self.y = y
        self.weight = initial_weight - 1 + random.uniform(0, 2.0)
        
        # Body composition
        self.BPm = self.weight * 0.18    # Initial whole-body protein mass
        self.BLm = self.weight * 0.03    # Initial whole-body lipid mass
        self.init_Gut_fill = 0.277 * self.weight ** 0.612
        
        # Pd related properties
        if breed == 'gilt':
            self.Pd_max = 149.9799
            self.BP_at_Pd_max = 11.3016
        elif breed == 'barrow':
            self.Pd_max = 145.3477
            self.BP_at_Pd_max = 10.2483
        else:  # male
            self.Pd_max = 165.5064
            self.BP_at_Pd_max = 13.6612
            
        self.init_BLm_BPm = (0.305 - 0.000875 * self.Pd_max) * self.weight ** 0.45
        self.Prd_1 = 0
        self.RAC_day = 0
        
        # Additional properties required for simulation
        self.Ash = 0
        self.Wat = 0
        self.ME_intake = 0
        self.ME_intake_rac = 0
        self.Prd = 0
        self.maximum_Pd = self.Pd_max
        self.maximum_pd_after_pd_max_start_decline = 0
        self.BP_at_maturity = 0
        self.Rate_constant = 0
        self.Lid = 0
        self.feed_intake = 0
        self.feed_intake_es = 0
        self.LCT = 0
        self.Minimum_space_for_maximum_ME_intake = 0
        self.Fraction_of_ME_intake = 0
        self.maximum_daily_feed_intake = 0
        self.standard_maintenance_ME_requirements = 0
        self.ME_requirements_for_thermogenesis = 0
        self.Maintenance_ME_requirements = 0
        self.Gut_fill = 0
        self.EBW = 0
        self.PBT = 0
        self.fat_free_lean = 0
        self.final_weight = 0
        self.Pd_by_energy_int = 0
        
        # RAC related properties
        self.BWG_rac = 0
        self.MEIR = 0
        self.increase_Pd_rac = 0
        self.Pd_rac_W = 0
        self.Pd_rac_d = 0
        self.RAC_lean_tissue_gain = 0
        self.rac_PBT = 0
        
        # Amino acid requirements
        self.GIT_lys_loss = 0
        self.Integu_lys_loss = 0
        self.SID_lys_for_GIT = 0
        self.lys_in_Pd = 0
        self.SID_lys_for_pd = 0
        self.SID_lys = 0
        self.Ferm_SID_thr = 0
        
        # Calcium and Phosphorus
        self.P = 0
        self.maximum_P_retention = 0
        self.STTD_P = 0
        self.Total_Ca = 0
        
        # Amino acids
        self.Arg = 0
        self.His = 0
        self.Ile = 0
        self.Leu = 0
        self.Met = 0
        self.Meth_cys = 0
        self.Phe = 0
        self.Phe_tyr = 0
        self.Thr = 0
        self.Trp = 0
        self.Val = 0
        self.Nit = 0
        
        # Minerals
        self.Sodium = 0
        self.Chlorine = 0
        self.Magnesium = 0
        self.Potassium = 0
        self.Copper = 0
        self.Iodine = 0
        self.Iron = 0
        self.Manganese = 0
        self.Selenium = 0
        self.Zinc = 0
        
        # Vitamins
        self.Vit_A = 0
        self.Vit_D3 = 0
        self.Vit_E = 0
        self.Vit_K = 0
        self.Biotin = 0
        self.Choline = 0
        self.Folacin = 0
        self.Niacin = 0
        self.Pantothenic_acid = 0
        self.Riboflavin = 0
        self.Thiamin = 0
        self.Vit_B6 = 0
        self.Vit_B12 = 0
        self.Linoleic_acid = 0
        
        # Track weight gain
        self.weight_gain = 0

    def move(self, region_boundaries, world_width, world_height):
        # Move the pig randomly within its region
        angle = random.uniform(-30, 30)
        self.x += 0.4 * math.cos(math.radians(angle))
        self.y += 0.4 * math.sin(math.radians(angle))
        
        # Keep within the region boundaries
        region_min_x = region_boundaries[self.region-1][0]
        region_max_x = region_boundaries[self.region-1][1]
        
        if self.x < region_min_x:
            self.x = region_min_x
        elif self.x > region_max_x:
            self.x = region_max_x
            
        # Keep within world boundaries for y
        if self.y > world_height - 1:
            self.y = world_height - 1
        elif self.y < 1:
            self.y = 1

    def feed(self, environmental_temperature, T, ME_content, stochastic_weight_gain,
             ME_requirements_for_increased_activity_or_genotype_adjustment, RAC, 
             init_weight_rac, RAC_level, Dry_matter, ferm_fiber_content, sell_weight):
        """
        Simulate feeding and growth for a pig
        Returns True if pig should be sold, False otherwise
        """
        # Calculate weight gain based on breed
        if self.breed == 'gilt':
            if stochastic_weight_gain:
                base_weight_gain = -0.0477 * self.weight ** 2 + 8.8503 * self.weight + 485.17
                deviation = self.random_triangular(-20, 0, 20)
                self.weight_gain = base_weight_gain + deviation
            else:
                self.weight_gain = -0.0477 * self.weight ** 2 + 8.8503 * self.weight + 485.17
                
            # Calculate ME intake
            self.ME_intake = 10967 * (1 - math.exp(-math.exp(-3.803) * self.weight ** 0.9072))
            
            # Calculate protein deposition
            self.Prd = 137 * (0.7066 + 0.013289 * self.weight - 0.0001312 * self.weight ** 2 + 2.8627 * self.weight ** 3 * 10 ** (-7))
            
        elif self.breed == 'barrow':
            if stochastic_weight_gain:
                base_weight_gain = -0.0765 * self.weight ** 2 + 14.162 * self.weight + 291.23
                deviation = self.random_triangular(-20, 0, 20)
                self.weight_gain = base_weight_gain + deviation
            else:
                self.weight_gain = -0.0765 * self.weight ** 2 + 14.162 * self.weight + 291.23
                
            # Calculate ME intake
            self.ME_intake = 10447 * (1 - math.exp(-math.exp(-4.283) * self.weight ** 1.0843))
            
            # Calculate protein deposition
            self.Prd = 133 * (0.7078 + 0.013764 * self.weight - 0.00014211 * self.weight ** 2 + 3.2698 * self.weight ** 3 * 10 ** (-7))
            
        else:  # male
            if stochastic_weight_gain:
                base_weight_gain = -0.0603 * self.weight ** 2 + 12.043 * self.weight + 335.44 - 20
                deviation = self.random_triangular(-20, 0, 20)
                self.weight_gain = base_weight_gain + deviation
            else:
                self.weight_gain = -0.0603 * self.weight ** 2 + 12.043 * self.weight + 335.44
                
            # Calculate ME intake
            self.ME_intake = 10638 * (1 - math.exp(-math.exp(-3.803) * self.weight ** 0.9072))
            
            # Calculate protein deposition
            self.Prd = 151 * (0.6558 + 0.012740 * self.weight - 0.00010390 * self.weight ** 2 + 1.64001 * self.weight ** 3 * 10 ** (-7))
        
        # Update weight
        self.weight += (self.weight_gain / 1000)
        
        # Update body composition
        self.BP_at_maturity = 2.7182 * self.BP_at_Pd_max
        self.Rate_constant = 2.7182 * self.Pd_max / (self.BP_at_maturity * 1000)
        
        # Update protein mass
        self.BPm += self.Prd / 1000
        
        # Calculate maximum protein deposition after Pd max starts to decline
        self.maximum_pd_after_pd_max_start_decline = self.BPm * 1000 * self.Rate_constant * math.log(self.BP_at_maturity / self.BPm)
        
        # Update ash and water content
        self.Ash = 0.189 * self.BPm
        self.P = 1.1613 + 26.012 * self.BPm + 0.2299 * self.BPm ** 2
        self.Wat = (4.322 + 0.0044 * self.Pd_max) * (self.P ** 0.855)
        
        # Update Lower Critical Temperature (LCT)
        self.LCT = 17.9 - (0.0375 * self.weight)
        
        # Update space requirements
        self.Minimum_space_for_maximum_ME_intake = 0.0336 * self.weight ** 0.667
        
        # Calculate fraction of ME intake based on temperature
        self.Fraction_of_ME_intake = 1 - 0.012914 * (T - (self.LCT + 3)) - 0.001179 * (T - (self.LCT + 3)) ** 2
        
        # Calculate maximum daily feed intake
        self.maximum_daily_feed_intake = 111 * (self.weight ** 0.803) * (1.00 + 0.025 * (self.LCT - T))
        
        # Calculate standard maintenance ME requirements
        self.standard_maintenance_ME_requirements = 197 * self.weight ** 0.60
        
        # Calculate ME requirements for thermogenesis
        self.ME_requirements_for_thermogenesis = 0.07425 * (self.LCT - T) * self.standard_maintenance_ME_requirements
        
        # Calculate total maintenance ME requirements
        if environmental_temperature:
            self.Maintenance_ME_requirements = (self.standard_maintenance_ME_requirements + 
                                             self.ME_requirements_for_thermogenesis + 
                                             ME_requirements_for_increased_activity_or_genotype_adjustment)
        else:
            self.Maintenance_ME_requirements = (self.standard_maintenance_ME_requirements + 
                                            ME_requirements_for_increased_activity_or_genotype_adjustment)
        
        # Calculate lipid deposition
        self.Lid = (self.ME_intake - self.Maintenance_ME_requirements - (self.Prd * 10.6)) / 12.5
        
        # Update lipid mass
        self.BLm += self.Lid / 1000
        
        # Calculate empty body weight (EBW)
        self.EBW = self.BPm + self.BLm + self.Wat + self.Ash
        
        # Calculate gut fill
        self.Gut_fill = 0.3043 * self.EBW ** 0.5977
        
        # Calculate probe backfat thickness
        self.PBT = -5 + (12.3 * self.BLm / self.BPm) + (0.13 * self.BPm)
        
        # Calculate Pd by energy intake
        adjustment = 0.001
        self.Pd_by_energy_int = (30 + (21 + 20 * math.exp((-0.021) * self.weight)) * 
                               (self.ME_intake - (1.3 * self.Maintenance_ME_requirements)) * 
                               (self.Pd_max / 125) * (1 + (0.015 * (20 - T)))) * adjustment
        
        # Determine maximum Pd
        if self.Prd > self.Prd_1:
            self.maximum_Pd = self.Pd_max
        else:
            self.maximum_Pd = self.maximum_pd_after_pd_max_start_decline
        
        self.Prd_1 = self.Prd
        
        # Calculate feed intake based on breed
        self.update_feed_intake(ME_content)
        
        # Apply ractopamine effects if enabled
        if RAC:
            self.feed_rac(init_weight_rac, RAC_level)
        
        # Calculate amino acid requirements
        self.calculate_amino_acid_requirements(ferm_fiber_content)
        
        # Calculate mineral requirements
        self.calculate_minerals()
        
        # Calculate vitamin requirements
        self.calculate_vitamins()
        
        # Calculate phosphorus requirements
        self.calculate_phosphorus_requirements(Dry_matter)
        
        # Check if the pig should be sold
        if self.weight > sell_weight:
            self.final_weight = self.weight
            self.fat_free_lean = 62.073 + 0.0308 * self.final_weight - 1.0101 * self.PBT + 0.00774 * self.PBT ** 2
            return True
        
        return False
    
    def random_triangular(self, a, b, c):
        """
        Generate a random number from a triangular distribution
        """
        U = random.random()
        if U < (c - a) / (b - a):
            return a + math.sqrt(U * (b - a) * (c - a))
        else:
            return b - math.sqrt((1 - U) * (b - a) * (b - c))
    
    def update_feed_intake(self, ME_content):
        """
        Update feed intake based on pig breed
        """
        if self.breed == 'gilt':
            self.feed_intake_es = 1.053 * self.ME_intake / ME_content
            self.feed_intake = 2.755 * (1 - (math.exp(-math.exp(-4.755) * (self.weight ** 1.214))))
        elif self.breed == 'barrow':
            self.feed_intake_es = 1.053 * self.ME_intake / ME_content
            self.feed_intake = 2.88 * (1 - (math.exp(-math.exp(-5.921) * (self.weight ** 1.512))))
        else:  # male
            self.feed_intake = 1.053 * self.ME_intake / ME_content
    
    def feed_rac(self, init_weight_rac, RAC_level):
        """
        Apply ractopamine effects if the pig is heavy enough and has been on RAC for less than 28 days
        """
        if self.RAC_day < 28:
            if self.weight > init_weight_rac:
                self.BWG_rac = self.weight - init_weight_rac
                
                # Calculate MEIR (proportional reduction in ME intake)
                self.MEIR = -0.191263 + (0.019013 * self.BWG_rac) - (0.000443 * self.BWG_rac ** 2) + (0.000003539 * self.BWG_rac ** 3)
                
                # Calculate ME intake with RAC
                self.ME_intake_rac = (1 - (self.MEIR * (RAC_level / 20) ** 0.7)) * self.ME_intake
                
                # Calculate increase in Pd due to RAC
                self.increase_Pd_rac = 0.33 * ((RAC_level / 20) ** 0.33)
                
                # Calculate Pd_rac_W and Pd_rac_d
                self.Pd_rac_W = (1.73 + (0.00776 * self.BWG_rac) - 
                                (0.00205 * self.BWG_rac ** 2) + 
                                (0.000017 * self.BWG_rac ** 3) + 
                                (((0.1 * RAC_level) - 1) * (self.BWG_rac * 0.001875)))
                
                self.Pd_rac_d = (1.714 + (0.01457 * self.RAC_day) - 
                                (0.00361 * self.RAC_day ** 2) + 
                                (0.000055 * self.RAC_day ** 3))
                
                # Calculate RAC-induced lean tissue gain
                self.RAC_lean_tissue_gain = self.Pd_rac_W / 0.2
                
                # Calculate probe backfat thickness adjusted for RAC
                self.rac_PBT = self.PBT * (1 + 0.05 * self.RAC_day / 10) * ((RAC_level / 20) ** 0.7)
                
                # Increment RAC day
                self.RAC_day += 1
    
    def calculate_amino_acid_requirements(self, ferm_fiber_content):
        """
        Calculate amino acid requirements
        """
        # Lysine requirements
        self.GIT_lys_loss = self.feed_intake * (0.417 / 1000) * 0.88 * 1.1
        self.Integu_lys_loss = 0.0045 * self.weight ** 0.75
        self.SID_lys_for_GIT = (self.GIT_lys_loss + self.Integu_lys_loss) / (0.75 + 0.002 * (self.maximum_Pd - 147.7))
        self.lys_in_Pd = (self.Prd * 0.0710) + (self.Pd_rac_W * 0.0822)
        self.SID_lys_for_pd = (self.lys_in_Pd / (0.75 + (0.002 * (self.maximum_Pd - 147.7)))) * (1 + 0.0547 + (0.002215 * self.weight))
        self.SID_lys = self.SID_lys_for_GIT + self.SID_lys_for_pd
        self.Ferm_SID_thr = (self.feed_intake / 1000) * ferm_fiber_content * 0.0042
        
        # Calculate other amino acids based on SID_lys
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
        """
        Calculate mineral requirements
        """
        weight_ln = math.log(self.weight)
        self.Sodium = -2.5588 + 1.1335 * weight_ln
        self.Chlorine = -2.0706 + 0.9068 * weight_ln
        self.Magnesium = -1.0353 + 0.4534 * weight_ln
        self.Potassium = -0.4591 + 1.0774 * weight_ln
        self.Copper = -0.8705 + 1.9286 * weight_ln
        self.Iodine = -0.3624 + 0.1587 * weight_ln
        self.Iron = 34.357 + 15.904 * weight_ln
        self.Manganese = -5.1766 + 2.2669 * weight_ln
        self.Selenium = -0.0924 + 0.1048 * weight_ln
        self.Zinc = -70.251 + 43.634 * weight_ln
    
    def calculate_vitamins(self):
        """
        Calculate vitamin requirements
        """
        weight_ln = math.log(self.weight)
        self.Vit_A = -3364.8 + 1473.5 * weight_ln
        self.Vit_D3 = -388.24 + 170.02 * weight_ln
        self.Vit_E = -28.471 + 12.468 * weight_ln
        self.Vit_K = -1.2941 + 0.5667 * weight_ln
        self.Biotin = -0.1294 + 0.0567 * weight_ln
        self.Choline = -0.7765 + 0.34 * weight_ln
        self.Folacin = -0.7765 + 0.34 * weight_ln
        self.Niacin = -77.649 + 34.004 * weight_ln
        self.Pantothenic_acid = -12.202 + 6.6304 * weight_ln
        self.Riboflavin = -2.2184 + 1.615 * weight_ln
        self.Thiamin = -2.5883 + 1.1335 * weight_ln
        self.Vit_B6 = -2.5883 + 1.1335 * weight_ln
        self.Vit_B12 = 16.64 + (-0.852) * weight_ln
        self.Linoleic_acid = -2.5883 + 1.1335 * weight_ln
    
    def calculate_phosphorus_requirements(self, Dry_matter):
        """
        Calculate phosphorus and calcium requirements
        """
        # Set maximum P retention based on breed
        if self.breed == 'gilt':
            self.maximum_P_retention = 3.824
        elif self.breed == 'barrow':
            self.maximum_P_retention = 3.550
        else:  # male
            self.maximum_P_retention = 4.610
        
        self.feed_dry_intake = self.feed_intake * Dry_matter
        self.STTD_P = 0.85 * ((self.maximum_P_retention / 0.77) + 0.19 * self.feed_dry_intake + 0.007 * self.weight)
        self.Total_Ca = self.STTD_P * 2.15


class PigGrowthSimulation:
    def __init__(self):
        # Simulation parameters
        self.init_weight = 20
        self.sell_weight = 130
        self.total_feed_intake = 0
        self.init_weight_rac = 78
        self.days = 0
        self.sold_count = 0
        
        # Configure world and regions
        self.world_width = 30  # equivalent to max-pxcor - min-pxcor + 1
        self.world_height = 30  # equivalent to max-pycor - min-pycor + 1
        self.num_regions = 5
        self.region_boundaries = self.calculate_region_boundaries(self.num_regions)
        
        # Lists to hold pig agents
        self.gilts = []
        self.barrows = []
        self.males = []
        
        # Data for plotting
        self.days_data = []
        self.total_feed_intake_data = []
        self.pig_count_data = []
        self.sold_count_data = []
        
        # Data for individual pig tracking
        self.tracked_pig_data = {
            'gilt': {'weight': [], 'feed_intake': [], 'ME_intake': [], 'Prd': [], 'Lid': [], 'BPm': [], 'BLm': [], 'PBT': [], 'weight_gain': [], 'SID_lys': []},
            'barrow': {'weight': [], 'feed_intake': [], 'ME_intake': [], 'Prd': [], 'Lid': [], 'BPm': [], 'BLm': [], 'PBT': [], 'weight_gain': [], 'SID_lys': []},
            'male': {'weight': [], 'feed_intake': [], 'ME_intake': [], 'Prd': [], 'Lid': [], 'BPm': [], 'BLm': [], 'PBT': [], 'weight_gain': [], 'SID_lys': []}
        }
        
        # Track specific pigs
        self.tracked_gilt = None
        self.tracked_barrow = None
        self.tracked_male = None
    
    def calculate_region_boundaries(self, num_regions):
        """
        Calculate the boundaries of each region
        Returns a list of [min_x, max_x] for each region
        """
        region_width = self.world_width / num_regions
        boundaries = []
        
        for i in range(num_regions):
            min_x = -self.world_width/2 + i * region_width
            max_x = min_x + region_width - 1
            boundaries.append([min_x, max_x])
        
        return boundaries
    
    def setup(self, pig_R1, pig_R2, pig_R3, pig_R4, pig_R5):
        """
        Initialize the simulation
        """
        # Reset simulation variables
        self.days = 0
        self.sold_count = 0
        self.total_feed_intake = 0
        
        # Clear pig lists
        self.gilts = []
        self.barrows = []
        self.males = []
        
        # Clear data for plotting
        self.days_data = []
        self.total_feed_intake_data = []
        self.pig_count_data = []
        self.sold_count_data = []
        
        # Reset tracked pig data
        for breed in self.tracked_pig_data:
            for data_type in self.tracked_pig_data[breed]:
                self.tracked_pig_data[breed][data_type] = []
        
        # Create initial populations of pigs in each region
        pigs_per_region = [pig_R1, pig_R2, pig_R3, pig_R4, pig_R5]
        
        for region_num, num_pigs in enumerate(pigs_per_region, 1):
            # Create gilts
            for _ in range(random.randint(0, num_pigs)):
                x = random.uniform(self.region_boundaries[region_num-1][0], self.region_boundaries[region_num-1][1])
                y = random.uniform(-self.world_height/2 + 1, self.world_height/2 - 1)
                pig = PigAgent('gilt', region_num, x, y, self.init_weight)
                self.gilts.append(pig)
            
            # Create barrows
            for _ in range(random.randint(0, num_pigs)):
                x = random.uniform(self.region_boundaries[region_num-1][0], self.region_boundaries[region_num-1][1])
                y = random.uniform(-self.world_height/2 + 1, self.world_height/2 - 1)
                pig = PigAgent('barrow', region_num, x, y, self.init_weight)
                self.barrows.append(pig)
            
            # Create males
            for _ in range(random.randint(0, num_pigs)):
                x = random.uniform(self.region_boundaries[region_num-1][0], self.region_boundaries[region_num-1][1])
                y = random.uniform(-self.world_height/2 + 1, self.world_height/2 - 1)
                pig = PigAgent('male', region_num, x, y, self.init_weight)
                self.males.append(pig)
        
        # Set up tracked pigs (one of each breed if available)
        if self.gilts:
            self.tracked_gilt = self.gilts[0]
        if self.barrows:
            self.tracked_barrow = self.barrows[0]
        if self.males:
            self.tracked_male = self.males[0]
        
        print("Simulation setup complete.")
        print(f"Initial populations - Gilts: {len(self.gilts)}, Barrows: {len(self.barrows)}, Males: {len(self.males)}")
    
    def go(self, environmental_temperature, T, ME_content, stochastic_weight_gain, 
           ME_requirements_for_increased_activity_or_genotype_adjustment, RAC, 
           RAC_level, Dry_matter, ferm_fiber_content, selling_rate=100):
        """
        Run one day of the simulation
        """
        self.days += 1
        
        # Move all pigs
        for pig in self.gilts + self.barrows + self.males:
            pig.move(self.region_boundaries, self.world_width, self.world_height)
        
        # Feed gilts and check if any should be sold
        sold_gilts = []
        for pig in self.gilts:
            if pig.feed(environmental_temperature, T, ME_content, stochastic_weight_gain,
                       ME_requirements_for_increased_activity_or_genotype_adjustment, RAC,
                       self.init_weight_rac, RAC_level, Dry_matter, ferm_fiber_content, self.sell_weight):
                if random.randint(0, 99) < selling_rate:
                    sold_gilts.append(pig)
                    self.sold_count += 1
        
        # Feed barrows and check if any should be sold
        sold_barrows = []
        for pig in self.barrows:
            if pig.feed(environmental_temperature, T, ME_content, stochastic_weight_gain,
                       ME_requirements_for_increased_activity_or_genotype_adjustment, RAC,
                       self.init_weight_rac, RAC_level, Dry_matter, ferm_fiber_content, self.sell_weight):
                if random.randint(0, 99) < selling_rate:
                    sold_barrows.append(pig)
                    self.sold_count += 1
        
        # Feed males and check if any should be sold
        sold_males = []
        for pig in self.males:
            if pig.feed(environmental_temperature, T, ME_content, stochastic_weight_gain,
                       ME_requirements_for_increased_activity_or_genotype_adjustment, RAC,
                       self.init_weight_rac, RAC_level, Dry_matter, ferm_fiber_content, self.sell_weight):
                if random.randint(0, 99) < selling_rate:
                    sold_males.append(pig)
                    self.sold_count += 1
        
        # Remove sold pigs
        for pig in sold_gilts:
            self.gilts.remove(pig)
        for pig in sold_barrows:
            self.barrows.remove(pig)
        for pig in sold_males:
            self.males.remove(pig)
        
        # Calculate total feed intake
        self.total_feed_intake = sum(pig.feed_intake for pig in self.gilts + self.barrows + self.males)
        
        # Store data for plotting
        self.days_data.append(self.days)
        self.total_feed_intake_data.append(self.total_feed_intake)
        self.pig_count_data.append(len(self.gilts) + len(self.barrows) + len(self.males))
        self.sold_count_data.append(self.sold_count)
        
        # Store data for tracked pigs
        if self.tracked_gilt in self.gilts:
            self.tracked_pig_data['gilt']['weight'].append(self.tracked_gilt.weight)
            self.tracked_pig_data['gilt']['feed_intake'].append(self.tracked_gilt.feed_intake)
            self.tracked_pig_data['gilt']['ME_intake'].append(self.tracked_gilt.ME_intake)
            self.tracked_pig_data['gilt']['Prd'].append(self.tracked_gilt.Prd)
            self.tracked_pig_data['gilt']['Lid'].append(self.tracked_gilt.Lid)
            self.tracked_pig_data['gilt']['BPm'].append(self.tracked_gilt.BPm)
            self.tracked_pig_data['gilt']['BLm'].append(self.tracked_gilt.BLm)
            self.tracked_pig_data['gilt']['PBT'].append(self.tracked_gilt.PBT)
            self.tracked_pig_data['gilt']['weight_gain'].append(self.tracked_gilt.weight_gain)
            self.tracked_pig_data['gilt']['SID_lys'].append(self.tracked_gilt.SID_lys)
        
        if self.tracked_barrow in self.barrows:
            self.tracked_pig_data['barrow']['weight'].append(self.tracked_barrow.weight)
            self.tracked_pig_data['barrow']['feed_intake'].append(self.tracked_barrow.feed_intake)
            self.tracked_pig_data['barrow']['ME_intake'].append(self.tracked_barrow.ME_intake)
            self.tracked_pig_data['barrow']['Prd'].append(self.tracked_barrow.Prd)
            self.tracked_pig_data['barrow']['Lid'].append(self.tracked_barrow.Lid)
            self.tracked_pig_data['barrow']['BPm'].append(self.tracked_barrow.BPm)
            self.tracked_pig_data['barrow']['BLm'].append(self.tracked_barrow.BLm)
            self.tracked_pig_data['barrow']['PBT'].append(self.tracked_barrow.PBT)
            self.tracked_pig_data['barrow']['weight_gain'].append(self.tracked_barrow.weight_gain)
            self.tracked_pig_data['barrow']['SID_lys'].append(self.tracked_barrow.SID_lys)
        
        if self.tracked_male in self.males:
            self.tracked_pig_data['male']['weight'].append(self.tracked_male.weight)
            self.tracked_pig_data['male']['feed_intake'].append(self.tracked_male.feed_intake)
            self.tracked_pig_data['male']['ME_intake'].append(self.tracked_male.ME_intake)
            self.tracked_pig_data['male']['Prd'].append(self.tracked_male.Prd)
            self.tracked_pig_data['male']['Lid'].append(self.tracked_male.Lid)
            self.tracked_pig_data['male']['BPm'].append(self.tracked_male.BPm)
            self.tracked_pig_data['male']['BLm'].append(self.tracked_male.BLm)
            self.tracked_pig_data['male']['PBT'].append(self.tracked_male.PBT)
            self.tracked_pig_data['male']['weight_gain'].append(self.tracked_male.weight_gain)
            self.tracked_pig_data['male']['SID_lys'].append(self.tracked_male.SID_lys)
        
        print(f"Day {self.days}: Total pigs = {len(self.gilts) + len(self.barrows) + len(self.males)}, "
              f"Feed intake = {self.total_feed_intake:.2f} kg, Sold = {self.sold_count}")
        
        # Check if simulation should end
        if self.days >= 140:
            return False
        return True
    
    def display_pig_info(self):
        """
        Display information about tracked pigs
        """
        if self.tracked_gilt in self.gilts:
            print("\nTracked Gilt Information:")
            print(f"Weight: {self.tracked_gilt.weight:.2f} kg")
            print(f"ME intake: {self.tracked_gilt.ME_intake:.2f} kcal/day")
            print(f"Pd: {self.tracked_gilt.Prd:.2f} g/day")
            print(f"Ld: {self.tracked_gilt.Lid:.2f} g/day")
            print(f"BP: {self.tracked_gilt.BPm:.2f} kg")
            print(f"BL: {self.tracked_gilt.BLm:.2f} kg")
            print(f"Feed intake: {self.tracked_gilt.feed_intake:.2f} kg")
        
        if self.tracked_barrow in self.barrows:
            print("\nTracked Barrow Information:")
            print(f"Weight: {self.tracked_barrow.weight:.2f} kg")
            print(f"ME intake: {self.tracked_barrow.ME_intake:.2f} kcal/day")
            print(f"Pd: {self.tracked_barrow.Prd:.2f} g/day")
            print(f"Ld: {self.tracked_barrow.Lid:.2f} g/day")
            print(f"BP: {self.tracked_barrow.BPm:.2f} kg")
            print(f"BL: {self.tracked_barrow.BLm:.2f} kg")
            print(f"Feed intake: {self.tracked_barrow.feed_intake:.2f} kg")
        
        if self.tracked_male in self.males:
            print("\nTracked Male Information:")
            print(f"Weight: {self.tracked_male.weight:.2f} kg")
            print(f"ME intake: {self.tracked_male.ME_intake:.2f} kcal/day")
            print(f"Pd: {self.tracked_male.Prd:.2f} g/day")
            print(f"Ld: {self.tracked_male.Lid:.2f} g/day")
            print(f"BP: {self.tracked_male.BPm:.2f} kg")
            print(f"BL: {self.tracked_male.BLm:.2f} kg")
            print(f"Feed intake: {self.tracked_male.feed_intake:.2f} kg")
    
    def create_plots(self):
        """
        Create and display plots for the simulation results
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('Pig Growth Simulation Results', fontsize=16)
        
        # External Parameters plot
        ax1 = fig.add_subplot(231)
        ax1.plot(self.days_data, self.pig_count_data, label='Pigs')
        ax1.plot(self.days_data, self.sold_count_data, label='Sold Pigs')
        ax1.plot(self.days_data, self.total_feed_intake_data, label='Daily Feed Intake (kg)')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Count / kg')
        ax1.set_title('External Parameters')
        ax1.legend()
        ax1.grid(True)
        
        # Weight plot
        ax2 = fig.add_subplot(232)
        if self.tracked_pig_data['gilt']['weight']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['gilt']['weight'])], 
                    self.tracked_pig_data['gilt']['weight'], label='Gilt')
        if self.tracked_pig_data['barrow']['weight']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['barrow']['weight'])], 
                    self.tracked_pig_data['barrow']['weight'], label='Barrow')
        if self.tracked_pig_data['male']['weight']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['male']['weight'])], 
                    self.tracked_pig_data['male']['weight'], label='Male')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Weight (kg)')
        ax2.set_title('Weight')
        ax2.legend()
        ax2.grid(True)
        
        # Pd plot
        ax3 = fig.add_subplot(233)
        if self.tracked_pig_data['gilt']['Prd']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['gilt']['Prd'])], 
                    self.tracked_pig_data['gilt']['Prd'], label='Gilt')
        if self.tracked_pig_data['barrow']['Prd']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['barrow']['Prd'])], 
                    self.tracked_pig_data['barrow']['Prd'], label='Barrow')
        if self.tracked_pig_data['male']['Prd']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['male']['Prd'])], 
                    self.tracked_pig_data['male']['Prd'], label='Male')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Pd (g/day)')
        ax3.set_title('Protein Deposition')
        ax3.legend()
        ax3.grid(True)
        
        # Ld plot
        ax4 = fig.add_subplot(234)
        if self.tracked_pig_data['gilt']['Lid']:
            ax4.plot(self.days_data[:len(self.tracked_pig_data['gilt']['Lid'])], 
                    self.tracked_pig_data['gilt']['Lid'], label='Gilt')
        if self.tracked_pig_data['barrow']['Lid']:
            ax4.plot(self.days_data[:len(self.tracked_pig_data['barrow']['Lid'])], 
                    self.tracked_pig_data['barrow']['Lid'], label='Barrow')
        if self.tracked_pig_data['male']['Lid']:
            ax4.plot(self.days_data[:len(self.tracked_pig_data['male']['Lid'])], 
                    self.tracked_pig_data['male']['Lid'], label='Male')
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Ld (g/day)')
        ax4.set_title('Lipid Deposition')
        ax4.legend()
        ax4.grid(True)
        
        # ME intake plot
        ax5 = fig.add_subplot(235)
        if self.tracked_pig_data['gilt']['ME_intake']:
            ax5.plot(self.days_data[:len(self.tracked_pig_data['gilt']['ME_intake'])], 
                    self.tracked_pig_data['gilt']['ME_intake'], label='Gilt')
        if self.tracked_pig_data['barrow']['ME_intake']:
            ax5.plot(self.days_data[:len(self.tracked_pig_data['barrow']['ME_intake'])], 
                    self.tracked_pig_data['barrow']['ME_intake'], label='Barrow')
        if self.tracked_pig_data['male']['ME_intake']:
            ax5.plot(self.days_data[:len(self.tracked_pig_data['male']['ME_intake'])], 
                    self.tracked_pig_data['male']['ME_intake'], label='Male')
        ax5.set_xlabel('Days')
        ax5.set_ylabel('ME Intake (kcal/day)')
        ax5.set_title('Metabolizable Energy Intake')
        ax5.legend()
        ax5.grid(True)
        
        # Feed intake plot
        ax6 = fig.add_subplot(236)
        if self.tracked_pig_data['gilt']['feed_intake']:
            ax6.plot(self.days_data[:len(self.tracked_pig_data['gilt']['feed_intake'])], 
                    self.tracked_pig_data['gilt']['feed_intake'], label='Gilt')
        if self.tracked_pig_data['barrow']['feed_intake']:
            ax6.plot(self.days_data[:len(self.tracked_pig_data['barrow']['feed_intake'])], 
                    self.tracked_pig_data['barrow']['feed_intake'], label='Barrow')
        if self.tracked_pig_data['male']['feed_intake']:
            ax6.plot(self.days_data[:len(self.tracked_pig_data['male']['feed_intake'])], 
                    self.tracked_pig_data['male']['feed_intake'], label='Male')
        ax6.set_xlabel('Days')
        ax6.set_ylabel('Feed Intake (kg/day)')
        ax6.set_title('Feed Intake')
        ax6.legend()
        ax6.grid(True)
        
        # Adjust layout and display plot
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
        
        # Create additional plots (probe backfat thickness, weight gain, SID lysine)
        fig2 = plt.figure(figsize=(15, 5))
        fig2.suptitle('Additional Pig Growth Metrics', fontsize=16)
        
        '''# PBT plot
        ax1 = fig2.add_subplot(131)
        if self.tracked_pig_data['gilt']['PBT']:
            ax1.plot(self.days_data[:len(self.tracked_pig_data['gilt']['PBT'])], 
                    self.tracked_pig_data['gilt']['PBT'], label='Gilt')
        if self.tracked_pig_data['barrow']['PBT']:
            ax1.plot(self.days_data[:len(self.tracked_pig_data['barrow']['PBT'])], 
                    self.tracked_pig_data['barrow']['PBT'], label='Barrow')
        if self.tracked_pig_data['male']['PBT']:
            ax1.plot(self.days_data[:len(self.tracked_pig_data['male']['PBT'])], 
                    self.tracked_pig_data['male']['PBT'], label='Male')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('PBT (mm)')
        ax1.set_title('Probe Backfat Thickness')
        ax1.legend()
        ax1.grid(True)'''
        
        '''# Weight gain plot
        ax2 = fig2.add_subplot(132)
        if self.tracked_pig_data['gilt']['weight_gain']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['gilt']['weight_gain'])], 
                    self.tracked_pig_data['gilt']['weight_gain'], label='Gilt')
        if self.tracked_pig_data['barrow']['weight_gain']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['barrow']['weight_gain'])], 
                    self.tracked_pig_data['barrow']['weight_gain'], label='Barrow')
        if self.tracked_pig_data['male']['weight_gain']:
            ax2.plot(self.days_data[:len(self.tracked_pig_data['male']['weight_gain'])], 
                    self.tracked_pig_data['male']['weight_gain'], label='Male')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Weight Gain (g/day)')
        ax2.set_title('Daily Weight Gain')
        ax2.legend()
        ax2.grid(True)'''
        
        '''# SID lysine plot
        ax3 = fig2.add_subplot(133)
        if self.tracked_pig_data['gilt']['SID_lys']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['gilt']['SID_lys'])], 
                    self.tracked_pig_data['gilt']['SID_lys'], label='Gilt')
        if self.tracked_pig_data['barrow']['SID_lys']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['barrow']['SID_lys'])], 
                    self.tracked_pig_data['barrow']['SID_lys'], label='Barrow')
        if self.tracked_pig_data['male']['SID_lys']:
            ax3.plot(self.days_data[:len(self.tracked_pig_data['male']['SID_lys'])], 
                    self.tracked_pig_data['male']['SID_lys'], label='Male')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('SID Lysine (g/day)')
        ax3.set_title('Standardized Ileal Digestible Lysine Requirements')
        ax3.legend()
        ax3.grid(True)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()'''


def run_simulation_gui():
    """
    Create a GUI to run the pig growth simulation
    """
    # Create the main window
    root = tk.Tk()
    root.title("Pig Growth Simulation")
    root.geometry("1000x800")
    
    # Create a frame for controls
    control_frame = ttk.Frame(root, padding="10")
    control_frame.pack(fill=tk.X)
    
    # Create a notebook for different parameter tabs
    param_notebook = ttk.Notebook(root)
    param_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Create tabs for different parameter categories
    basic_tab = ttk.Frame(param_notebook)
    environ_tab = ttk.Frame(param_notebook)
    pig_tab = ttk.Frame(param_notebook)
    
    param_notebook.add(basic_tab, text="Basic Parameters")
    param_notebook.add(environ_tab, text="Environmental Parameters")
    param_notebook.add(pig_tab, text="Pig Parameters")
    
    # Add parameters to Basic tab
    ttk.Label(basic_tab, text="Initial Population:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    # Region 1-5 population inputs
    ttk.Label(basic_tab, text="Region 1:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    pig_R1 = tk.IntVar(value=5)
    ttk.Spinbox(basic_tab, from_=0, to=20, textvariable=pig_R1, width=5).grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Region 2:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
    pig_R2 = tk.IntVar(value=5)
    ttk.Spinbox(basic_tab, from_=0, to=20, textvariable=pig_R2, width=5).grid(row=1, column=3, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Region 3:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    pig_R3 = tk.IntVar(value=5)
    ttk.Spinbox(basic_tab, from_=0, to=20, textvariable=pig_R3, width=5).grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Region 4:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
    pig_R4 = tk.IntVar(value=5)
    ttk.Spinbox(basic_tab, from_=0, to=20, textvariable=pig_R4, width=5).grid(row=2, column=3, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Region 5:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    pig_R5 = tk.IntVar(value=5)
    ttk.Spinbox(basic_tab, from_=0, to=20, textvariable=pig_R5, width=5).grid(row=3, column=1, padx=5, pady=5)
    
    ttk.Separator(basic_tab, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=4, sticky=tk.EW, pady=10)
    
    # Other basic parameters
    ttk.Label(basic_tab, text="Initial Weight (kg):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
    init_weight = tk.DoubleVar(value=20)
    ttk.Spinbox(basic_tab, from_=10, to=30, textvariable=init_weight, width=5, increment=0.5).grid(row=5, column=1, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Sell Weight (kg):").grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
    sell_weight = tk.DoubleVar(value=130)
    ttk.Spinbox(basic_tab, from_=100, to=150, textvariable=sell_weight, width=5, increment=0.5).grid(row=5, column=3, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="RAC Start Weight (kg):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
    init_weight_rac = tk.DoubleVar(value=78)
    ttk.Spinbox(basic_tab, from_=50, to=100, textvariable=init_weight_rac, width=5, increment=0.5).grid(row=6, column=1, padx=5, pady=5)
    
    ttk.Label(basic_tab, text="Selling Rate (%):").grid(row=6, column=2, sticky=tk.W, padx=5, pady=5)
    selling_rate = tk.IntVar(value=100)
    ttk.Spinbox(basic_tab, from_=0, to=100, textvariable=selling_rate, width=5).grid(row=6, column=3, padx=5, pady=5)
    
    # Add parameters to Environmental tab
    ttk.Label(environ_tab, text="Environmental Controls:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    ttk.Label(environ_tab, text="Temperature (°C):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    T = tk.DoubleVar(value=20)
    ttk.Spinbox(environ_tab, from_=0, to=40, textvariable=T, width=5, increment=0.5).grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(environ_tab, text="ME Content (kcal/kg):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
    ME_content = tk.DoubleVar(value=3300)
    ttk.Spinbox(environ_tab, from_=2500, to=4000, textvariable=ME_content, width=5, increment=50).grid(row=1, column=3, padx=5, pady=5)
    
    ttk.Label(environ_tab, text="Dry Matter Content:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    Dry_matter = tk.DoubleVar(value=0.88)
    ttk.Spinbox(environ_tab, from_=0.80, to=1.0, textvariable=Dry_matter, width=5, increment=0.01).grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(environ_tab, text="Fermentable Fiber Content:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
    ferm_fiber_content = tk.DoubleVar(value=0.15)
    ttk.Spinbox(environ_tab, from_=0, to=0.5, textvariable=ferm_fiber_content, width=5, increment=0.01).grid(row=2, column=3, padx=5, pady=5)
    
    # Checkboxes
    environmental_temperature = tk.BooleanVar(value=True)
    ttk.Checkbutton(environ_tab, text="Consider Environmental Temperature", variable=environmental_temperature).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    stochastic_weight_gain = tk.BooleanVar(value=True)
    ttk.Checkbutton(environ_tab, text="Stochastic Weight Gain", variable=stochastic_weight_gain).grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Add parameters to Pig tab
    ttk.Label(pig_tab, text="Pig Specific Parameters:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    ttk.Label(pig_tab, text="ME Requirements for Activity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ME_requirements_for_increased_activity = tk.DoubleVar(value=0)
    ttk.Spinbox(pig_tab, from_=0, to=1000, textvariable=ME_requirements_for_increased_activity, width=5, increment=10).grid(row=1, column=1, padx=5, pady=5)
    
    # RAC parameters
    RAC = tk.BooleanVar(value=False)
    ttk.Checkbutton(pig_tab, text="Use Ractopamine (RAC)", variable=RAC).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    
    ttk.Label(pig_tab, text="RAC Level (ppm):").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    RAC_level = tk.DoubleVar(value=5)
    ttk.Spinbox(pig_tab, from_=0, to=20, textvariable=RAC_level, width=5, increment=1).grid(row=2, column=2, padx=5, pady=5)
    
    # Create a frame for the plots
    plot_frame = ttk.Frame(root)
    plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create a canvas for displaying plots
    fig = Figure(figsize=(10, 8))
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    # Status indicator
    status_var = tk.StringVar(value="Ready to run simulation")
    status_label = ttk.Label(root, textvariable=status_var, font=('Arial', 10, 'italic'))
    status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    # Create simulation instance
    simulation = PigGrowthSimulation()
    
    # Function to run the simulation
    def run_simulation():
        # Update status
        status_var.set("Setting up simulation...")
        root.update()
        
        # Set up the simulation with parameters from the GUI
        simulation.init_weight = init_weight.get()
        simulation.sell_weight = sell_weight.get()
        simulation.init_weight_rac = init_weight_rac.get()
        
        simulation.setup(
            pig_R1.get(),
            pig_R2.get(),
            pig_R3.get(),
            pig_R4.get(),
            pig_R5.get()
        )
        
        status_var.set("Running simulation...")
        root.update()
        
        # Run simulation for 140 days or until it stops
        for _ in range(140):
            # Update the canvas to show progress
            if _ % 10 == 0:
                status_var.set(f"Running simulation... Day {_}")
                root.update()
            
            # Run one day of the simulation
            continue_sim = simulation.go(
                environmental_temperature.get(),
                T.get(),
                ME_content.get(),
                stochastic_weight_gain.get(),
                ME_requirements_for_increased_activity.get(),
                RAC.get(),
                RAC_level.get(),
                Dry_matter.get(),
                ferm_fiber_content.get(),
                selling_rate.get()
            )
            
            if not continue_sim:
                break
        
        status_var.set(f"Simulation completed. Days simulated: {simulation.days}")
        
        # Create plots after the simulation
        update_plots()
    
    # Function to update the plots
    def update_plots():
        # Clear previous plots
        fig.clear()
        
        # Create a 2x2 grid of subplots
        axs = fig.subplots(2, 2)
        
        # External Parameters plot (top left)
        axs[0, 0].plot(simulation.days_data, simulation.pig_count_data, label='Pigs')
        axs[0, 0].plot(simulation.days_data, simulation.sold_count_data, label='Sold Pigs')
        axs[0, 0].plot(simulation.days_data, simulation.total_feed_intake_data, label='Daily Feed Intake (kg)')
        axs[0, 0].set_xlabel('Days')
        axs[0, 0].set_ylabel('Count / kg')
        axs[0, 0].set_title('External Parameters')
        axs[0, 0].legend()
        axs[0, 0].grid(True)
        
        # Weight plot (top right)
        for breed, color in [('gilt', 'pink'), ('barrow', 'orange'), ('male', 'green')]:
            if simulation.tracked_pig_data[breed]['weight']:
                days = simulation.days_data[:len(simulation.tracked_pig_data[breed]['weight'])]
                axs[0, 1].plot(days, simulation.tracked_pig_data[breed]['weight'], label=breed.capitalize(), color=color)
        axs[0, 1].set_xlabel('Days')
        axs[0, 1].set_ylabel('Weight (kg)')
        axs[0, 1].set_title('Weight')
        axs[0, 1].legend()
        axs[0, 1].grid(True)
        
        # Protein Deposition plot (bottom left)
        for breed, color in [('gilt', 'pink'), ('barrow', 'orange'), ('male', 'green')]:
            if simulation.tracked_pig_data[breed]['Prd']:
                days = simulation.days_data[:len(simulation.tracked_pig_data[breed]['Prd'])]
                axs[1, 0].plot(days, simulation.tracked_pig_data[breed]['Prd'], label=breed.capitalize(), color=color)
        axs[1, 0].set_xlabel('Days')
        axs[1, 0].set_ylabel('Pd (g/day)')
        axs[1, 0].set_title('Protein Deposition')
        axs[1, 0].legend()
        axs[1, 0].grid(True)
        
        # Lipid Deposition plot (bottom right)
        for breed, color in [('gilt', 'pink'), ('barrow', 'orange'), ('male', 'green')]:
            if simulation.tracked_pig_data[breed]['Lid']:
                days = simulation.days_data[:len(simulation.tracked_pig_data[breed]['Lid'])]
                axs[1, 1].plot(days, simulation.tracked_pig_data[breed]['Lid'], label=breed.capitalize(), color=color)
        axs[1, 1].set_xlabel('Days')
        axs[1, 1].set_ylabel('Ld (g/day)')
        axs[1, 1].set_title('Lipid Deposition')
        axs[1, 1].legend()
        axs[1, 1].grid(True)
        
        # Adjust layout and update canvas
        fig.tight_layout()
        canvas.draw()
    
    # Create buttons for controlling the simulation
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(pady=10)
    
    setup_button = ttk.Button(button_frame, text="Setup Simulation", command=lambda: simulation.setup(
        pig_R1.get(),
        pig_R2.get(),
        pig_R3.get(),
        pig_R4.get(),
        pig_R5.get()
    ))
    setup_button.grid(row=0, column=0, padx=5)
    
    run_button = ttk.Button(button_frame, text="Run Full Simulation", command=run_simulation)
    run_button.grid(row=0, column=1, padx=5)
    
    plot_button = ttk.Button(button_frame, text="Show Detailed Plots", command=simulation.create_plots)
    plot_button.grid(row=0, column=2, padx=5)
    
    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    run_simulation_gui()