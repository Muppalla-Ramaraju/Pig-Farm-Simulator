import matplotlib.pyplot as plt
import pandas as pd
from model import PigModel

def plot_tracked_data(file="tracked_agents_data.csv"):
    """Plot the tracked data for specified agents."""
    df = pd.read_csv(file)
    variables = [
        "Weight", "Weight Gain", "Pd", "Ld",
        "ME Intake", "Feed Intake", "SID Lys",
        "Maintenance ME", "PBT"
    ]

    for var in variables:
        plt.figure(figsize=(10, 6))
        for gender in df["Gender"].unique():
            agent_data = df[df["Gender"] == gender]
            plt.plot(agent_data["Day"], agent_data[var], label=f"{gender.capitalize()}")
        plt.title(f"{var} Over Time")
        plt.xlabel("Day")
        plt.ylabel(var)
        plt.legend()
        plt.grid()
        plt.savefig(f"{var}_plot.png")
        plt.show()

if __name__ == "__main__":
    ME_content = 3600  # Define ME content

    # Create and run the model
    model = PigModel(num_gilts=12, num_barrows=10, num_males=10, init_weight=20, sell_weight=130, ME_content=ME_content)
    for i in range(130):  # Simulate for 100 days
        model.step()

    # Save and plot tracked data
    model.save_tracked_data()
    plot_tracked_data("tracked_agents_data.csv")


    #Addign a line to demo the github

    #time setting step func
    #keep focusing from bw and bw_gain perspective