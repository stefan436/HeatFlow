# src/core/visualisation.py

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
import numpy as np


def close_on_enter(event):
    if event.key == 'enter':
        plt.close()


def show_until_enter():
    """Connects the enter key to the close function and displays."""
    fig = plt.gcf()
    fig.canvas.mpl_connect('key_press_event', close_on_enter)
    print("Drücke Enter (im Fenster), um zur nächsten Visualisierung zu gelangen.")
    plt.show()


def plot_setup_dashboard(lambda_mat, q_mat, u0):
    """Visualisiert die Eingangsmatrizen: Materialien, Wärmequellen, Starttemperatur."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    fig.suptitle("Simulations-Setup Übersicht", fontsize=16, fontweight='bold')

    unique_lambda_mats = np.unique(lambda_mat)

    # 1. Plot: Wärmeleitfähigkeit
    im0 = axes[0].imshow(lambda_mat, cmap='viridis', origin='lower')
    axes[0].set_title("Wärmeleitfähigkeit (lambda_mat)")
    axes[0].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im0, ax=axes[0], label='Wärmeleitfähigkeit (W/(m·K))', shrink=0.8, pad=0.05)

    # 2. Plot: Volumetrische Wärmeleistung
    im1 = axes[1].imshow(q_mat, cmap='magma', origin='lower')
    axes[1].set_title("Perm. Wärmequellen (q_mat)")
    axes[1].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im1, ax=axes[1], label='Volumetrische Leistung (W/m³)', shrink=0.8, pad=0.05)

    # 3. Plot: Initiales Temperaturfeld
    im2 = axes[2].imshow(u0, cmap='hot', origin='lower')
    axes[2].set_title("Initiales Temperaturfeld (u0)")
    axes[2].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im2, ax=axes[2], label='Temperatur (°C)', shrink=0.8, pad=0.05)

    return fig
    

def initial_state(final_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[0, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title("Startzustand der Simulation")
    plt.colorbar(im, label='Temperatur (°C)')
    
    # Overlay to show different materials
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)
    return fig


def final_state(final_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[-1, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title(f"Endzustand (Integrationsschritt {len(final_tensor)-1})")
    plt.colorbar(im, label='Temperatur (°C)')
    
    # Overlay to show different materials
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)
    return fig


def interactive_heat_map(time_steps, sol_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    fig.colorbar(im, label='Temperatur (°C)')
    
    # NEU: Initiale Zeit als Titel setzen
    ax.set_title(f"Zeit: {time_steps[0]:.1f} s")
        
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)

    ax_time = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(ax_time, 'Integrationsschritt', 0, len(sol_tensor)-1, valinit=0, valfmt='%d')

    def update(val):
        t_idx = int(slider.val)
        im.set_data(sol_tensor[t_idx, :, :])
        ax.set_title(f"Zeit: {time_steps[t_idx]:.1f} s")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    return fig, slider


def animate_heat(time_steps, sol_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    ax.set_title("Animation Wärmefluss")
    plt.colorbar(im, label='Temperatur (°C)')

    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)

    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=12, fontweight='bold')

    def update(frame):
        im.set_data(sol_tensor[frame, :, :])
        time_text.set_text(f'Zeit: {time_steps[frame]:.1f} s')
        return [im, time_text]

    ani = FuncAnimation(fig, update, frames=len(sol_tensor), interval=50, blit=False)
    return fig, ani