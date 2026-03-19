# src/core/visualisation.py

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation


def close_on_enter(event):
    if event.key == 'enter':
        plt.close()


def show_until_enter():
    """Connects the enter key to the close function and displays."""
    fig = plt.gcf() # Get current figure
    fig.canvas.mpl_connect('key_press_event', close_on_enter)
    print("Press Enter (in the plot) to continue to the next visualisation.")
    plt.show()


def plot_setup_dashboard(alpha, temp_rate_mat, u0):
    """Visualisiert die Eingangsmatrizen: Materialien, Wärmeuellen, Starttemperatur."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Simulations-Setup Übersicht", fontsize=16)

    # 1. Material (Alpha)
    im0 = axes[0].imshow(alpha, cmap='viridis', origin='lower')
    axes[0].set_title("Materialverteilung/Diffusivität (Alpha)")
    fig.colorbar(im0, ax=axes[0], label='Diffusivität (m²/s)')

    # 2. Heat source (temp_rate_mat)
    im1 = axes[1].imshow(temp_rate_mat, cmap='magma', origin='lower')
    axes[1].set_title("Perm. Wärmeuellen (temp_rate_mat)")
    fig.colorbar(im1, ax=axes[1], label='Temperatur (°C)')

    # 3. initial heat map (u0)
    im2 = axes[2].imshow(u0, cmap='hot', origin='lower')
    axes[2].set_title("Initiales Temperaturfeld (u0)")
    fig.colorbar(im2, ax=axes[2], label='Temperatur (°C)')

    plt.tight_layout()


def initial_state(final_tensor, vmin, vmax, alpha=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[0, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title("Startzustand der Simulation")
    plt.colorbar(im, label='Temperatur (°C)')
    
    # Overlay to show different materials
    if alpha is not None:
        ax.contour(alpha, levels=3, colors='cyan', linewidths=0.8, alpha=0.6)


def final_state(final_tensor, vmin, vmax, alpha=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[-1, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title(f"Endzustand (Frame {len(final_tensor)-1})")
    plt.colorbar(im, label='Temperatur (°C)')
    
    # Overlay to show different materials
    if alpha is not None:
        ax.contour(alpha, levels=3, colors='cyan', linewidths=0.8, alpha=0.6)


def interactive_heat_map(sol_tensor, vmin, vmax, alpha=None):
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    fig.colorbar(im, label='Temperatur (°C)')
    
    if alpha is not None:
        ax.contour(alpha, levels=3, colors='cyan', linewidths=0.8, alpha=0.6)

    ax_time = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(ax_time, 'Step', 0, len(sol_tensor)-1, valinit=0, valfmt='%d')

    def update(val):
        t_idx = int(slider.val)
        im.set_data(sol_tensor[t_idx, :, :])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


def animate_heat(sol_tensor, vmin, vmax, alpha=None):
    fig, ax = plt.subplots()
    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    ax.set_title("Animation Wärmefluss")
    plt.colorbar(im, label='Temperatur (°C)')

    # Overlay to show different materials
    if alpha is not None:
        ax.contour(alpha, levels=3, colors='cyan', linewidths=0.8, alpha=0.6)

    # frame count
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=12, fontweight='bold')

    def update(frame):
        im.set_data(sol_tensor[frame, :, :])
        time_text.set_text(f'Frame: {frame}')
        return [im, time_text]

    # The 'ani' reference must be returned; otherwise, the garbage collector will delete the animation
    ani = FuncAnimation(fig, update, frames=len(sol_tensor), interval=50, blit=False)   # blit=False keeps the alpha contour for every frame
    return ani