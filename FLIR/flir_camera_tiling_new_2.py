import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button

# ── Fixed parameters ──────────────────────────────────────────────────────────
SENSOR_W_PX  = 640
SENSOR_H_PX  = 512
PIXEL_PITCH  = 12e-3
SENSOR_W_MM  = SENSOR_W_PX * PIXEL_PITCH   # 7.680 mm
SENSOR_H_MM  = SENSOR_H_PX * PIXEL_PITCH   # 6.144 mm
F2           = 36.0
BEAM_D_MM    = 0.45
OBJECT_DIST_DEFAULT = 4 * 25.4             # 101.6 mm (4 inches)
SENSOR_BACK  = 50.92

RELAY_FL = [47.85, 72.71, 98.09, 148.34, 198.55]

# ── Optics ────────────────────────────────────────────────────────────────────
def analyze(f1, obj_dist=OBJECT_DIST_DEFAULT, sbd=SENSOR_BACK):
    u1 = obj_dist
    if abs(u1 - f1) < 1e-9:
        return None
    v1 = f1 * u1 / (u1 - f1)

    denom2 = sbd - F2
    if abs(denom2) < 1e-9:
        return None
    u2 = sbd * F2 / denom2

    d = v1 + u2
    if d <= 0:
        return None

    m1 = -v1 / u1
    m2 = -sbd / u2
    M  = m1 * m2

    beam_img_d = abs(M) * BEAM_D_MM
    beam_px    = beam_img_d / PIXEL_PITCH

    return dict(f1=f1, d=d, v1=v1, u2=u2, M=M, sbd=sbd, obj_dist=u1,
                beam_img_d=beam_img_d, beam_px=beam_px)



# ── Draw functions ────────────────────────────────────────────────────────────
def draw_rays(ax, r):
    ax.clear()
    if r is None:
        ax.text(0.5, 0.5, "No valid solution for these parameters",
                transform=ax.transAxes, ha='center', color='red', fontsize=12)
        ax.set_title('Ray Diagram')
        return

    u1     = r['obj_dist'] if 'obj_dist' in r else OBJECT_DIST_DEFAULT
    x_obj  = -u1
    x_L1   = 0.0
    x_img1 = r['v1']
    x_L2   = r['d']
    x_sens = r['d'] + r['sbd']

    mirror_h = BEAM_D_MM / 2
    m1       = -r['v1'] / u1
    img1_h   = abs(m1) * mirror_h
    final_h  = r['M'] * mirror_h
    y_max    = max(mirror_h, img1_h, abs(final_h), SENSOR_H_MM/2) * 1.7

    ax.axhline(0, color='k', lw=0.8, alpha=0.4)
    ax.plot([x_obj,  x_obj],  [-mirror_h, mirror_h],   color='green',     lw=3,  label='Mirror')
    ax.plot([x_L1,   x_L1],   [-y_max*.8, y_max*.8],   color='blue',      lw=2,  label=f'L1 {r["f1"]:.2f}mm')
    ax.plot([x_img1, x_img1], [-img1_h,   img1_h],     color='purple',    lw=1.5, ls='--', alpha=0.7, label='Intermediate image')
    ax.plot([x_L2,   x_L2],   [-y_max*.8, y_max*.8],   color='royalblue', lw=2,  label=f'L2 Boson {F2}mm')
    ax.add_patch(Rectangle((x_sens, -SENSOR_H_MM/2), SENSOR_W_MM*0.1, SENSOR_H_MM,
                            color='gray', alpha=0.6, label='Sensor'))

    # Chief ray (through centre of each lens)
    for (x0,y0),(x1,y1) in [((x_obj,  mirror_h), (x_L1,   0)),
                              ((x_L1,   0),        (x_img1, -img1_h)),
                              ((x_img1,-img1_h),   (x_L2,   0)),
                              ((x_L2,   0),        (x_sens,  final_h))]:
        ax.annotate('', xy=(x1,y1), xytext=(x0,y0),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.3))

    # Marginal ray (parallel to axis from top of object, bends at focal points)
    # Segment 1: parallel from object top to L1
    ax.annotate('', xy=(x_L1, mirror_h), xytext=(x_obj, mirror_h),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.0, linestyle='dashed'))
    # Segment 2: L1 bends it through rear focal point of L1, hits intermediate image plane
    # After L1, ray passes through rear focal point (x_L1 + f1, 0), then continues to x_img1
    f1 = r['f1']
    slope_after_L1 = (0 - mirror_h) / (f1)          # slope through rear focal point
    y_at_img1 = mirror_h + slope_after_L1 * (x_img1 - x_L1)
    ax.annotate('', xy=(x_img1, y_at_img1), xytext=(x_L1, mirror_h),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.0, linestyle='dashed'))
    # Segment 3: parallel to axis into L2 (telecentric-like, from intermediate image height)
    ax.annotate('', xy=(x_L2, y_at_img1), xytext=(x_img1, y_at_img1),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.0, linestyle='dashed'))
    # Segment 4: L2 bends through its rear focal point toward sensor
    slope_after_L2 = (0 - y_at_img1) / F2
    y_at_sens = y_at_img1 + slope_after_L2 * (x_sens - x_L2)
    ax.annotate('', xy=(x_sens, y_at_sens), xytext=(x_L2, y_at_img1),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.0, linestyle='dashed'))

    for x, lbl in [(x_obj, "Mirror\n4 in"), (x_L1, f"L1\n{r['f1']:.2f}mm"),
                   (x_L2, f"L2\n{F2}mm"),   (x_sens, "Sensor")]:
        ax.text(x, y_max*0.92, lbl, ha='center', va='top', fontsize=8,
                bbox=dict(fc='white', alpha=0.7, pad=2))

    y_ann = -y_max * 0.72
    for xa, xb, lbl in [(x_obj, x_L1, f"{u1:.1f}mm\n({u1/25.4:.2f}in)"),
                         (x_L1, x_L2, f"d={r['d']:.1f}mm\n({r['d']/25.4:.2f}in)"),
                         (x_L2, x_sens, f"{r['sbd']:.1f}mm\n({r['sbd']/25.4:.2f}in)")]:
        ax.annotate('', xy=(xb, y_ann), xytext=(xa, y_ann),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1))
        ax.text((xa+xb)/2, y_ann - y_max*0.08, lbl, ha='center', fontsize=8,
                bbox=dict(fc='lightyellow', alpha=0.8, pad=1))

    ax.set_xlim(x_obj - u1*0.12, x_sens + u1*0.12)
    ax.set_ylim(-y_max, y_max)
    ax.set_xlabel('Optical axis (mm)')
    ax.set_ylabel('Height (mm)')
    ax.set_title('Two-Lens Ray Diagram  (L1 = relay, L2 = fixed Boson 36mm)')
    ax.grid(True, ls='--', alpha=0.5)
    ax.legend(loc='upper center', fontsize=8, ncol=3, framealpha=0.9)


def draw_sensor(ax, r):
    ax.clear()
    if r is None:
        ax.text(0.5, 0.5, "No valid solution for these parameters",
                transform=ax.transAxes, ha='center', color='red', fontsize=12)
        ax.set_title('Sensor Footprint')
        return

    sw, sh = SENSOR_W_MM/2, SENSOR_H_MM/2
    br = r['beam_img_d'] / 2

    ax.add_patch(Rectangle((-sw, -sh), SENSOR_W_MM, SENSOR_H_MM,
                            fill=False, ec='green', lw=2, label='Sensor'))
    mirror_img_r = abs(r['M']) * 25.4 / 2   # 1 inch mirror projected onto sensor
    ax.add_patch(Circle((0,0), mirror_img_r, fill=False, ec='steelblue', lw=2,
                        ls='-',  label=f'Mirror edge  ⌀{mirror_img_r*2:.2f}mm'))
    ax.add_patch(Circle((0,0), br*3, color='yellow', alpha=0.45, label=f'3× beam  ({br*6:.3f}mm)'))
    ax.add_patch(Circle((0,0), br*2, color='orange', alpha=0.55, label=f'2× beam  ({br*4:.3f}mm)'))
    ax.add_patch(Circle((0,0), br,   color='red',    alpha=0.85,
                        label=f'Beam  ⌀{r["beam_img_d"]:.3f}mm  ({r["beam_px"]:.1f}px)'))
    ax.plot(0, 0, 'k+', ms=10)

    ax.text(0.02, 0.98, f'Magnification = {r["M"]:.4f}×',
            transform=ax.transAxes, fontsize=10, va='top',
            bbox=dict(boxstyle='round', fc='wheat', alpha=0.85))

    lim = max(sw, sh, br*3) * 1.2
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Height (mm)')
    ax.set_title('Sensor Footprint')
    ax.grid(True, ls='--', alpha=0.5)
    ax.legend(loc='lower right', fontsize=8)


# ── Main ──────────────────────────────────────────────────────────────────────
def create_visualization():
    idx_init = RELAY_FL.index(72.71)

    fig = plt.figure(figsize=(17, 8))
    gs  = GridSpec(1, 2, width_ratios=[1.1, 0.9], figure=fig)
    ax_rays   = fig.add_subplot(gs[0])
    ax_sensor = fig.add_subplot(gs[1])
    plt.subplots_adjust(left=0.05, bottom=0.22, right=0.97, top=0.90, wspace=0.15)

    # ── Sliders ───────────────────────────────────────────────────────────────
    ax_sf1 = plt.axes([0.15, 0.12, 0.70, 0.03], facecolor='lightyellow')
    ax_sod = plt.axes([0.15, 0.06, 0.70, 0.03], facecolor='lightyellow')
    ax_btn = plt.axes([0.02, 0.08, 0.07, 0.04])

    s_f1 = Slider(ax_sf1, 'Relay FL (mm)', 0, len(RELAY_FL)-1,
                  valinit=idx_init, valstep=1, valfmt='%0.0f')
    # Focal length labels under slider
    for i, fl in enumerate(RELAY_FL):
        ax_sf1.text(i/(len(RELAY_FL)-1), -1.1, f'{fl}mm',
                    transform=ax_sf1.transAxes, ha='center', fontsize=8)

    s_sod = Slider(ax_sod, 'L1 distance to mirror (in)', 1.0, 15.0,
                   valinit=4.0, valstep=0.1, valfmt='%.1f in')

    btn = Button(ax_btn, 'Reset', color='lightyellow')

    def update(val):
        idx      = int(round(s_f1.val))
        obj_dist = s_sod.val * 25.4
        r        = analyze(RELAY_FL[idx], obj_dist)
        draw_rays(ax_rays, r)
        draw_sensor(ax_sensor, r)
        fig.suptitle(f'FLIR Boson 640 — Relay f={RELAY_FL[idx]:.2f}mm | '
                     f'Mag={r["M"]:.4f}× | Beam={r["beam_px"]:.1f}px | '
                     f'Object={s_sod.val:.1f}in'
                     if r else 'FLIR Boson 640 — No valid solution', fontsize=11)
        fig.canvas.draw_idle()

    def reset(event):
        s_f1.set_val(idx_init)
        s_sod.set_val(4.0)
        r = analyze(RELAY_FL[idx_init], OBJECT_DIST_DEFAULT)
        draw_rays(ax_rays, r)
        draw_sensor(ax_sensor, r)
        fig.suptitle(f'FLIR Boson 640 — Relay f={RELAY_FL[idx_init]:.2f}mm | '
                     f'Mag={r["M"]:.4f}× | Beam={r["beam_px"]:.1f}px | Object={OBJECT_DIST_DEFAULT/25.4:.1f}in'
                     if r else 'FLIR Boson 640', fontsize=11)
        fig.canvas.draw_idle()

    s_f1.on_changed(update)
    s_sod.on_changed(update)
    btn.on_clicked(reset)

    # Initial draw with best solution
    r = analyze(RELAY_FL[idx_init], OBJECT_DIST_DEFAULT)
    draw_rays(ax_rays, r)
    draw_sensor(ax_sensor, r)
    fig.suptitle(f'FLIR Boson 640 — Relay f={RELAY_FL[idx_init]:.2f}mm | '
                 f'Mag={r["M"]:.4f}× | Beam={r["beam_px"]:.1f}px | Object={OBJECT_DIST_DEFAULT/25.4:.1f}in'
                 if r else 'FLIR Boson 640', fontsize=11)

    plt.show()

if __name__ == "__main__":
    create_visualization()