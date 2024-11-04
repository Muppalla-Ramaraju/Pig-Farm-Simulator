# main.py

from model import PigModel
from mesa.space import MultiGrid  # Import MultiGrid for the grid environment

if __name__ == "__main__":
    # Create the model
    model = PigModel(num_gilts=10, num_barrows=10, num_males=10, init_weight=20, sell_weight=130)
    
    # Run for 100 steps
    for i in range(100):
        model.step()

    # Collect the data
    data = model.datacollector.get_agent_vars_dataframe()
    print(data)




    