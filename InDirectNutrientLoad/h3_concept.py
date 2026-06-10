"""
Conceptual illustration of the H3 hexagonal aggregation workflow
on the Lake Huron shoreline.

Steps shown:
 (a) raw coastal-wetland point loads
 (b) H3 resolution-6 grid laid over the shoreline
 (c) each cell colored by the MEDIAN load of the wetlands inside it
 (d) callout: how one cell's median is computed

The wetland points/loads are SYNTHETIC and illustrative; swap in real data
by replacing the `pts_ll` / `load` arrays. The shoreline is the real
Lake Huron polygon (Natural Earth 10m).
"""
import os
import urllib.request
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import h3
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.collections import PolyCollection
from matplotlib.patches import ConnectionPatch

CRS_MAP = 3174          # NAD83 / Great Lakes Albers (equal-area) – matches manuscript
RES = 6                 # H3 resolution used in the manuscript (~36 km^2 cells)
CMAP = "cividis"        # colorblind-safe, matches manuscript
rng = np.random.default_rng(11)

HERE = os.path.dirname(os.path.abspath(__file__))   # look for data next to this script
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"

def load_geojson(local_name, fallback_url, keep_names):
    """Read a local subset geojson; if absent, download the full Natural Earth
    file and subset it to `keep_names`. Returns a GeoDataFrame in EPSG:4326."""
    path = os.path.join(HERE, local_name)
    if os.path.exists(path):
        return gpd.read_file(path).to_crs(4326)
    print(f"{local_name} not found locally; downloading from Natural Earth...")
    tmp = os.path.join(HERE, "_ne_download.geojson")
    urllib.request.urlretrieve(fallback_url, tmp)
    g = gpd.read_file(tmp).to_crs(4326)
    g = g[g["name"].isin(keep_names)][["name", "geometry"]].reset_index(drop=True)
    g.to_file(path, driver="GeoJSON")     # cache the subset for next time
    os.remove(tmp)
    return g

# ----------------------------------------------------------------------
# 1. Lake Huron shoreline
# ----------------------------------------------------------------------
lakes = load_geojson("lake_huron.geojson", f"{NE}/ne_10m_lakes.geojson",
                     ["Lake Huron"])
geom = lakes.loc[lakes["name"] == "Lake Huron", "geometry"].iloc[0]
if geom.geom_type == "MultiPolygon":
    geom = max(geom.geoms, key=lambda g: g.area)
shore = geom.exterior                       # the shoreline line

lake_gdf = gpd.GeoSeries([geom], crs=4326).to_crs(CRS_MAP)

# US (Michigan) vs Canada (Ontario) land, for splitting the shoreline
states = load_geojson("mi_on.geojson",
                      f"{NE}/ne_10m_admin_1_states_provinces.geojson",
                      ["Michigan", "Ontario"])
mi_geom = states.loc[states["name"] == "Michigan", "geometry"].iloc[0]
on_geom = states.loc[states["name"] == "Ontario", "geometry"].iloc[0]
mi_gdf = gpd.GeoSeries([mi_geom], crs=4326).to_crs(CRS_MAP)
mi_proj = mi_gdf.iloc[0]
on_proj = gpd.GeoSeries([on_geom], crs=4326).to_crs(CRS_MAP).iloc[0]

# ----------------------------------------------------------------------
# 2. Synthetic coastal-wetland points + right-skewed loads (US side only)
# ----------------------------------------------------------------------
# oversample the whole shoreline, then keep points nearer Michigan than Ontario
M = 1600
d = rng.uniform(0, shore.length, M)
base = [shore.interpolate(x) for x in d]
lon = np.array([p.x for p in base]) + rng.normal(0, 0.018, M)
lat = np.array([p.y for p in base]) + rng.normal(0, 0.018, M)
cand = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326).to_crs(CRS_MAP)
us_side = np.array([p.distance(mi_proj) < p.distance(on_proj) for p in cand])
lon, lat = lon[us_side], lat[us_side]
N = len(lon)
pts_ll = np.column_stack([lat, lon])

# spatial trend (south + Saginaw-Bay side richer) + strong right skew
trend = (44.9 - lat) * 1.1 + (lon + 82.5) * 0.5
load = np.exp(0.55 * trend + rng.normal(0, 0.85, N))   # g m^-2 yr^-1, log-normal
load = np.clip(load, 0.05, None)

pts_gdf = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326).to_crs(CRS_MAP)
px = np.array([p.x for p in pts_gdf]); py = np.array([p.y for p in pts_gdf])

# ----------------------------------------------------------------------
# 3. H3 indexing + median per cell
# ----------------------------------------------------------------------
cell_of = np.array([h3.latlng_to_cell(la, lo, RES) for la, lo in pts_ll])
cells = {}
for c, v in zip(cell_of, load):
    cells.setdefault(c, []).append(v)
cell_median = {c: float(np.median(v)) for c, v in cells.items()}

# continuous coastal hex ribbon (cells with points + their neighbours) for the grid panel
ribbon = set()
for c in cells:
    ribbon.update(h3.grid_disk(c, 1))

def cell_poly(c):
    b = h3.cell_to_boundary(c)               # list of (lat, lon)
    g = Polygon([(lo, la) for la, lo in b])
    return gpd.GeoSeries([g], crs=4326).to_crs(CRS_MAP).iloc[0]

ribbon_polys = {c: cell_poly(c) for c in ribbon}
filled_polys = {c: ribbon_polys[c] for c in cell_median}

# ----------------------------------------------------------------------
# 4. Figure
# ----------------------------------------------------------------------
plt.rcParams.update({"font.size": 6.5, "font.family": "DejaVu Sans",
                     "axes.titlesize": 7.5, "axes.titleweight": "bold"})
norm = LogNorm(vmin=np.quantile(load, 0.02), vmax=np.quantile(load, 0.98))
cmap = mpl.colormaps[CMAP]

figW, figH = 6.69, 5.3
fig = plt.figure(figsize=(figW, figH))
xmin, xmax = px.min(), px.max()
ymin, ymax = py.min(), py.max()
padx = 0.07 * (xmax - xmin); pady = 0.07 * (ymax - ymin)
mapw = (xmax - xmin) + 2 * padx; maph = (ymax - ymin) + 2 * pady
asp = mapw / maph

# --- top row: three map strips a, b, c, sized so they fill the width ---
top_m = 0.10                      # room above maps for suptitle + panel labels
Hf = 0.62                         # map height fraction
Wf = asp * Hf * (figH / figW)     # width fraction giving equal aspect (no whitespace)
y_m_top = 1 - top_m
y_m_bot = y_m_top - Hf
left_m = 0.035
content_r = 0.875                 # right edge of the map strips (colorbar sits beyond)
sg = (content_r - left_m - 3 * Wf) / 2     # even gaps that fill the row
xA = left_m
xB = left_m + Wf + sg
xC = left_m + 2 * (Wf + sg)
axA = fig.add_axes([xA, y_m_bot, Wf, Hf])
axB = fig.add_axes([xB, y_m_bot, Wf, Hf])
axC = fig.add_axes([xC, y_m_bot, Wf, Hf])

# --- bottom band: (d) callout = explanation text (left) + zoom hexagon (right, under c) ---
gap_below = 0.03; bottom_m = 0.03
band_top = y_m_bot - gap_below
band_h = band_top - bottom_m
hexW = band_h * (figH / figW)                  # square display box
cxc = xC + Wf / 2
axHex = fig.add_axes([cxc - hexW / 2, bottom_m, hexW, band_h])

def base_map(ax):
    mi_gdf.plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=0)
    lake_gdf.plot(ax=ax, facecolor="#eef3f6", edgecolor="#7a7a7a", linewidth=0.5, zorder=1)
    ax.set_xlim(xmin - padx, xmax + padx); ax.set_ylim(ymin - pady, ymax + pady)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)

# ---- (a) raw point loads
base_map(axA)
axA.scatter(px, py, c=load, cmap=cmap, norm=norm, s=5,
            edgecolor="white", linewidth=0.1, zorder=3)
axA.set_title("(a)", loc="left", fontsize=7)

# ---- (b) H3 grid overlay
base_map(axB)
pc = PolyCollection([np.array(p.exterior.coords) for p in ribbon_polys.values()],
                    facecolors="none", edgecolors="#c0392b", linewidths=0.3, zorder=2)
axB.add_collection(pc)
axB.scatter(px, py, c="#2c3e50", s=1.8, zorder=3)
axB.set_title("(b)", loc="left", fontsize=7)

# ---- (c) median per cell
base_map(axC)
vals = np.array([cell_median[c] for c in filled_polys])
pc2 = PolyCollection([np.array(p.exterior.coords) for p in filled_polys.values()],
                     array=vals, cmap=cmap, norm=norm,
                     edgecolors="white", linewidths=0.25, zorder=2)
axC.add_collection(pc2)
axC.set_title("(c)", loc="left", fontsize=7)

# ---- (d) single-cell callout
# pick a cell with >=5 points and the strongest right-skew (max/min ratio)
cand = {c: v for c, v in cells.items() if len(v) >= 5}
focus = max(cand, key=lambda c: max(cand[c]) / min(cand[c]))
fb = cell_poly(focus)
fmembers = cell_of == focus
fx, fy, fv = px[fmembers], py[fmembers], load[fmembers]

axHex.set_aspect("equal"); axHex.set_xticks([]); axHex.set_yticks([])
for s in axHex.spines.values(): s.set_visible(False)
axHex.add_collection(PolyCollection([np.array(fb.exterior.coords)],
                     facecolors=cmap(norm(cell_median[focus])), alpha=0.30,
                     edgecolors="#c0392b", linewidths=1.0))
axHex.scatter(fx, fy, c=fv, cmap=cmap, norm=norm, s=42,
              edgecolor="white", linewidth=0.6, zorder=4)
cx, cy = fb.centroid.x, fb.centroid.y
for x, y, v in zip(fx, fy, fv):
    ang = np.arctan2(y - cy, x - cx)
    dx, dy = 8 * np.cos(ang), 8 * np.sin(ang)
    axHex.annotate(f"{v:.1f}", (x, y), textcoords="offset points", xytext=(dx, dy),
                   ha="center", va="center", fontsize=5, color="#33424a", zorder=5)
bx0, by0, bx1, by1 = fb.bounds
m = 0.14 * (bx1 - bx0)
axHex.set_xlim(bx0 - m, bx1 + m); axHex.set_ylim(by0 - m, by1 + m)
med = cell_median[focus]; mean = float(np.mean(fv))

# (d) label + explanation text in the left part of the band
txt_x = (left_m + (cxc - hexW / 2 - 0.02)) / 2
fig.text(left_m, band_top - 0.005, "(d) why the median", fontsize=7,
         fontweight="bold", ha="left", va="top")
fig.text(txt_x, bottom_m + band_h * 0.46,
         f"{len(fv)} wetlands fall in the highlighted cell\n"
         f"loads: {', '.join(f'{v:.1f}' for v in np.sort(fv))}\n"
         f"mean = {mean:.1f}  (skewed by the {max(fv):.1f} outlier)\n"
         f"median = {med:.1f}  \u2192  the cell's value",
         fontsize=6.5, ha="center", va="center", color="#1a2429", linespacing=1.6,
         bbox=dict(boxstyle="round,pad=0.5", fc="#f0eee6", ec="#b8b8b8", lw=0.6))

# connector from focus cell in (c) down to the zoom hexagon
axC.add_collection(PolyCollection([np.array(fb.exterior.coords)],
                   facecolors="none", edgecolors="#c0392b", linewidths=1.0, zorder=5))
con = ConnectionPatch(xyA=(cx, by0), coordsA=axC.transData,
                      xyB=(cx, by1), coordsB=axHex.transData,
                      arrowstyle="-|>", color="#c0392b", lw=0.9,
                      connectionstyle="arc3,rad=0.0")
fig.add_artist(con)

# shared colorbar, aligned to the map row
cax = fig.add_axes([content_r + 0.018, y_m_bot, 0.013, Hf])
cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.ax.yaxis.set_major_locator(mpl.ticker.LogLocator(base=10, subs=(1.0, 2.0, 5.0), numticks=20))
cb.ax.yaxis.set_minor_locator(mpl.ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=60))
cb.ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
cb.ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
cb.ax.tick_params(labelsize=5.5, length=2.5, width=0.5)
cb.set_label("nutrient load (g m$^{-2}$ yr$^{-1}$)", fontsize=6)

# fig.suptitle("Aggregating coastal-wetland loads to an H3 hexagonal grid",
#              fontsize=9, fontweight="bold", x=0.5, y=0.97)

fig.savefig(os.path.join(HERE, "h3_concept.jpeg"), dpi=300, facecolor="white")
fig.savefig(os.path.join(HERE, "h3_concept.pdf"), facecolor="white")
print("focus cell members:", len(fv), "median", round(med, 2))
print("n cells filled:", len(filled_polys), "n points:", N)
print("saved")