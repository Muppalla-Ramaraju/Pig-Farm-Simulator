# Pig-Farm-Simulator
This Project is to run a growth simulation for pigs, end users will be swine farmers who raise and breed pigs for food production. 

This simulation focuses on modeling the growth of gilts, barrows, and male pigs, taking into account weight gain, 
nutrient intake, body composition, and other growth factors. 
The model also aims to optimize feeding strategies based on guidelines from the Nutrient Requirement of Swine (NRC).

End Goal of the project is to build a full stack web application with interactive visualizations
for farmers to predict the optimal feeding strategies, buy and sell weights.
Daily feeding mechanism calculates the food intake, metabloizable energy, vitamins, protein and mineral deposition, and weight gain etc.,

**Project Structure**

/Pig-Farm-Simulator
  ├── agent.py      # Defines the PigAgent class
  
  ├── model.py      # Defines the PigModel class
  
  ├── main.py       # For running the simulations with desired params

**PigAgent Class: agent.py**

This file defines the PigAgent class, representing individual pig agents within the simulation. Each pig agent has various attributes, such as:

	•	Weight and Body Composition: Including whole-body protein mass (BPm), lipid mass (BLm), and ash content.
	•	Feed Intake and Energy Requirements: ME_intake, maintenance_ME_requirements, and other metrics for nutrient and energy management.
	•	Growth Metrics: Factors like Prd (protein deposition rate), Pd_max, weight_gain, and more to monitor and simulate growth changes over time.
	•	Environmental Interactions: Includes parameters for the region, minimum space requirements, and other environmental considerations.

The agent’s step() method (to be fully implemented) will update these attributes based on growth and feeding calculations.

**PigModel Class: model.py**

This file defines the PigModel class, which initializes the simulation environment, sets global variables, and manages the creation and tracking of pig agents:

	•	Global Variables: For settings like init_weight, sell_weight, total_feed_intake, and region_boundaries.
	•	Agent Setup: Creates gilts, barrows, and male pigs, assigns them to regions on a grid, and initializes each with random initial weights.
	•	Scheduling and Regions: Divides the grid into regions, assigning pigs to specific areas as per the simulation requirements.

The step() method advances the model by one day (or step), where each pig’s growth and nutrient attributes are updated based on predefined equations and environmental factors.

**Invoke the simulation: main.py**

This script serves as the entry point for running the simulation. Here, you can specify the number of gilts, barrows, and males, along with other parameters like initial weight and target sell weight. It initializes the PigModel and runs the simulation for a specified number of steps (days), tracking the evolution of the pig agents’ attributes over time.

#Future Enhancements

The simulation will be further enhanced to incorporate:

	•	Detailed nutrient intake calculations for amino acids, minerals, and vitamins.
	•	Dynamic visualization of pig growth metrics and nutrient intake.
	•	Front-end support for user input and real-time data visualization, potentially using Streamlit or Mesa’s built-in server.

