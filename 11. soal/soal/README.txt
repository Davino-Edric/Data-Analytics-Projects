mport pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the CSV file
df = pd.read_csv("cluster.csv")

replace = {0: 1, 1: 2, 2: 3, 3: 4, 4:5, 5:6}  # Replace these with the desired new values

# Use the replace method to replace values based on the mapping
df["Clusters"].replace(replace, inplace=True)

data = df[['Age', 'Income', 'SpendingScore']]


# Map target Labels to their corresponding names
target_labels = {1: 'Muda, Menengah, Seadanya', 2: 'Tua, Menengah, Seadanya', 3:'Muda, Kaya, Boros', 4:'Tua Kaya, Irit', 
                 5:'Muda, Miskin, Boros', 6:'Tua, Miskin, Irit'}
# Select independent and dependent variables
target = df["Clusters"]

df["Clusters"].unique()

data.head()

# Create a function to update the 3D scatter plot
def update_plot():
    x_axis = x_axis_combobox.get()
    y_axis = y_axis_combobox.get()
    z_axis = z_axis_combobox.get()
    selected_targets = [i + 1 for i, var in enumerate(button_vars) if var.get()]  # Get selected targets

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Set the color map based on the selected target classes
    colors = {1: 'r', 2: 'b', 3: 'g', 4: 'y', 5: 'c', 6:'m'}

    for target_class in selected_targets:
        label = target_labels.get(target_class, f'Target {target_class}')
        indices = (target == target_class)
        ax.scatter(data[x_axis][indices], data[y_axis][indices], data[z_axis][indices], c=colors[target_class],
                   label=label)

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_zlabel(z_axis)

    # Add a Legend
    ax.legend()
    plt.title(f"3D Scatter Plot ({x_axis}, {y_axis}, {z_axis})")

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0)
    canvas.draw()

# Create the main window
root = tk.Tk()
root.title("3D Scatter Plot GUI")

# Create Labels and comboboxes for axis selection
x_label = ttk.Label(root, text="X-Axis: ")
x_label.grid(row=0, column=0)
x_axis_combobox = ttk.Combobox(root, values=data.columns.tolist())
x_axis_combobox.grid(row=0, column=1)

y_label = ttk.Label(root, text="Y-Axis: ")
y_label.grid(row=1, column=0)
y_axis_combobox = ttk.Combobox(root, values=data.columns.tolist())
y_axis_combobox.grid(row=1, column=1)

z_label = ttk.Label(root, text="Z-Axis: ")
z_label.grid(row=2, column=0)
z_axis_combobox = ttk.Combobox(root, values=data.columns.tolist())
z_axis_combobox.grid(row=2, column=1)

# Create buttons for selecting target classes
button_vars = [tk.IntVar() for _ in range(6)]  # Adjust the range based on the number of target classes

target_buttons = [ttk.Checkbutton(root, text=target_labels[i+1], variable=button_vars[i]) for i in range(6)]

for i, button in enumerate(target_buttons):
    button.grid(row=4, column=i, padx=5)

# Create a frame to hold the embedded plot
plot_frame = ttk.Frame(root)
plot_frame.grid(row=5, column=0, columnspan=2)

# Create a button to update the plot
plot_button = ttk.Button(root, text="Plot", command=update_plot)
plot_button.grid(row=6, column=0, columnspan=2)

root.mainloop()
