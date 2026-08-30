#!/usr/bin/env python3
"""Renderiza una vista previa 3D de un STL (para ver el modelo sin Tinkercad)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh

def render(path, out, title=None, elev=25, azim=-60):
    m = mesh.Mesh.from_file(path)
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    poly = Poly3DCollection(m.vectors, facecolors="#4da3ff", edgecolors="#1a5cbf",
                            linewidths=0.3, alpha=0.95)
    ax.add_collection3d(poly)
    pts = m.vectors.reshape(-1, 3)
    ax.auto_scale_xyz(pts[:, 0], pts[:, 1], pts[:, 2])
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=14)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print(f"render -> {out}")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], title=sys.argv[3] if len(sys.argv) > 3 else None)
