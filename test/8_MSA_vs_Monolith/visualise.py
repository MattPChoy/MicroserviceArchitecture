import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the seaborn pastel palette
sns.set_palette("pastel")

# Data
microservice = {
    1: 88.4777777,
    2: 181.122222,
    4: 317.888888,
    8: 510.644444,
    16: 745.07777,
    32: 1047.522222,
    64: 1030.5777777
}
monolith = 170

# Extract x (replicas) and y (throughput) values from the microservice dictionary
x_microservice = list(microservice.keys())
y_microservice = list(microservice.values())

# Set the style to "darkgrid" with gray grid lines
sns.set_style("darkgrid", {'axes.grid.color': 'gray'})

# Plot a yellow shaded region for the monolith throughput (in bolder yellow)
plt.fill_between([min(x_microservice), max(x_microservice)], 0, monolith, color='gold', alpha=0.5, label='Monolith')

# Create a scatter plot for microservice data (in bolder blue)
plt.scatter(x_microservice, y_microservice, color='steelblue', label='Microservice')

# Label the axes
plt.xlabel('Replicas')
plt.ylabel('Throughput')

# Add a legend
plt.legend()

# Show the plot
plt.title('Microservice Replicas vs. Throughput')

plt.show()
