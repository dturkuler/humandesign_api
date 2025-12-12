import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from matplotlib.colors import to_rgba
import matplotlib.transforms
from svgpath2mpl import parse_path
import json
import numpy as np

import io
import os

# --- 1. CONFIGURATION ---
LAYOUT_FILE = "layout_data.json"
OUTPUT_FILE = "bodygraph_output.png"

# Colors
COLOR_DEFINED = "#D4AF37"  # Gold-ish for defined centers
COLOR_UNDEFINED = "#FFFFFF" # Pure White
COLOR_STROKE = "black"
COLOR_RED = "#DC143C"      # Crimson
COLOR_BLACK = "black"
COLOR_BODY_BG = "#E6E6E6"  # Darker gray vertical background for better contrast with white centers

# Canvas Size (Matched to XAML ViewBox/Canvas)
# XAML Canvas is 240x320. 
CANVAS_W = 240
CANVAS_H = 320

def load_json_layout():
    # Use absolute path relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, LAYOUT_FILE)
    with open(path, 'r') as f:
        return json.load(f)

def svg_to_mpl_path(svg_d):
    """Converts an SVG path string 'd' to a Matplotlib Path object."""
    if not svg_d:
        return None
    # svgpath2mpl works great usually.
    return parse_path(svg_d)

def draw_chart(chart_data, layout_data):
    # Setup Figure conforming to the aspect ratio
    fig, ax = plt.subplots(figsize=(8, 10.6), dpi=150) # Approx 240x320 ratio
    ax.set_xlim(0, CANVAS_W)
    ax.set_ylim(CANVAS_H, 0) # Flip Y axis because SVG/Canvas is top-left origin
    ax.axis('off')
    
    # 1. DRAW BODY OUTLINE
    body_d = layout_data.get('body_outline', "")
    if body_d:
        path = svg_to_mpl_path(body_d)
        patch = patches.PathPatch(path, facecolor=COLOR_BODY_BG, edgecolor='black', linewidth=0.8, zorder=0)
        ax.add_patch(patch)

    # 2. PREPARE DATA
    defined_centers = set(chart_data['general'].get('defined_centers', []))
    # Typo correction
    if "Anja" in defined_centers: 
        defined_centers.remove("Anja")
        defined_centers.add("Ajna")
        
    design_gates = {g['Gate']: g for g in chart_data['gates']['des']['Planets']}
    personality_gates = {g['Gate']: g for g in chart_data['gates']['prs']['Planets']}
    
    # 3. DRAW CHANNELS / GATES
    # The XAML logic draws *half channels* (gates) separately.
    # If Chart[Gate] is active, we draw that gate's stub.
    # If the *Channel* is formed, both stubs meet.
    # We iterate 1..64
    
    channels_layout = layout_data.get('channels', {})
    
    for gate_id_str, geo_data in channels_layout.items():
        gate_id = int(gate_id_str)
        
        path_d = geo_data.get('channel_path')
        if not path_d: continue
        mpl_path = svg_to_mpl_path(path_d)
        
        # 1. Always Draw Gray Background (Inactive state)
        # Matches the provided image style where all paths are visible in light gray/dark gray
        patch_bg = patches.PathPatch(mpl_path, facecolor='none', edgecolor="#D3D3D3", linewidth=4, capstyle='round', zorder=0.5)
        ax.add_patch(patch_bg)

        # Check activation
        is_design = gate_id in design_gates
        is_personality = gate_id in personality_gates
        
        if not (is_design or is_personality):
            continue
            
        z_order = 1
        
        if is_design and is_personality:
            # Draw Red base
            patch_red = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_RED, linewidth=4, capstyle='round', zorder=z_order)
            ax.add_patch(patch_red)
            # Draw Black stripe
            patch_blk = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_BLACK, linewidth=4, linestyle=(0, (3, 3)), capstyle='round', zorder=z_order+0.1)
            ax.add_patch(patch_blk)
        elif is_design:
            patch = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_RED, linewidth=4, capstyle='round', zorder=z_order)
            ax.add_patch(patch)
        elif is_personality:
            patch = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_BLACK, linewidth=4, capstyle='round', zorder=z_order)
            ax.add_patch(patch)

    # 4. DRAW CENTERS (On top of channels)
    centers_layout = layout_data.get('centers', {})
    
    # Map generic names to XAML keys if needed. 
    # Our extract script used keys like "Head", "Ajna", "Throat", "G", "Heart", "Sacral", "SolarPlexus", "Spleen", "Root".
    # User JSON has "G_Center". XAML uses "G".
    name_map = {
        "G_Center": "G",
        "Anja": "Ajna"
    }
    
    for name, data in centers_layout.items():
        # Determine if defined
        # Check mapped name in layout vs JSON
        json_name = name
        # Reverse map for checking definition
        if name == "G": json_name = "G_Center"
        
        is_defined = json_name in defined_centers or name in defined_centers
        
        fill_c = COLOR_DEFINED if is_defined else COLOR_UNDEFINED
        stroke_c = "gold" if is_defined else "gray" # Matches XAML style roughly
        if not is_defined: stroke_c = "gray"
        else: stroke_c = "#B8860B" # DarkGoldenRod for better visibility than 'Gold'
        
        z_order = 10
        
        if data['type'] == 'rect':
            # X/Y in XAML Canvas are Top-Left
            rect = patches.Rectangle((data['x'], data['y']), data['w'], data['h'], 
                                     linewidth=2, edgecolor=stroke_c, facecolor=fill_c, zorder=z_order)
            ax.add_patch(rect)
        elif data['type'] == 'path':
            path = svg_to_mpl_path(data['path'])
            patch = patches.PathPatch(path, facecolor=fill_c, edgecolor=stroke_c, linewidth=2, zorder=z_order)
            
            # Apply Transform if present
            transform_str = data.get('transform')
            if transform_str:
                # Parse "m11 m12 m21 m22 dx dy"
                # XAML: M11, M12, M21, M22, OffsetX, OffsetY
                # MPL Affine2D.from_values(a, b, c, d, e, f) matches this order: a=M11, b=M12...
                t_vals = [float(v) for v in transform_str.split()]
                if len(t_vals) == 6:
                    t = matplotlib.transforms.Affine2D.from_values(*t_vals)
                    # We must add the patch's transform to the data transform (ax.transData)
                    patch.set_transform(t + ax.transData)
            
            ax.add_patch(patch)

    # 5. DRAW GATE NUMBERS
    gate_coords = layout_data.get('gates_coords', {})
    
    # We should iterate through all 64 gates to display them
    for gate_id_str, pt in gate_coords.items():
        gate_id = int(gate_id_str)
        x, y = pt['x'], pt['y']
        
        # Check if gate is active to highlight? 
        is_active = (gate_id in design_gates) or (gate_id in personality_gates)
        
        # Circle background for number
        # XAML Gate Template uses a small Ellipse 6.5x6.5
        # We'll draw a small circle
        
        circle_color = "gainsboro" if is_active else "none" # Highlight active gates? XAML logic: 'IsActive' -> Fill 'Transparent' else... wait.
        # XAML Logic: If NOT active -> Fill Transparent. If mouse over -> Gainsboro.
        # So inactive gates are just numbers. Active gates... actually usually in HD charts, the number is circled if active.
        # Let's circle active gates.
        
        if is_active:
            circ = patches.Circle((x + 3, y + 3), radius=3.5, facecolor='white', edgecolor='purple', linewidth=0.5, alpha=0.8, zorder=20)
            ax.add_patch(circ)
        
        # Text
        # The XAML coordinates (Canvas.Left/Top) are for the top-left of the button/control.
        # We want to center the text approx +3, +3
        ax.text(x + 3.2, y + 4.5, str(gate_id), fontsize=4, ha='center', va='center', zorder=21, color='black', fontfamily='sans-serif')

    # 6. SIDE PANELS (Planets) - Optional but good for completeness
    # Draw simple lists on left/right outside the canvas w/ clipping off? 
    # Current setup is 240x320. Side panels would need more width.
    # Let's keep it simple and just draw the chart as requested.
    
    # 6. SIDE PANELS (Planets) - Optional but good for completeness
    # Draw simple lists on left/right outside the canvas w/ clipping off? 
    # Current setup is 240x320. Side panels would need more width.
    # Let's keep it simple and just draw the chart as requested.
    
    return fig

def generate_bodygraph_image(chart_data, fmt='png'):
    """
    Generates the BodyGraph image and returns it as whitespace-trimmed bytes.
    fmt: 'png', 'svg', 'jpg', 'jpeg'
    """
    layout = load_json_layout()
    fig = draw_chart(chart_data, layout)
    
    buf = io.BytesIO()
    
    # JPG does not support transparency
    use_transparent = True
    if fmt.lower() in ['jpg', 'jpeg']:
        use_transparent = False
        # Optional: Set background to white explicitly if strictly needed, 
        # but matplotlib defaults to white usually.
        fig.patch.set_facecolor('white')

    fig.savefig(buf, format=fmt, bbox_inches='tight', pad_inches=0.1, transparent=use_transparent)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
    
# --- EXECUTION ---
if __name__ == "__main__":
    # Test Data
    json_data = """
{
  "general": {
    "birth_date": "(1968, 2, 21, 11, 0)",
    "create_date": "(1967, 11, 26, 17, 14)",
    "energie_type": "Manifesting Generator",
    "strategy": "Wait to Respond",
    "signature": "Satisfaction",
    "not_self": "Frustration & Anger",
    "aura": "Open & Enveloping",
    "inner_authority": "Solar Plexus",
    "inc_cross": "The Right Angle Cross of the Sleeping Phoenix (1)",
    "profile": "2/4: Hermit Opportunist",
    "defined_centers": [
      "Heart",
      "Throat",
      "G_Center",
      "Root",
      "Sacral",
      "SolarPlexus",
      "Spleen"
    ],
    "undefined_centers": [
      "Anja",
      "Head"
    ],
    "split": "Single Definition",
    "variables": {
      "right_up": "right",
      "right_down": "left",
      "left_up": "right",
      "left_down": "right"
    }
  },
  "gates": {
    "prs": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 331.75753719941173,
          "Gate": 55,
          "Line": 2,
          "Color": 5,
          "Tone": 3,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Earth",
          "Lon": 151.75753719941173,
          "Gate": 59,
          "Line": 2,
          "Color": 5,
          "Tone": 3,
          "Base": 4,
          "Ch_Gate": 6
        },
        {
          "Planet": "Moon",
          "Lon": 244.2310066060069,
          "Gate": 34,
          "Line": 5,
          "Color": 3,
          "Tone": 2,
          "Base": 4,
          "Ch_Gate": 20
        },
        {
          "Planet": "North_Node",
          "Lon": 19.86214145569654,
          "Gate": 51,
          "Line": 6,
          "Color": 1,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 25
        },
        {
          "Planet": "South_Node",
          "Lon": 199.86214145569653,
          "Gate": 57,
          "Line": 6,
          "Color": 1,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 34
        },
        {
          "Planet": "Mercury",
          "Lon": 320.0165669655236,
          "Gate": 49,
          "Line": 2,
          "Color": 2,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 301.3880299909544,
          "Gate": 60,
          "Line": 6,
          "Color": 3,
          "Tone": 1,
          "Base": 3,
          "Ch_Gate": 3
        },
        {
          "Planet": "Mars",
          "Lon": 3.209266367962246,
          "Gate": 25,
          "Line": 6,
          "Color": 2,
          "Tone": 5,
          "Base": 3,
          "Ch_Gate": 51
        },
        {
          "Planet": "Jupiter",
          "Lon": 150.7621456594904,
          "Gate": 59,
          "Line": 1,
          "Color": 5,
          "Tone": 1,
          "Base": 3,
          "Ch_Gate": 6
        },
        {
          "Planet": "Saturn",
          "Lon": 10.109142964480705,
          "Gate": 21,
          "Line": 1,
          "Color": 4,
          "Tone": 6,
          "Base": 2,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 178.23219618103448,
          "Gate": 6,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 2,
          "Ch_Gate": 59
        },
        {
          "Planet": "Neptune",
          "Lon": 236.52059882399786,
          "Gate": 14,
          "Line": 3,
          "Color": 1,
          "Tone": 6,
          "Base": 3,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 172.0592318541099,
          "Gate": 47,
          "Line": 6,
          "Color": 3,
          "Tone": 3,
          "Base": 2,
          "Ch_Gate": 0
        }
      ]
    },
    "des": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 243.75753719926954,
          "Gate": 34,
          "Line": 4,
          "Color": 6,
          "Tone": 2,
          "Base": 3,
          "Ch_Gate": 20
        },
        {
          "Planet": "Earth",
          "Lon": 63.757537199269564,
          "Gate": 20,
          "Line": 4,
          "Color": 6,
          "Tone": 2,
          "Base": 3,
          "Ch_Gate": 57
        },
        {
          "Planet": "Moon",
          "Lon": 175.54009086572225,
          "Gate": 6,
          "Line": 4,
          "Color": 1,
          "Tone": 4,
          "Base": 5,
          "Ch_Gate": 59
        },
        {
          "Planet": "North_Node",
          "Lon": 27.398443914748626,
          "Gate": 3,
          "Line": 2,
          "Color": 1,
          "Tone": 4,
          "Base": 2,
          "Ch_Gate": 60
        },
        {
          "Planet": "South_Node",
          "Lon": 207.3984439147486,
          "Gate": 50,
          "Line": 2,
          "Color": 1,
          "Tone": 4,
          "Base": 2,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mercury",
          "Lon": 226.7428052951088,
          "Gate": 1,
          "Line": 4,
          "Color": 5,
          "Tone": 3,
          "Base": 1,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 198.03426226579404,
          "Gate": 57,
          "Line": 4,
          "Color": 1,
          "Tone": 4,
          "Base": 4,
          "Ch_Gate": 34
        },
        {
          "Planet": "Mars",
          "Lon": 296.05678504320747,
          "Gate": 61,
          "Line": 6,
          "Color": 4,
          "Tone": 6,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Jupiter",
          "Lon": 154.80087449484986,
          "Gate": 59,
          "Line": 5,
          "Color": 6,
          "Tone": 6,
          "Base": 3,
          "Ch_Gate": 6
        },
        {
          "Planet": "Saturn",
          "Lon": 5.792372444524146,
          "Gate": 17,
          "Line": 3,
          "Color": 1,
          "Tone": 2,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 178.5293431806214,
          "Gate": 46,
          "Line": 1,
          "Color": 2,
          "Tone": 5,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Neptune",
          "Lon": 234.44073840486212,
          "Gate": 43,
          "Line": 6,
          "Color": 6,
          "Tone": 4,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 172.62001351206544,
          "Gate": 47,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        }
      ]
    }
  },
  "channels": {
    "Channels": [
      {
        "channel": "6/59: The Channel of Mating (A Design Focused on Reproduction)"
      },
      {
        "channel": "20/34: The Channel of Charisma (A Design of Thoughts Becoming Deeds)"
      },
      {
        "channel": "25/51: The Channel of Initiation (A Design of Needing to be First)"
      },
      {
        "channel": "34/57: The Channel of Power (A Design of an Archetype)"
      },
      {
        "channel": "3/60: The Channel of Mutation (Energy that Generates and Initiates)"
      },
      {
        "channel": "20/57: The Channel of the Brainwave (A Design of Penetrating Awareness)"
      }
    ]
  }
}
"""
    
    chart = json.loads(json_data)
    layout = load_json_layout()
    fig = draw_chart(chart, layout)
    fig.savefig(OUTPUT_FILE, bbox_inches='tight', pad_inches=0.1, transparent=True)
    fig.savefig(OUTPUT_FILE.replace('.png', '.svg'), bbox_inches='tight', pad_inches=0.1, transparent=True)
    print(f"Chart saved to {OUTPUT_FILE} and {OUTPUT_FILE.replace('.png', '.svg')}")