#!/usr/bin/env python3
"""
Generate 900×600 article preview images for The Hertie Times.
Run from any directory; outputs JPGs to the same folder as this script.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patheffects as mpe
from matplotlib.collections import LineCollection
from scipy.ndimage import gaussian_filter
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = '#05111e'
NAVY  = '#1a3550'
TEAL  = '#1e7a8c'
AMBER = '#c9a84c'
CORAL = '#c87941'
RED   = '#c0392b'
PALE  = '#e8e4dc'
GREEN = '#27ae60'
BLUE  = '#2980b9'

# ── Core helpers ──────────────────────────────────────────────────────────────

def new(bg=BG):
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    return fig, ax

def save(fig, name):
    path = os.path.join(OUT, f'{name}.jpg')
    fig.savefig(path, dpi=100, bbox_inches='tight', pad_inches=0,
                facecolor=fig.get_facecolor(), format='jpeg',
                pil_kwargs={'quality': 88})
    plt.close(fig)
    print(f'  ✓  {name}.jpg')

def rng(seed=0):
    return np.random.RandomState(seed)

def smooth_noise(h, w, sigma, seed=0):
    r = rng(seed)
    return gaussian_filter(r.standard_normal((h, w)), sigma=sigma)

def glow_dots(ax, xs, ys, color, big=600, small=40, layers=5, alpha_base=0.07):
    for i in range(layers, 0, -1):
        ax.scatter(xs, ys, s=big * (i/layers)**1.8, c=color,
                   alpha=alpha_base, linewidths=0, zorder=5)
    ax.scatter(xs, ys, s=small, c=color, alpha=0.9, linewidths=0, zorder=6)

def glow_line(ax, xs, ys, color, lw=1.5, spread=6, alpha=0.85, zorder=5):
    ax.plot(xs, ys, color=color, lw=spread*3, alpha=0.06,
            solid_capstyle='round', zorder=zorder-1)
    ax.plot(xs, ys, color=color, lw=spread, alpha=0.18,
            solid_capstyle='round', zorder=zorder)
    ax.plot(xs, ys, color=color, lw=lw, alpha=alpha,
            solid_capstyle='round', zorder=zorder+1)

def bezier_arc(ax, x0, y0, x1, y1, sag, color, lw=1.2):
    mx, my = (x0+x1)/2, (y0+y1)/2 + sag
    t = np.linspace(0, 1, 300)
    bx = (1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1
    by = (1-t)**2*y0 + 2*(1-t)*t*my + t**2*y1
    glow_line(ax, bx, by, color, lw=lw)

def heat_field(ax, centers, color, spread=0.12, gamma=0.45, alpha=0.92):
    g = np.zeros((600, 900))
    for cx, cy, s in centers:
        px, py = int(cx*898), int(cy*598)
        g[py, px] = s
    g = gaussian_filter(g, sigma=spread*400)
    cmap = mc.LinearSegmentedColormap.from_list('h', [BG, color])
    ax.imshow(g, extent=[0,1,0,1], cmap=cmap, aspect='auto',
              origin='lower', zorder=2, alpha=alpha,
              norm=mc.PowerNorm(gamma=gamma, vmin=0))

def terrain(ax, seed=0, alpha=0.55, color=TEAL):
    r = rng(seed)
    x = np.linspace(0, 1, 300)
    y = np.linspace(0, 1, 200)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    for _ in range(8):
        cx, cy = r.uniform(0.1, 0.9), r.uniform(0.1, 0.9)
        Z += r.uniform(0.4, 1.2) * np.exp(-((X-cx)**2+(Y-cy)**2)/(2*0.15**2))
    Z = gaussian_filter(Z, sigma=12)
    ax.contour(X, Y, Z, levels=14, colors=[color], linewidths=0.5, alpha=alpha, zorder=2)

def grid_lines(ax, nx=22, ny=14, color=TEAL, alpha=0.12):
    for x in np.linspace(0, 1, nx):
        ax.axvline(x, color=color, alpha=alpha, lw=0.4, zorder=2)
    for y in np.linspace(0, 1, ny):
        ax.axhline(y, color=color, alpha=alpha, lw=0.4, zorder=2)

def ridge_plot(ax, n_ridges, seed, color=AMBER, bg_color=BG):
    r = rng(seed)
    x = np.linspace(0, 1, 500)
    for i in range(n_ridges):
        base_y = 0.08 + (i / n_ridges) * 0.75
        mu = r.uniform(0.3, 0.7)
        sig = r.uniform(0.06, 0.14)
        ht  = r.uniform(0.08, 0.20)
        y   = base_y + ht * np.exp(-0.5*((x-mu)/sig)**2)
        # Fill under ridge
        ax.fill_between(x, base_y, y, color=bg_color, zorder=10+i, alpha=1.0)
        alpha_c = 0.3 + 0.7*(i/n_ridges)
        ax.plot(x, y, color=color, lw=1.0, alpha=alpha_c, zorder=11+i)

def noise_layer(ax, seed, cmap_name, alpha=0.35, sigma=25):
    n = smooth_noise(600, 900, sigma, seed)
    ax.imshow(n, extent=[0,1,0,1], cmap=cmap_name, aspect='auto',
              origin='lower', alpha=alpha, zorder=1)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. elenadreyer-final  — SAR radar / Ukraine power grid
# ═══════════════════════════════════════════════════════════════════════════════
def make_elenadreyer_final():
    fig, ax = new()
    noise_layer(ax, 1, 'Greens', alpha=0.18, sigma=30)
    grid_lines(ax, nx=28, ny=18, color='#00cc44', alpha=0.18)
    r = rng(1)
    # Power-grid nodes (bright amber)
    nx_pts = 60
    xs = r.uniform(0.05, 0.95, nx_pts)
    ys = r.uniform(0.05, 0.95, nx_pts)
    glow_dots(ax, xs, ys, AMBER, big=300, small=18, layers=4, alpha_base=0.08)
    # A cluster of impacts
    ixs = r.uniform(0.25, 0.75, 12)
    iys = r.uniform(0.2, 0.8, 12)
    glow_dots(ax, ixs, iys, '#ff3300', big=800, small=30, layers=5, alpha_base=0.06)
    save(fig, 'elenadreyer-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. elenaiva-db2  — Ukraine power grid attack mapping
# ═══════════════════════════════════════════════════════════════════════════════
def make_elenaiva_db2():
    fig, ax = new()
    # Dense amber cluster attack centres
    centers = [(0.35,0.6,1.0),(0.55,0.55,0.8),(0.45,0.7,0.9),
               (0.6,0.4,0.7),(0.3,0.45,0.6),(0.7,0.65,0.5),(0.5,0.3,0.4)]
    heat_field(ax, centers, AMBER, spread=0.09, gamma=0.4)
    heat_field(ax, [(0.45,0.55,1.0)], '#ff4400', spread=0.14, gamma=0.5, alpha=0.5)
    grid_lines(ax, color='#1e3a5c', alpha=0.2)
    r = rng(2)
    glow_dots(ax, r.uniform(0.15,0.85,40), r.uniform(0.15,0.85,40),
              AMBER, big=200, small=12, layers=3, alpha_base=0.06)
    save(fig, 'elenaiva-db2')

# ═══════════════════════════════════════════════════════════════════════════════
# 3. luca-daniel-db1  — GPS interference halos
# ═══════════════════════════════════════════════════════════════════════════════
def make_luca_daniel_db1():
    fig, ax = new()
    noise_layer(ax, 3, 'Blues', alpha=0.15, sigma=40)
    # Interference rings
    interference = [(0.25, 0.65), (0.6, 0.4), (0.78, 0.7), (0.42, 0.3)]
    for (cx, cy) in interference:
        for r_ring in np.linspace(0.04, 0.22, 6):
            theta = np.linspace(0, 2*np.pi, 300)
            rx = cx + r_ring * np.cos(theta)
            ry = cy + r_ring * 0.6 * np.sin(theta)
            alpha = 0.35 * (1 - r_ring/0.25)
            ax.plot(rx, ry, color='#4fc3f7', lw=0.7, alpha=alpha, zorder=4)
    # Flight path arcs
    bezier_arc(ax, 0.05, 0.5, 0.95, 0.55, 0.15, AMBER, lw=1.0)
    bezier_arc(ax, 0.08, 0.35, 0.92, 0.7,  0.20, AMBER, lw=0.8)
    bezier_arc(ax, 0.1,  0.65, 0.9,  0.42, -0.05, AMBER, lw=0.7)
    glow_dots(ax, [cx for cx,_ in interference], [cy for _,cy in interference],
              '#4fc3f7', big=500, small=25, layers=4, alpha_base=0.10)
    save(fig, 'luca-daniel-db1')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. giorgio-final  — Mediterranean cyclone / storm spiral
# ═══════════════════════════════════════════════════════════════════════════════
def make_giorgio_final():
    fig, ax = new(bg='#020d1a')
    noise_layer(ax, 4, 'Blues', alpha=0.30, sigma=35)
    # Storm spiral arms
    for arm in range(3):
        offset = arm * 2 * np.pi / 3
        t = np.linspace(0, 4*np.pi, 500)
        r_s = 0.02 + 0.28 * (t / (4*np.pi))
        cx, cy = 0.5, 0.52
        xs = cx + r_s * np.cos(t + offset)
        ys = cy + r_s * 0.72 * np.sin(t + offset)
        alpha = 0.55 - 0.1*arm
        ax.plot(xs, ys, color=PALE, lw=0.9 - 0.2*arm, alpha=alpha, zorder=5)
    # Calm eye
    theta = np.linspace(0, 2*np.pi, 200)
    ax.plot(0.5 + 0.022*np.cos(theta), 0.52 + 0.018*np.sin(theta),
            color=PALE, lw=0.8, alpha=0.6, zorder=6)
    # Tiny vessel
    glow_dots(ax, [0.38], [0.42], AMBER, big=600, small=14, layers=5, alpha_base=0.10)
    save(fig, 'giorgio-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. sophia-final  — Algerian military / Sahara enforcement
# ═══════════════════════════════════════════════════════════════════════════════
def make_sophia_final():
    fig, ax = new(bg='#0e0a04')
    # Sand/desert noise
    noise_layer(ax, 5, 'YlOrBr', alpha=0.28, sigma=45)
    terrain(ax, seed=5, alpha=0.30, color='#8b6914')
    r = rng(5)
    # Arrest location dots
    xs = r.beta(2,2,80) * 0.8 + 0.1
    ys = r.beta(2,2,80) * 0.8 + 0.1
    glow_dots(ax, xs, ys, RED, big=250, small=10, layers=3, alpha_base=0.06)
    # A few bright sites
    glow_dots(ax, [0.35, 0.55, 0.68], [0.6, 0.45, 0.7], AMBER,
              big=500, small=20, layers=4, alpha_base=0.10)
    save(fig, 'sophia-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. sophia-db1  — Algeria migration: scraping military reports
# ═══════════════════════════════════════════════════════════════════════════════
def make_sophia_db1():
    fig, ax = new(bg='#0a0806')
    noise_layer(ax, 6, 'copper', alpha=0.20, sigma=35)
    # Faint horizontal "report line" texture
    for y in np.linspace(0.08, 0.92, 22):
        ax.axhline(y, color=AMBER, alpha=0.07, lw=0.5, zorder=2)
    r = rng(6)
    # Data points rising as scraping progresses (left → right)
    xs = np.sort(r.uniform(0.05, 0.95, 60))
    ys = 0.1 + 0.8 * np.cumsum(r.exponential(0.015, 60))
    ys = np.clip(ys / ys.max() * 0.80, 0, 0.90)
    glow_line(ax, xs, ys, AMBER, lw=1.4, spread=5)
    glow_dots(ax, xs[::8], ys[::8], AMBER, big=200, small=14, layers=3, alpha_base=0.08)
    save(fig, 'sophia-db1')

# ═══════════════════════════════════════════════════════════════════════════════
# 7. luca-final  — The Caucasus Corridor flight paths
# ═══════════════════════════════════════════════════════════════════════════════
def make_luca_final():
    fig, ax = new()
    terrain(ax, seed=7, alpha=0.50, color='#1a3550')
    noise_layer(ax, 7, 'Blues', alpha=0.12, sigma=50)
    # Multiple flight corridors
    routes = [
        (0.02, 0.72, 0.98, 0.60, 0.18),
        (0.02, 0.68, 0.98, 0.55, 0.20),
        (0.02, 0.65, 0.98, 0.50, 0.22),
        (0.02, 0.60, 0.98, 0.45, 0.20),
        (0.02, 0.55, 0.98, 0.40, 0.18),
    ]
    for i, (x0,y0,x1,y1,sag) in enumerate(routes):
        alpha_c = 0.3 + 0.14*i
        lw_c = 0.7 + 0.2*i
        t = np.linspace(0, 1, 300)
        mx, my = (x0+x1)/2, (y0+y1)/2 + sag
        bx = (1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1
        by = (1-t)**2*y0 + 2*(1-t)*t*my + t**2*y1
        ax.plot(bx, by, color=AMBER, lw=lw_c*4, alpha=0.05, solid_capstyle='round')
        ax.plot(bx, by, color=AMBER, lw=lw_c, alpha=alpha_c, solid_capstyle='round')
    # Tbilisi / Baku waypoints
    glow_dots(ax, [0.55, 0.68], [0.60, 0.54], AMBER, big=400, small=18, layers=4, alpha_base=0.10)
    save(fig, 'luca-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. nadine-final  — Spring on Two Wheels / cycling safety
# ═══════════════════════════════════════════════════════════════════════════════
def make_nadine_final():
    fig, ax = new(bg='#060e0a')
    # Urban grid (street map aesthetic)
    r = rng(8)
    for x in np.linspace(0, 1, 18):
        ax.axvline(x, color='#1a2e20', lw=2.5 if r.rand()<0.3 else 0.8, alpha=0.7, zorder=1)
    for y in np.linspace(0, 1, 12):
        ax.axhline(y, color='#1a2e20', lw=2.5 if r.rand()<0.3 else 0.8, alpha=0.7, zorder=1)
    # Crash scatter (red dots)
    xs = r.uniform(0.05, 0.95, 35)
    ys = r.uniform(0.05, 0.95, 35)
    glow_dots(ax, xs, ys, RED, big=350, small=12, layers=4, alpha_base=0.08)
    # Single cyclist route (amber)
    cx = np.array([0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95])
    cy = np.array([0.5,  0.55, 0.45, 0.6, 0.5, 0.55, 0.48])
    from scipy.interpolate import make_interp_spline
    spl = make_interp_spline(cx, cy, k=3)
    xs2 = np.linspace(0.05, 0.95, 400)
    glow_line(ax, xs2, spl(xs2), AMBER, lw=2.0, spread=6, alpha=0.9)
    save(fig, 'nadine-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 9. chirag-final  — Election forecast ridge plot
# ═══════════════════════════════════════════════════════════════════════════════
def make_chirag_final():
    fig, ax = new()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ridge_plot(ax, n_ridges=14, seed=9, color=TEAL)
    # Actual result marker
    ax.axvline(0.59, color=RED, lw=1.5, alpha=0.85, zorder=30)
    ax.scatter([0.59], [0.97], color=RED, s=50, zorder=31)
    save(fig, 'chirag-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 10. lou-final  — Don't trust the polls / poll uncertainty
# ═══════════════════════════════════════════════════════════════════════════════
def make_lou_final():
    fig, ax = new()
    x = np.linspace(0, 1, 500)
    r = rng(10)
    # Smooth trend line
    trend = 0.45 + 0.1 * np.sin(x * 3.5) + gaussian_filter(r.normal(0, 0.02, 500), 15)
    # Uncertainty band that widens toward the right
    sigma = 0.01 + 0.18 * x**2
    ax.fill_between(x, trend-sigma*2, trend+sigma*2, color=TEAL, alpha=0.10, zorder=2)
    ax.fill_between(x, trend-sigma, trend+sigma, color=TEAL, alpha=0.20, zorder=3)
    glow_line(ax, x, trend, AMBER, lw=1.8, spread=4, alpha=0.90)
    # Actual result dot (exploded right)
    result_y = trend[-1] + r.normal(0, 0.08)
    glow_dots(ax, [0.97], [np.clip(result_y, 0.1, 0.9)], RED, big=600, small=30, layers=5)
    save(fig, 'lou-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 11. leticia-xiaohan-final  — Ice cream to politics / stacked bars
# ═══════════════════════════════════════════════════════════════════════════════
def make_leticia_xiaohan_final():
    fig, ax = new(bg='#04101a')
    parties = ['#c0392b','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c']
    r = rng(11)
    n_bars = 12
    xs = np.linspace(0.08, 0.92, n_bars)
    width = 0.055
    for xi in xs:
        fracs = r.dirichlet(np.ones(6) * 2)
        bottom = 0.05
        for j, frac in enumerate(fracs):
            h = frac * 0.88
            ax.bar(xi, h, bottom=bottom, width=width, color=parties[j],
                   alpha=0.75, zorder=3, edgecolor='none')
            bottom += h
    # Transition line: ice cream → politics
    ax.axvline(0.5, color=PALE, lw=0.8, alpha=0.35, linestyle='--', zorder=4)
    save(fig, 'leticia-xiaohan-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 12. oliver-final  — Bundestag dot portrait
# ═══════════════════════════════════════════════════════════════════════════════
def make_oliver_final():
    fig, ax = new()
    r = rng(12)
    decade_colors = ['#2980b9','#27ae60','#e74c3c','#f39c12','#8e44ad',
                     '#16a085','#c0392b','#2c3e50']
    # Hemicycle arrangement: multiple arcs
    dots_x, dots_y, dots_c = [], [], []
    total = 0
    for arc_i, n_arc in enumerate([40, 55, 70, 85, 100, 115, 130, 141]):
        radius = 0.18 + arc_i * 0.07
        angles = np.linspace(np.pi * 0.08, np.pi * 0.92, n_arc)
        for angle in angles:
            dots_x.append(0.5 + radius * np.cos(angle))
            dots_y.append(0.28 + radius * np.sin(angle))
            decade = r.randint(0, len(decade_colors))
            dots_c.append(decade_colors[decade])
            total += 1
            if total >= 736:
                break
        if total >= 736:
            break
    ax.scatter(dots_x, dots_y, s=18, c=dots_c, alpha=0.82, linewidths=0, zorder=3)
    save(fig, 'oliver-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 13. giorgio-db2  — Remigrazione: word entering parliament
# ═══════════════════════════════════════════════════════════════════════════════
def make_giorgio_db2():
    fig, ax = new(bg='#08060f')
    noise_layer(ax, 13, 'Purples', alpha=0.20, sigma=40)
    # Parliamentary chamber: semicircle of faint seats
    for arc_i, n_arc in enumerate([20, 30, 38]):
        radius = 0.22 + arc_i * 0.09
        angles = np.linspace(np.pi*0.1, np.pi*0.9, n_arc)
        xs = 0.5 + radius * np.cos(angles)
        ys = 0.25 + radius * np.sin(angles)
        ax.scatter(xs, ys, s=12, c=NAVY, alpha=0.6, linewidths=0, zorder=2)
    # Word growing like a shadow from a podium
    for size, alpha_t in [(80,0.06),(55,0.12),(38,0.22),(24,0.55)]:
        ax.text(0.5, 0.48, 'REMIGRAZIONE', fontsize=size, fontfamily='monospace',
                color=RED, alpha=alpha_t, ha='center', va='center',
                fontweight='bold', zorder=5, transform=ax.transData)
    save(fig, 'giorgio-db2')

# ═══════════════════════════════════════════════════════════════════════════════
# 14. bjarne-final  — Paper money dissolving
# ═══════════════════════════════════════════════════════════════════════════════
def make_bjarne_final():
    fig, ax = new(bg='#0d0900')
    noise_layer(ax, 14, 'YlOrBr', alpha=0.22, sigma=30)
    r = rng(14)
    # Stack of banknote rectangles
    for i in range(8, 0, -1):
        y0 = 0.15 + i * 0.03
        alpha_note = 0.08 + i * 0.06
        rect = plt.Rectangle((0.18, y0), 0.64, 0.18,
                              facecolor=AMBER, alpha=alpha_note*0.6,
                              edgecolor=AMBER, linewidth=0.5, zorder=3+i)
        ax.add_patch(rect)
    # Dissolving particles rising up
    n_part = 120
    px = r.uniform(0.20, 0.80, n_part)
    py = r.beta(2, 1, n_part) * 0.8 + 0.15
    sizes = r.uniform(5, 60, n_part)
    alphas = (1 - (py - 0.15)/0.85) * 0.6
    ax.scatter(px, py, s=sizes, c=AMBER, alpha=alphas.clip(0.05, 0.7),
               linewidths=0, zorder=6)
    save(fig, 'bjarne-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 15. ujwal-final  — Efficiency trap / supply chain chokepoints
# ═══════════════════════════════════════════════════════════════════════════════
def make_ujwal_final():
    fig, ax = new(bg='#020c18')
    noise_layer(ax, 15, 'Blues', alpha=0.20, sigma=50)
    # Ocean texture: faint horizontal lines
    for y in np.linspace(0, 1, 40):
        ax.axhline(y, color='#0a2040', lw=0.4, alpha=0.5, zorder=1)
    # Trade route arteries
    routes = [
        (0.02, 0.38, 0.95, 0.62, 0.05),
        (0.02, 0.55, 0.95, 0.45, -0.05),
        (0.05, 0.68, 0.90, 0.35, 0.08),
    ]
    for x0,y0,x1,y1,sag in routes:
        bezier_arc(ax, x0,y0,x1,y1,sag, AMBER, lw=0.9)
    # Chokepoint nodes (Hormuz, Suez, Malacca, Bosporus)
    choke = [(0.62, 0.48), (0.48, 0.50), (0.81, 0.45), (0.53, 0.58)]
    for cx, cy in choke:
        glow_dots(ax, [cx], [cy], RED, big=1200, small=16, layers=6, alpha_base=0.08)
    save(fig, 'ujwal-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 16. anna-final  — CEE price convergence
# ═══════════════════════════════════════════════════════════════════════════════
def make_anna_final():
    fig, ax = new()
    # West-to-East price gradient as colour field
    x = np.linspace(0, 1, 900)
    y = np.linspace(0, 1, 600)
    X, Y = np.meshgrid(x, y)
    # Warm east (amber) converging toward cool west (teal)
    Z = 0.3 + 0.7 * X + 0.15 * smooth_noise(600, 900, 30, 16)
    cmap = mc.LinearSegmentedColormap.from_list('conv', [TEAL, BG, AMBER])
    ax.imshow(Z, extent=[0,1,0,1], cmap=cmap, aspect='auto',
              origin='lower', zorder=1, alpha=0.80)
    # Contour overlay
    ax.contour(X, Y, Z, levels=12, colors=[PALE], linewidths=0.4, alpha=0.25, zorder=3)
    # Convergence arrow
    glow_line(ax, [0.85, 0.5], [0.5, 0.5], PALE, lw=2.0, spread=6, alpha=0.6)
    save(fig, 'anna-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 17. ffal-final  — Education / career network
# ═══════════════════════════════════════════════════════════════════════════════
def make_ffal_final():
    fig, ax = new()
    noise_layer(ax, 17, 'Blues', alpha=0.12, sigma=40)
    r = rng(17)
    # Root node (university gate)
    root = (0.5, 0.12)
    # Career path branches (2 main: male/female tracks)
    def branch(start, end, color, depth=0, spread=0.15):
        if depth > 3:
            return
        glow_line(ax, [start[0], end[0]], [start[1], end[1]], color, lw=1.0-depth*0.2, spread=3)
        if depth < 3:
            for _ in range(2):
                new_end = (end[0] + r.uniform(-spread, spread),
                           end[1] + r.uniform(0.1, 0.22))
                if 0.02 < new_end[0] < 0.98 and new_end[1] < 0.95:
                    branch(end, new_end, color, depth+1, spread*0.7)
    branch(root, (0.32, 0.38), TEAL)
    branch(root, (0.68, 0.38), AMBER)
    glow_dots(ax, [root[0]], [root[1]], PALE, big=400, small=22, layers=4)
    save(fig, 'ffal-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 18. aishwarya-final  — Turkey press freedom: 1427 dots
# ═══════════════════════════════════════════════════════════════════════════════
def make_aishwarya_final():
    fig, ax = new(bg='#040508')
    noise_layer(ax, 18, 'Oranges', alpha=0.10, sigma=40)
    r = rng(18)
    # Turkey-shaped cluster (elongated, centered)
    n = 1427
    raw_x = r.normal(0.5, 0.20, n)
    raw_y = r.normal(0.52, 0.12, n)
    # Turkey is wider than tall; clip to rough boundary
    mask = ((raw_x > 0.08) & (raw_x < 0.92) &
            (raw_y > 0.28) & (raw_y < 0.76))
    xs = raw_x[mask][:1000]
    ys = raw_y[mask][:1000]
    sizes = r.uniform(3, 18, len(xs))
    alphas = r.uniform(0.3, 0.85, len(xs))
    ax.scatter(xs, ys, s=sizes, c=CORAL, alpha=alphas, linewidths=0, zorder=4)
    # A few bright "major events"
    glow_dots(ax, [0.3, 0.55, 0.72], [0.52, 0.48, 0.55], CORAL,
              big=800, small=20, layers=5, alpha_base=0.10)
    save(fig, 'aishwarya-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 19. skyler-final  — Eagle Hills ad investigation
# ═══════════════════════════════════════════════════════════════════════════════
def make_skyler_final():
    fig, ax = new(bg='#060912')
    noise_layer(ax, 19, 'Blues', alpha=0.15, sigma=30)
    r = rng(19)
    # Ad grid cards
    ad_colors = [AMBER, RED, TEAL, AMBER, PALE, RED]
    for row in range(3):
        for col in range(4):
            x = 0.08 + col * 0.23
            y = 0.62 - row * 0.25
            alpha = r.uniform(0.10, 0.30)
            rect = plt.Rectangle((x, y), 0.19, 0.21,
                                  facecolor=ad_colors[(row*4+col)%6],
                                  alpha=alpha, edgecolor=PALE,
                                  linewidth=0.3, zorder=3)
            ax.add_patch(rect)
    # Highlight: "93% English" vs Russian
    rect_h = plt.Rectangle((0.08, 0.12), 0.84, 0.38,
                             facecolor='none', edgecolor=RED,
                             linewidth=1.5, alpha=0.6, zorder=5)
    ax.add_patch(rect_h)
    glow_dots(ax, [0.15, 0.78], [0.31, 0.31], [BLUE, RED],
              big=300, small=14, layers=3, alpha_base=0.08)
    save(fig, 'skyler-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 20. lou-db1  — Comedy attention economy / Wikipedia spikes
# ═══════════════════════════════════════════════════════════════════════════════
def make_lou_db1():
    fig, ax = new()
    x = np.linspace(0, 1, 600)
    r = rng(20)
    # Baseline noise (low attention)
    baseline = 0.12 + 0.04 * gaussian_filter(r.standard_normal(600), 8)
    # Scandal spike (sharp, tall, decays fast) — RED
    scandal = np.zeros(600)
    scandal[220] = 1.0
    scandal = gaussian_filter(scandal, 12) * 0.70
    # Joke plateau (lower, sustained) — GREEN
    joke = np.zeros(600)
    joke[350:] = r.uniform(0.18, 0.28, 250)
    joke[:350] = baseline[:350]
    joke = gaussian_filter(joke, 5)
    ax.fill_between(x, 0, baseline + scandal, color=RED, alpha=0.35, zorder=3)
    ax.fill_between(x, 0, joke, color=GREEN, alpha=0.30, zorder=2)
    glow_line(ax, x, baseline + scandal, RED, lw=1.4, spread=4)
    glow_line(ax, x, joke, GREEN, lw=1.2, spread=4)
    # Labels (tiny)
    ax.text(0.38, 0.82, 'scandal', fontsize=6, color=RED, alpha=0.7,
            fontfamily='monospace', va='center', ha='center', zorder=10)
    ax.text(0.70, 0.35, 'joke', fontsize=6, color=GREEN, alpha=0.7,
            fontfamily='monospace', va='center', ha='center', zorder=10)
    save(fig, 'lou-db1')

# ═══════════════════════════════════════════════════════════════════════════════
# 21. farhan-final  — Heat-stressed India
# ═══════════════════════════════════════════════════════════════════════════════
def make_farhan_final():
    fig, ax = new(bg='#080404')
    # India-shaped heat field (elongated triangle pointing south)
    centers = [
        (0.5, 0.75, 1.0),(0.35, 0.65, 0.8),(0.65, 0.65, 0.8),
        (0.45, 0.52, 0.9),(0.55, 0.50, 0.9),(0.5, 0.38, 0.7),
        (0.5, 0.25, 0.5),(0.40, 0.42, 0.6),(0.60, 0.40, 0.6),
        (0.30, 0.70, 0.5),(0.70, 0.72, 0.4),
    ]
    heat_field(ax, centers, '#e74c3c', spread=0.10, gamma=0.5, alpha=0.85)
    heat_field(ax, [(0.5, 0.68, 0.6),(0.38, 0.55, 0.5)], '#ff9900', spread=0.07, gamma=0.6, alpha=0.5)
    # White contour overlay (maternal health)
    x = np.linspace(0, 1, 300)
    y = np.linspace(0, 1, 200)
    X, Y = np.meshgrid(x, y)
    Z = smooth_noise(200, 300, 15, 21)
    ax.contour(X, Y, Z, levels=8, colors=[PALE], linewidths=0.5, alpha=0.25, zorder=5)
    save(fig, 'farhan-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 22. ashley-db2  — Heat deaths USA: red tide
# ═══════════════════════════════════════════════════════════════════════════════
def make_ashley_db2():
    fig, ax = new(bg='#080004')
    # US heat-death density (highest in Southwest/Southeast)
    centers = [
        (0.18, 0.40, 1.0),(0.28, 0.35, 0.9),(0.35, 0.32, 0.8),
        (0.55, 0.30, 0.7),(0.65, 0.38, 0.7),(0.72, 0.42, 0.6),
        (0.45, 0.50, 0.6),(0.60, 0.55, 0.5),(0.25, 0.55, 0.4),
        (0.80, 0.48, 0.4),(0.35, 0.45, 0.5),
    ]
    heat_field(ax, centers, RED, spread=0.10, gamma=0.4, alpha=0.88)
    heat_field(ax, [(0.5, 0.4, 1.0)], CORAL, spread=0.25, gamma=0.6, alpha=0.30)
    # Tiny hurricane icons
    for hx, hy in [(0.75, 0.65),(0.82, 0.55),(0.68, 0.60)]:
        theta = np.linspace(0, 2*np.pi, 100)
        r_h = 0.012
        ax.plot(hx + r_h*np.cos(theta)*np.linspace(1,0.1,100),
                hy + r_h*np.sin(theta)*np.linspace(1,0.1,100),
                color=PALE, lw=0.6, alpha=0.30, zorder=5)
    save(fig, 'ashley-db2')

# ═══════════════════════════════════════════════════════════════════════════════
# 23. leticia-xiaohan-db2  — Berlin May Day demo route
# ═══════════════════════════════════════════════════════════════════════════════
def make_leticia_xiaohan_db2():
    fig, ax = new(bg='#040a06')
    # Street grid (Berlin block scale)
    for x in np.linspace(0, 1, 30):
        ax.axvline(x, color='#0e1f0e', lw=1.2, alpha=0.8, zorder=1)
    for y in np.linspace(0, 1, 20):
        ax.axhline(y, color='#0e1f0e', lw=1.2, alpha=0.8, zorder=1)
    # Demo route evolving east over decades (5 decades, each a slightly different path)
    base_x = np.array([0.15, 0.25, 0.35, 0.50, 0.65, 0.78, 0.88])
    base_y = np.array([0.55, 0.52, 0.58, 0.50, 0.54, 0.48, 0.52])
    decade_colors = ['#4fc3f7','#29b6f6','#039be5','#0288d1','#01579b']
    r = rng(23)
    for i, dc in enumerate(decade_colors):
        jitter_x = np.sort(base_x + r.normal(0, 0.03, len(base_x)))
        jitter_y = base_y + r.normal(0, 0.03, len(base_y))
        jitter_x = np.clip(jitter_x, 0.05, 0.95)
        jitter_y = np.clip(jitter_y, 0.05, 0.95)
        from scipy.interpolate import make_interp_spline
        spl = make_interp_spline(jitter_x, jitter_y, k=3)
        xs = np.linspace(0.15, 0.88, 300)
        alpha_c = 0.25 + 0.15*i
        lw_c = 0.6 + 0.3*i
        ax.plot(xs, spl(xs), color=dc, lw=lw_c, alpha=alpha_c, zorder=4+i)
    # Brightest (latest) route
    glow_line(ax, np.linspace(0.15, 0.88, 300), spl(np.linspace(0.15, 0.88, 300)),
              '#4fc3f7', lw=2.0, spread=5, alpha=0.85)
    save(fig, 'leticia-xiaohan-db2')

# ═══════════════════════════════════════════════════════════════════════════════
# 24. leticia-xiaohan-db1  — Berlin emergency response times
# ═══════════════════════════════════════════════════════════════════════════════
def make_leticia_xiaohan_db1():
    fig, ax = new(bg='#030810')
    # District grid
    for x in np.linspace(0, 1, 16):
        ax.axvline(x, color='#0a1828', lw=2.0, alpha=0.9, zorder=1)
    for y in np.linspace(0, 1, 11):
        ax.axhline(y, color='#0a1828', lw=2.0, alpha=0.9, zorder=1)
    # Response time gradient: fast (green, west) → slow (red, east/south)
    x = np.linspace(0, 1, 900)
    y = np.linspace(0, 1, 600)
    X, Y = np.meshgrid(x, y)
    Z = 0.4*X + 0.3*(1-Y) + 0.15*smooth_noise(600, 900, 40, 24)
    cmap = mc.LinearSegmentedColormap.from_list('resp', [GREEN, AMBER, RED])
    ax.imshow(Z, extent=[0,1,0,1], cmap=cmap, aspect='auto',
              origin='lower', alpha=0.55, zorder=2)
    # Ambulance light (Neukölln)
    glow_dots(ax, [0.62], [0.35], '#4fc3f7', big=1200, small=18, layers=6, alpha_base=0.10)
    save(fig, 'leticia-xiaohan-db1')

# ═══════════════════════════════════════════════════════════════════════════════
# 25. elena-m-final  — Data centres / Virginia electricity
# ═══════════════════════════════════════════════════════════════════════════════
def make_elena_m_final():
    fig, ax = new(bg='#030509')
    noise_layer(ax, 25, 'Blues', alpha=0.15, sigma=40)
    # Night-time grid of streets
    for x in np.linspace(0, 1, 40):
        ax.axvline(x, color='#080f1a', lw=0.8, alpha=0.7, zorder=1)
    for y in np.linspace(0, 1, 27):
        ax.axhline(y, color='#080f1a', lw=0.8, alpha=0.7, zorder=1)
    # Server farm cluster — northern Virginia (right-centre)
    farm_centers = [(0.62, 0.60, 1.0),(0.68, 0.55, 0.9),(0.58, 0.65, 0.8),
                    (0.72, 0.62, 0.7),(0.65, 0.50, 0.6)]
    heat_field(ax, farm_centers, PALE, spread=0.06, gamma=0.35, alpha=0.90)
    # Power transmission lines radiating out
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        ex = 0.64 + 0.45 * np.cos(angle)
        ey = 0.58 + 0.45 * np.sin(angle)
        glow_line(ax, [0.64, ex], [0.58, ey], AMBER, lw=0.5, spread=2, alpha=0.30)
    glow_dots(ax, [0.64], [0.58], PALE, big=1500, small=14, layers=6, alpha_base=0.08)
    save(fig, 'elena-m-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 26. daniel-final  — Native American land loss / peeling layers
# ═══════════════════════════════════════════════════════════════════════════════
def make_daniel_final():
    fig, ax = new(bg='#080503')
    # Layered territory shapes (abstract polygons, each smaller and lighter)
    layer_colors = ['#5d3a1a','#7d5020','#9b6a2a','#c9a84c','#e8d89a']
    layer_alphas = [0.80, 0.65, 0.50, 0.38, 0.25]
    r = rng(26)
    for i, (col, alp) in enumerate(zip(layer_colors, layer_alphas)):
        scale = 0.85 - i * 0.12
        # Irregular polygon (abstract US territory)
        angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
        jitter = 1.0 + r.uniform(-0.2, 0.2, 12)
        rx = 0.5 + scale * 0.42 * jitter * np.cos(angles)
        ry = 0.5 + scale * 0.34 * jitter * np.sin(angles)
        poly = plt.Polygon(list(zip(rx, ry)), closed=True,
                           facecolor=col, alpha=alp, edgecolor=PALE,
                           linewidth=0.5, zorder=3+i)
        ax.add_patch(poly)
    save(fig, 'daniel-final')

# ═══════════════════════════════════════════════════════════════════════════════
# 27. maria-final  — Food deserts / redlining
# ═══════════════════════════════════════════════════════════════════════════════
def make_maria_final():
    fig, ax = new(bg='#030810')
    # Faint lit census-tract grid
    for x in np.linspace(0, 1, 55):
        for y in np.linspace(0, 1, 37):
            alpha = 0.05 + 0.12 * np.random.RandomState(int(x*100+y*10)).rand()
            ax.scatter([x], [y], s=6, c=PALE, alpha=alpha, linewidths=0, zorder=2)
    # Food desert voids: large dark blobs suppress the grid
    void_centers = [(0.20, 0.65),(0.48, 0.42),(0.65, 0.28),(0.78, 0.70),(0.35, 0.30)]
    for cx, cy in void_centers:
        heat_field(ax, [(cx, cy, 1.0)], BG, spread=0.09, gamma=0.5, alpha=0.92)
    # Redlining boundary lines
    r = rng(27)
    for _ in range(8):
        xs = r.uniform(0.05, 0.95, 4)
        ys = r.uniform(0.05, 0.95, 4)
        xs.sort()
        ax.plot(xs, ys, color=RED, lw=0.6, alpha=0.28, zorder=5)
    save(fig, 'maria-final')

# ═══════════════════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating article thumbnails...')
    make_elenadreyer_final()
    make_elenaiva_db2()
    make_luca_daniel_db1()
    make_giorgio_final()
    make_sophia_final()
    make_sophia_db1()
    make_luca_final()
    make_nadine_final()
    make_chirag_final()
    make_lou_final()
    make_leticia_xiaohan_final()
    make_oliver_final()
    make_giorgio_db2()
    make_bjarne_final()
    make_ujwal_final()
    make_anna_final()
    make_ffal_final()
    make_aishwarya_final()
    make_skyler_final()
    make_lou_db1()
    make_farhan_final()
    make_ashley_db2()
    make_leticia_xiaohan_db2()
    make_leticia_xiaohan_db1()
    make_elena_m_final()
    make_daniel_final()
    make_maria_final()
    print(f'\nDone — 27 images written to:\n  {OUT}')
