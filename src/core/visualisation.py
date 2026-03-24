# src/core/visualisation.py

import textwrap

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches


def close_on_enter(event):
    if event.key == 'enter':
        plt.close()


def show_until_enter():
    """Connects the enter key to the close function and displays."""
    fig = plt.gcf()
    fig.canvas.mpl_connect('key_press_event', close_on_enter)
    print("Drücke Enter (im Fenster), um zur nächsten Visualisierung zu gelangen.")
    plt.show()


def plot_setup_dashboard(lambda_mat, q_mat, u0, rho_mat, heat_cap_mat, substrate=None, components=None):
    """Visualisiert die Eingangsmatrizen: Materialien, Wärmequellen, Starttemperatur."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
    fig.suptitle("Simulations-Setup Übersicht", fontsize=16, fontweight='bold')

    unique_lambda_mats = np.unique(lambda_mat)

    # 1. Plot: Wärmeleitfähigkeit
    im0 = axes[0].imshow(lambda_mat, cmap='viridis', origin='lower')
    axes[0].set_title("Spezifische\nWärmeleitfähigkeit")
    axes[0].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im0, ax=axes[0], label='Wärmeleitfähigkeit in W/(m·K)', shrink=0.8, pad=0.05)

    marker_style = {
        'color': 'white',
        'fontsize': 10,
        'fontweight': 'bold',
        'ha': 'center',
        'va': 'center',
        'path_effects': [pe.withStroke(linewidth=2, foreground='black')]
    }

    legend_handles = []
    material_to_idx = {} 
    current_idx = 1

    # MAX_WIDTH definiert, ab wie vielen Zeichen eine neue Zeile begonnen wird
    MAX_WIDTH = 25

    # Substrat umbrechen und als reiner Legenden-Eintrag hinzufügen
    if substrate:
        wrapped_substrate = textwrap.fill(substrate, width=MAX_WIDTH)
        legend_handles.append(mpatches.Patch(color='none', label=f"Substrat: {wrapped_substrate}"))

    # Bauteile materialbasiert nummerieren und umbrechen
    if components:
        for comp in components:
            if hasattr(comp, 'material') and comp.material:
                mat_name = comp.material
                
                # Wenn Material neu ist, weise neuen Index zu und erweitere Legende
                if mat_name not in material_to_idx:
                    material_to_idx[mat_name] = str(current_idx)
                    wrapped_name = textwrap.fill(mat_name, width=MAX_WIDTH)
                    legend_handles.append(mpatches.Patch(color='none', label=f"[{current_idx}] {wrapped_name}"))
                    current_idx += 1
                
                # Hole den korrekten Index für dieses Material
                idx = material_to_idx[mat_name]
                axes[0].text(comp.x_center, comp.y_center, idx, **marker_style)

    # Legende dynamisch formatieren
    if legend_handles:
        # Ab 6 Einträgen machen wir 2 Spalten, ab 12 Einträgen 3 Spalten
        num_cols = 1 if len(legend_handles) <= 5 else (2 if len(legend_handles) <= 12 else 3)
        
        fig.legend(handles=legend_handles, 
                   loc='outside lower center', 
                   fancybox=True, shadow=False, ncol=num_cols, framealpha=0.9,
                   handlelength=0, handletextpad=0, fontsize=9)

    heating_rate_mat = np.zeros_like(q_mat)
    mask = (rho_mat > 0) & (heat_cap_mat > 0)
    heating_rate_mat[mask] = q_mat[mask] / (rho_mat[mask] * heat_cap_mat[mask])

    # 2. Plot: Initiale Aufheizrate
    im1 = axes[1].imshow(heating_rate_mat, cmap='magma', origin='lower')
    axes[1].set_title("Theoretische \nAufheizrate (adiabatisch)")
    axes[1].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im1, ax=axes[1], label='Temperaturänderung in °C/s', shrink=0.8, pad=0.05)

    # 3. Plot: Initiales Temperaturfeld
    im2 = axes[2].imshow(u0, cmap='hot', origin='lower')
    axes[2].set_title("Startbedingungen\n(t = 0 s)")
    axes[2].contour(lambda_mat, levels=unique_lambda_mats, colors='cyan', linewidths=0.8, alpha=0.6)
    fig.colorbar(im2, ax=axes[2], label='Temperatur in °C', shrink=0.8, pad=0.05)

    return fig

def initial_state(final_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[0, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title("Temperaturfeld bei t = 0,0 s")
    plt.colorbar(im, label='Temperatur in °C')
    
    # Overlay to show different materials
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)
    return fig


def final_state(time_steps, final_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(final_tensor[-1, :, :], cmap="hot", vmin=vmin, vmax=vmax, origin="lower")
    ax.set_title(f"Temperaturfeld nach t = {time_steps[-1]:.1f} s")
    plt.colorbar(im, label='Temperatur in °C')
    
    # Overlay to show different materials
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)
    return fig


def interactive_heat_map(time_steps, sol_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    fig.colorbar(im, label='Temperatur in °C')
    
    ax.set_title("Dynamische\nTemperaturverteilung")
        
    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)

    ax_time = plt.axes([0.2, 0.1, 0.65, 0.03])
    
    slider = Slider(ax_time, "Zeit", 0, len(sol_tensor)-1, valinit=0, valfmt='%d')
    slider.valtext.set_text(f"{time_steps[0]:.1f} s")

    def update(val):
        t_idx = int(slider.val)
        im.set_data(sol_tensor[t_idx, :, :])
        slider.valtext.set_text(f"{time_steps[t_idx]:.1f} s")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    return fig, slider


def animate_heat(time_steps, sol_tensor, vmin, vmax, lambda_mat=None):
    fig, ax = plt.subplots()
    im = ax.imshow(sol_tensor[0, :, :], cmap='hot', origin='lower', vmin=vmin, vmax=vmax)
    ax.set_title("Animation Wärmefluss")
    plt.colorbar(im, label='Temperatur in °C')

    if lambda_mat is not None:
        ax.contour(lambda_mat, levels=np.unique(lambda_mat), colors='cyan', linewidths=0.8, alpha=0.6)

    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=12, fontweight='bold')

    def update(frame):
        im.set_data(sol_tensor[frame, :, :])
        time_text.set_text(f'Zeit: {time_steps[frame]:.1f} s')
        return [im, time_text]

    ani = FuncAnimation(fig, update, frames=len(sol_tensor), interval=50, blit=False)
    return fig, ani