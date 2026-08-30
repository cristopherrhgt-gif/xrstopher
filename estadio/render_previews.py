#!/usr/bin/env python3
"""Renderiza vistas previas PNG de las piezas del estadio y del estadio completo."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PIECES = os.path.join(HERE, "estadio-piezas")

COLORS = {
    "verde-cancha": "#43A047",
    "verde-franjas-oscuras": "#388E3C",
    "gris-gradas": "#90A4AE",
    "blanco-lineas": "#F5F5F5",
    "columnas-pizarra": "#546E7A",
    "techos-plateado": "#CFD8DC",
    "rojo-asientos": "#E53935",
    "azul-asientos": "#1E88E5",
    "oscuro": "#424242",
    "amarillo-luces": "#FBC02D",
}


def render(mesh, path, color, title, elev=25, azim=-60):
    fig = plt.figure(figsize=(6.5, 6.5), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("white")
    v, f = mesh.vertices, mesh.faces
    poly = Poly3DCollection(v[f], facecolors=color, edgecolors="#333333",
                            linewidths=0.25, alpha=0.97)
    ax.add_collection3d(poly)
    ax.auto_scale_xyz(v[:, 0], v[:, 1], v[:, 2])
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=12, pad=2)
    fig.tight_layout()
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)
    print("render ->", os.path.relpath(path, HERE))


def main():
    # piezas
    for name, hexc in COLORS.items():
        stl = os.path.join(PIECES, name + ".stl")
        if not os.path.exists(stl):
            continue
        m = trimesh.load(stl)
        render(m, os.path.join(PIECES, name + ".png"), hexc, name)
    # estadio completo
    full = trimesh.load(os.path.join(HERE, "estadio-tinkercad.stl"))
    render(full, os.path.join(HERE, "estadio-full.png"), "#9FB3C8",
           "Estadio completo", elev=22, azim=-55)
    render(full, os.path.join(HERE, "estadio-full-top.png"), "#9FB3C8",
           "Estadio (vista superior)", elev=89, azim=-90)


if __name__ == "__main__":
    main()
