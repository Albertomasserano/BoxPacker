import streamlit as st
import plotly.graph_objects as go
import math
import random

# --- Konfiguration ---
KISTE = (567, 366, 315)
RAND = 5
ABSTAND = 20
EXT_HEIGHT = 150

RINGE_DATEN = {
    "256W7225-1": (215.83, 36.1),
    "256W7625-1": (283.49, 48.73),
    "256W7227-1": (240.41, 97.49),
    "256W7425-1": (258.97, 45.8),
    "256W7427-1": (279.7, 114.37),
    "256W7525-1": (356.87, 69.05),
    "256W7527-1": (391.8, 140.85),
    "256W7627-1": (315.4, 126.12),
    "2240-0820": (165, 20.5),
    "2240-1310": (165, 38.5),
    "2241-0820": (204.5, 30.2),
    "2241-1310": (204.5, 47.6),
    "2389-0010": (194, 195),
    "2389-0050": (179.775, 41.8),
    "2389-0052": (179.775, 22.2),
    "4776-0050": (179.775, 41.5),
    "4776-0051": (191.4, 57.25),
    "4776-0052": (179.775, 23.6),
    "4776-0055": (191.4, 57.25),
    "4776-0057": (179.6, 23.4),
    "6882-1003 (E-Jet)": (165.1, 23.5),
    "6882-1004": (158.2, 22.3),
    "6882-1013": (165.04, 23.7),
    "6882-1014": (158, 22.3),
    "6884-1006 (E-Jet)": (165.1, 33.5),
    "6884-1007": (158, 32.3)
}

# --- Funktionen ---
def innere_maße(kiste, rand):
    L, B, H = kiste
    return L - 2*rand, B - 2*rand, H - 2*rand

def optimiere_achse(kiste, teil, rand, abstand, achse):
    inner_L, inner_B, inner_H = innere_maße(kiste, rand)
    p1, p2, ps = teil
    best = {'maße': (0,0,0), 'reihen': (0,0,0), 'gesamt': 0, 'uses_ext': False, 'H_tot': inner_H}
    for dims in [(p1, p2), (p2, p1)]:
        if achse == 'Z':
            continue
        elif achse == 'X':
            dx, dy, dz = ps, dims[0], dims[1]
        else:
            dx, dy, dz = dims[0], ps, dims[1]
        uses_ext = dz > inner_H
        H_tot = inner_H + (EXT_HEIGHT if uses_ext else 0)
        nx = math.floor((inner_L + abstand) / (dx + abstand))
        ny = math.floor((inner_B + abstand) / (dy + abstand))
        nz = 1
        total = nx * ny * nz
        if total > best['gesamt']:
            best = {
                'maße': (dx, dy, dz),
                'reihen': (nx, ny, nz),
                'gesamt': total,
                'uses_ext': uses_ext,
                'H_tot': H_tot,
                'achse': achse
            }
    return best

def berechne_beste_konfiguration(teil):
    konfigs = [optimiere_achse(KISTE, teil, RAND, ABSTAND, ax) for ax in ('X','Y')]
    return max(konfigs, key=lambda x: x['gesamt'])

def zeichne_kiste_plotly(cfg, ring_name=""):
    inner_L, inner_B, inner_H = innere_maße(KISTE, RAND)
    dx, dy, dz = cfg['maße']
    nx, ny, _ = cfg['reihen']
    uses_ext = cfg['uses_ext']
    H_tot = cfg['H_tot']

    fig = go.Figure()

    def crea_cubo(x0, y0, z0, dx, dy, dz, color, opacity, name=None, showlegend=False):
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        X = [x0,x1,x1,x0,x0,x1,x1,x0]
        Y = [y0,y0,y1,y1,y0,y0,y1,y1]
        Z = [z0,z0,z0,z0,z1,z1,z1,z1]
        faces = [
            (0,1,2), (0,2,3),
            (4,5,6), (4,6,7),
            (0,1,5), (0,5,4),
            (1,2,6), (1,6,5),
            (2,3,7), (2,7,6),
            (3,0,4), (3,4,7)
        ]
        i_faces, j_faces, k_faces = zip(*faces)
        fig.add_trace(go.Mesh3d(
            x=X, y=Y, z=Z,
            i=i_faces, j=j_faces, k=k_faces,
            opacity=opacity,
            color=color,
            flatshading=True,
            showscale=False,
            name=name if name else "",
            legendgroup=name,
            showlegend=showlegend
        ))
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        for e in edges:
            fig.add_trace(go.Scatter3d(
                x=[X[e[0]], X[e[1]]],
                y=[Y[e[0]], Y[e[1]]],
                z=[Z[e[0]], Z[e[1]]],
                mode='lines',
                line=dict(color='black', width=1),
                showlegend=False
            ))

    # Box esterno blu
    crea_cubo(0, 0, 0, inner_L, inner_B, H_tot, color='blue', opacity=0.1, name="Kiste", showlegend=True)

    # Ringe
    count = 1
    for i in range(nx):
        for j in range(ny):
            x0 = i * (dx + ABSTAND)
            y0 = j * (dy + ABSTAND)
            z0 = 0
            color = f"rgb({random.randint(50,255)}, {random.randint(50,255)}, {random.randint(50,255)})"
            crea_cubo(x0, y0, z0, dx, dy, dz, color=color, opacity=1, name=f"Ring {count}")
            count += 1

    # Estensione
    if uses_ext:
        crea_cubo(0, 0, inner_H, inner_L, inner_B, EXT_HEIGHT, color='lightgray', opacity=0.3, name="Extension", showlegend=True)

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title=dict(text=ring_name, x=0.5),
        legend=dict(x=0.85, y=0.95)
    )
    return fig

# --- Streamlit UI ---
st.set_page_config(layout="centered")
st.title("📦 Ring-Konfigurator")

with st.container():
    ring = st.selectbox("Ring auswählen", list(RINGE_DATEN.keys()))

if ring:
    d, h = RINGE_DATEN[ring]
    best_cfg = berechne_beste_konfiguration((d, d, h))
    fig = zeichne_kiste_plotly(best_cfg, ring)

    # Calcola legenda testuale
    nx, ny, _ = best_cfg['reihen']
    dx, dy, dz = best_cfg['maße']
    gesamt = best_cfg['gesamt']
    sep_kurz = max(0, ny + 1)
    sep_lang = max(0, nx + 1)
    achse = best_cfg['achse']
    axis_label = f"Ausrichtung: {'X' if achse == 'X' else 'Y'}-Achse"

    titel = (
        f"**{ring}**\n\n"
        f"{axis_label}  \n"
        f"Durchmesser: **{dx:.1f} mm**, Dicke: **{dz:.1f} mm**  \n"
        f"Reihen: X = **{nx}**, Y = **{ny}**  \n"
        f"**{gesamt} Ringe insgesamt**  \n"
        f"Kurztrenner: **{sep_lang}**, Langtrenner: **{sep_kurz}**"
    )
    st.markdown(titel)

    if best_cfg['uses_ext']:
        st.info("⚠️ Zusätzliche Höhe wird benötigt (EXT_HEIGHT)!")

    st.plotly_chart(fig, use_container_width=True)
