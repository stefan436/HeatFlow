# src/visualisation.py

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation

from .config_system import *


def close_on_enter(event):
    if event.key == 'enter':
        plt.close()

def show_until_enter():
    """Connects the enter key to the close function and displays."""
    fig = plt.gcf() # Get current figure
    fig.canvas.mpl_connect('key_press_event', close_on_enter)
    print("Press Enter (in the plot) to continue to the next visualisation.")
    plt.show()

def initial_state(final_tensor):
    final_matrix = final_tensor[0, :, :]
    plt.imshow(final_matrix, cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    plt.colorbar(label='Temperature (°C)')

def final_state(final_tensor):
    final_matrix = final_tensor[-1, :, :]
    plt.imshow(final_matrix, cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    plt.colorbar(label='Temperature (°C)')

def interactive_heat_map(sol_tensor):
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25) # Make room for the slider

    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    fig.colorbar(im)

    ax_time = plt.axes([0.2, 0.1, 0.65, 0.03])          # Add the slider
    slider = Slider(ax_time, 'Step', 0, len(sol_tensor)-1, valinit=0, valfmt='%d')

    # Update function called when slider moves
    def update(val):
        t_idx = int(slider.val)
        im.set_data(sol_tensor[t_idx, :, :])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


def animate_heat(sol_tensor):
    fig, ax = plt.subplots()
    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=0, vmax=100)
    
    def update(frame):
        im.set_data(sol_tensor[frame, :, :])
        ax.set_title(f"Step: {frame}")
        return [im]

    ani = FuncAnimation(fig, update, frames=len(sol_tensor), interval=50, blit=True)
    plt.show()