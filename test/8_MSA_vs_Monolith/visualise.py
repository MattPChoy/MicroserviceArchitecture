import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the seaborn pastel palette
sns.set_palette("pastel")

# Data
microservice = {
    1: 80.0278,
    2: 160.3444,
    4: 295.1639,
    8: 560.6583,
    16: 949.4111,
    24: 1072.8944,
    32: 1139.1652,
    40: 1149.2000,
    48: 1134.2917,
    56: 1056.1222,
    64: 1017.7778,
}
monolith = 170

# Extract x (replicas) and y (throughput) values from the microservice dictionary
x_microservice = list(microservice.keys())
y_microservice = list(microservice.values())

# Set the style to "darkgrid" with gray grid lines
sns.set_style("darkgrid", {'axes.grid.color': 'gray'})

# Plot a yellow shaded region for the monolith throughput (in bolder yellow)
plt.fill_between([0, max(x_microservice)], 0, monolith, color='gold', alpha=0.5, label='Monolith')

# Create a scatter plot for microservice data (in bolder blue)
plt.scatter(x_microservice, y_microservice, color='steelblue', label='Microservice')

# Label the axes
plt.xlabel('Number of Instances')
plt.ylabel('Throughput (req/s)')

# Add a legend
plt.legend()

# Show the plot
plt.title('Microservice Instances vs. Throughput')

plt.show()
