"""
Jerryy's AI Color Engine
Deterministic color harmonization, archetype recognition,
HEX-based palette synthesis, and WCAG contrast validation.
"""

import os
import re
import math
import colorsys
from typing import Dict, Any, List, Optional, Tuple

# WCAG Contrast Math
def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Converts #RGB or #RRGGBB to (r, g, b) 0-255."""
    h = hex_str.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    if len(h) != 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts r, g, b (0-255) to uppercase #RRGGBB."""
    r_c = max(0, min(255, int(round(r))))
    g_c = max(0, min(255, int(round(g))))
    b_c = max(0, min(255, int(round(b))))
    return f"#{r_c:02X}{g_c:02X}{b_c:02X}"

def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculates W3C relative luminance from sRGB values:
    L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
    """
    def channel_linear(val: int) -> float:
        c = val / 255.0
        return c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)

    r_lin = channel_linear(rgb[0])
    g_lin = channel_linear(rgb[1])
    b_lin = channel_linear(rgb[2])
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculates contrast ratio (L1 + 0.05) / (L2 + 0.05) where L1 >= L2."""
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = (lighter + 0.05) / (darker + 0.05)
    return round(ratio, 2)

def evaluate_wcag(ratio: float, is_large_text: bool = False) -> str:
    """Returns WCAG compliance level string."""
    if is_large_text:
        if ratio >= 4.5:
            return "AAA PASS"
        elif ratio >= 3.0:
            return "AA PASS"
        return "FAIL"
    else:
        if ratio >= 7.0:
            return "AAA PASS"
        elif ratio >= 4.5:
            return "AA PASS"
        elif ratio >= 3.0:
            return "AA LARGE PASS"
        return "FAIL"

def calculate_palette_contrast(colors: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calculates WCAG contrast metrics for key color roles."""
    role_map = {c['role'].lower(): c['hex'] for c in colors}
    bg = role_map.get('background', '#FFFFFF')
    surface = role_map.get('surface', '#F4F4F5')
    text = role_map.get('text', '#111827')
    primary = role_map.get('primary', '#2F69FF')

    text_bg_ratio = contrast_ratio(text, bg)
    text_surf_ratio = contrast_ratio(text, surface)
    white_pri_ratio = contrast_ratio('#FFFFFF', primary)
    black_pri_ratio = contrast_ratio('#000000', primary)

    return {
        "text_on_background": {
            "ratio": f"{text_bg_ratio}:1",
            "score": text_bg_ratio,
            "status": evaluate_wcag(text_bg_ratio)
        },
        "text_on_surface": {
            "ratio": f"{text_surf_ratio}:1",
            "score": text_surf_ratio,
            "status": evaluate_wcag(text_surf_ratio)
        },
        "white_on_primary": {
            "ratio": f"{white_pri_ratio}:1",
            "score": white_pri_ratio,
            "status": evaluate_wcag(white_pri_ratio, is_large_text=True)
        },
        "black_on_primary": {
            "ratio": f"{black_pri_ratio}:1",
            "score": black_pri_ratio,
            "status": evaluate_wcag(black_pri_ratio, is_large_text=True)
        }
    }

# Archetype Presets
PALETTE_PRESETS = {
    "fintech": {
        "name": "Midnight Ledger",
        "mood": ["professional", "trustworthy", "modern"],
        "reply": "A focused dark fintech system built on deep navy foundations, confident royal blue controls, and clear green financial accents.",
        "colors": [
            {"role": "background", "hex": "#080D1A", "usage": "Deep immersive application background"},
            {"role": "surface", "hex": "#111827", "usage": "Cards, table headers, and navigation panes"},
            {"role": "primary", "hex": "#2F69FF", "usage": "Primary action buttons and active toggles"},
            {"role": "secondary", "hex": "#38BDF8", "usage": "Data chart lines and secondary controls"},
            {"role": "accent", "hex": "#22C55E", "usage": "Positive movement and success badges"},
            {"role": "text", "hex": "#F8FAFC", "usage": "High-contrast readable typographic content"}
        ]
    },
    "healthcare": {
        "name": "Calm Sanitas",
        "mood": ["calm", "clinical", "accessible"],
        "reply": "A clean, clinical healthcare palette pairing tranquil slate-white backgrounds with soothing teal, trustworthy medical blue, and reassuring mint accents.",
        "colors": [
            {"role": "background", "hex": "#F8FAFC", "usage": "Serene, glare-free light background"},
            {"role": "surface", "hex": "#FFFFFF", "usage": "Patient records and diagnostic cards"},
            {"role": "primary", "hex": "#0EA5E9", "usage": "Primary scheduling and consultation actions"},
            {"role": "secondary", "hex": "#14B8A6", "usage": "Vitals charts and secondary navigation"},
            {"role": "accent", "hex": "#10B981", "usage": "Healthy indicators and confirmation states"},
            {"role": "text", "hex": "#0F172A", "usage": "Crisp, legible clinical text"}
        ]
    },
    "cyberpunk": {
        "name": "Neon Ronin",
        "mood": ["electric", "dystopian", "high-octane"],
        "reply": "An electric cyberpunk palette anchored in obsidian violet with incandescent magenta, cyber-cyan vectors, and vivid ultraviolet accents.",
        "colors": [
            {"role": "background", "hex": "#090014", "usage": "Deep obsidian abyss background"},
            {"role": "surface", "hex": "#16002D", "usage": "HUD frames, telemetry containers, and cards"},
            {"role": "primary", "hex": "#8B5CF6", "usage": "Main action buttons and weapon tiers"},
            {"role": "secondary", "hex": "#00F5FF", "usage": "Cyber optic shields and active reticles"},
            {"role": "accent", "hex": "#FF2BD6", "usage": "Critical health alerts and neon triggers"},
            {"role": "text", "hex": "#F8F7FF", "usage": "Luminous readable typography"}
        ]
    },
    "luxury": {
        "name": "Onyx & Champagne",
        "mood": ["exclusive", "prestigious", "understated"],
        "reply": "An ultra-premium minimal luxury system balancing warm satin blacks, ivory surfaces, muted bronze-gold accents, and delicate champagne typography.",
        "colors": [
            {"role": "background", "hex": "#0C0C0D", "usage": "Satin dark minimal background"},
            {"role": "surface", "hex": "#18181B", "usage": "Showcase pedestals and item cards"},
            {"role": "primary", "hex": "#D4AF37", "usage": "Signature luxury CTAs and cart triggers"},
            {"role": "secondary", "hex": "#E5E5E5", "usage": "Secondary editorial controls"},
            {"role": "accent", "hex": "#C5A059", "usage": "Limited edition badges and brand mark"},
            {"role": "text", "hex": "#FAFAF9", "usage": "Editorial typography with pristine legibility"}
        ]
    },
    "gaming": {
        "name": "Apex Overdrive",
        "mood": ["competitive", "aggressive", "tactical"],
        "reply": "A tactical gaming UI palette utilizing basalt armor tones, infrared assault red, and high-visibility amber accents.",
        "colors": [
            {"role": "background", "hex": "#0F1115", "usage": "Basalt armored HUD backdrop"},
            {"role": "surface", "hex": "#1B1E26", "usage": "Inventory slots and match statistics"},
            {"role": "primary", "hex": "#EF4444", "usage": "Deploy triggers and primary strike buttons"},
            {"role": "secondary", "hex": "#F59E0B", "usage": "Weapon loadouts and level badges"},
            {"role": "accent", "hex": "#FF3366", "usage": "Critical hit feedback and killfeed"},
            {"role": "text", "hex": "#F1F5F9", "usage": "High-visibility telemetry text"}
        ]
    },
    "saas": {
        "name": "Linear Horizon",
        "mood": ["efficient", "focused", "modern"],
        "reply": "A clean, modern SaaS color scheme crafted for prolonged focus, clear hierarchy, and frictionless interaction.",
        "colors": [
            {"role": "background", "hex": "#F8FAFC", "usage": "Clean distraction-free canvas"},
            {"role": "surface", "hex": "#FFFFFF", "usage": "Dashboard widgets and workflow pipelines"},
            {"role": "primary", "hex": "#4F46E5", "usage": "Primary conversion button and active tab"},
            {"role": "secondary", "hex": "#6366F1", "usage": "Filtering tags and secondary links"},
            {"role": "accent", "hex": "#06B6D4", "usage": "Interactive metrics and graph focus states"},
            {"role": "text", "hex": "#1E293B", "usage": "Sharp, comfortable interface text"}
        ]
    },
    "portfolio": {
        "name": "Studio Slate",
        "mood": ["minimal", "curated", "editorial"],
        "reply": "A refined monochromatic design portfolio palette letting visual work take center stage with tactile slate contrasts and an iconic cobalt accent.",
        "colors": [
            {"role": "background", "hex": "#F7FAFC", "usage": "Slate pearl gallery background"},
            {"role": "surface", "hex": "#FFFFFF", "usage": "Case study cards and lightbox viewports"},
            {"role": "primary", "hex": "#2F69FF", "usage": "Contact trigger and interactive links"},
            {"role": "secondary", "hex": "#71717A", "usage": "Project categorization labels"},
            {"role": "accent", "hex": "#0E2AC5", "usage": "Interactive micro-animations"},
            {"role": "text", "hex": "#0A0A0A", "usage": "Bold, editorial headline typography"}
        ]
    },
    "ai": {
        "name": "Quantum Neural",
        "mood": ["futuristic", "cerebral", "intelligent"],
        "reply": "A cerebral AI interface system combining midnight indigo, electric violet tokens, and vibrant cyan neural vectors.",
        "colors": [
            {"role": "background", "hex": "#0B0F19", "usage": "Deep computational space"},
            {"role": "surface", "hex": "#131C31", "usage": "Inference cards and model inspector panels"},
            {"role": "primary", "hex": "#6366F1", "usage": "Run prompt button and active node"},
            {"role": "secondary", "hex": "#06B6D4", "usage": "Token streaming and latency metrics"},
            {"role": "accent", "hex": "#A855F7", "usage": "Generation complete and creative spark"},
            {"role": "text", "hex": "#F8FAFC", "usage": "Comfortable terminal and code text"}
        ]
    },
    "ecommerce": {
        "name": "Warm Atelier",
        "mood": ["inviting", "warm", "conversion-focused"],
        "reply": "An inviting, warm lifestyle e-commerce palette with organic terracotta highlights, cream surfaces, and decisive checkout accents.",
        "colors": [
            {"role": "background", "hex": "#FAF8F5", "usage": "Warm linen background"},
            {"role": "surface", "hex": "#FFFFFF", "usage": "Product grid tiles and drawer menus"},
            {"role": "primary", "hex": "#D9532F", "usage": "Add to Cart and checkout buttons"},
            {"role": "secondary", "hex": "#8A6D56", "usage": "Variant selectors and breadcrumbs"},
            {"role": "accent", "hex": "#2A9D8F", "usage": "Free shipping pill and in-stock indicator"},
            {"role": "text", "hex": "#292524", "usage": "Warm charcoal descriptive typography"}
        ]
    },
    "nature": {
        "name": "Nordic Moss",
        "mood": ["organic", "restorative", "sustainable"],
        "reply": "An organic, restorative palette celebrating Nordic pines, sage undergrowth, soft parchment, and sunlit lichen accents.",
        "colors": [
            {"role": "background", "hex": "#F4F6F0", "usage": "Organic parchment background"},
            {"role": "surface", "hex": "#FFFFFF", "usage": "Article cards and sustainability metrics"},
            {"role": "primary", "hex": "#2D5A43", "usage": "Primary buttons and active filters"},
            {"role": "secondary", "hex": "#6B8E7D", "usage": "Supporting tags and botanical diagrams"},
            {"role": "accent", "hex": "#E09F3E", "usage": "Seasonal highlight and key statistic"},
            {"role": "text", "hex": "#1C2D24", "usage": "Forest charcoal legible body copy"}
        ]
    },
    "volt": {
        "name": "Volt Kinetic",
        "mood": ["energetic", "neon", "high-velocity"],
        "reply": "An intense neon volt palette set against slate obsidian for extreme visibility and athletic momentum.",
        "colors": [
            {"role": "background", "hex": "#0A0D0E", "usage": "Obsidian athletic backdrop"},
            {"role": "surface", "hex": "#161B1E", "usage": "Telemetry widgets and split time panels"},
            {"role": "primary", "hex": "#E1FC03", "usage": "Start workout and record lap action"},
            {"role": "secondary", "hex": "#94A3B8", "usage": "Secondary cadence indicators"},
            {"role": "accent", "hex": "#00F5FF", "usage": "Peak heart rate and speed alerts"},
            {"role": "text", "hex": "#F8FAFC", "usage": "Crisp digital display typography"}
        ]
    }
}

def generate_palette_from_hex(base_hex: str, prompt: str = "") -> Dict[str, Any]:
    """
    Intelligently derives a full harmonious UI palette from a single user-supplied HEX code.
    Uses HSL/HSV math to create complementary, analogous, and accessible backgrounds/surfaces.
    """
    rgb = hex_to_rgb(base_hex)
    r_norm = rgb[0] / 255.0
    g_norm = rgb[1] / 255.0
    b_norm = rgb[2] / 255.0

    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

    is_dark_preferred = any(w in prompt.lower() for w in ['dark', 'black', 'gaming', 'cyber', 'night', 'deep', 'oled'])

    # Derive Background & Surface
    if is_dark_preferred or l < 0.35:
        # Dark theme
        bg_rgb = colorsys.hls_to_rgb(h, 0.06, min(s * 0.3, 0.25))
        surface_rgb = colorsys.hls_to_rgb(h, 0.12, min(s * 0.35, 0.3))
        text_hex = "#F8FAFC"
    else:
        # Light theme
        bg_rgb = colorsys.hls_to_rgb(h, 0.97, min(s * 0.15, 0.2))
        surface_rgb = (1.0, 1.0, 1.0)
        text_hex = "#0F172A"

    # Secondary: Analogous (+30 deg)
    sec_h = (h + 30 / 360.0) % 1.0
    sec_rgb = colorsys.hls_to_rgb(sec_h, min(0.65, max(0.4, l)), s)

    # Accent: Complementary (+180 deg) or Split-Complementary (+150 deg)
    accent_h = (h + 150 / 360.0) % 1.0
    accent_rgb = colorsys.hls_to_rgb(accent_h, 0.55, max(0.7, s))

    norm_base = rgb_to_hex(rgb[0], rgb[1], rgb[2])
    bg_hex = rgb_to_hex(bg_rgb[0] * 255, bg_rgb[1] * 255, bg_rgb[2] * 255)
    surface_hex = rgb_to_hex(surface_rgb[0] * 255, surface_rgb[1] * 255, surface_rgb[2] * 255)
    sec_hex = rgb_to_hex(sec_rgb[0] * 255, sec_rgb[1] * 255, sec_rgb[2] * 255)
    accent_hex = rgb_to_hex(accent_rgb[0] * 255, accent_rgb[1] * 255, accent_rgb[2] * 255)

    colors = [
        {"role": "background", "hex": bg_hex, "usage": "Main view canvas and atmospheric backing"},
        {"role": "surface", "hex": surface_hex, "usage": "Cards, sheets, and elevated elements"},
        {"role": "primary", "hex": norm_base, "usage": f"Key brand color based on your {norm_base} anchor"},
        {"role": "secondary", "hex": sec_hex, "usage": "Harmonious analogous secondary interactive tone"},
        {"role": "accent", "hex": accent_hex, "usage": "Split-complementary highlight for peak contrast"},
        {"role": "text", "hex": text_hex, "usage": "Accessible readable typography"}
    ]

    contrast = calculate_palette_contrast(colors)

    return {
        "reply": f"Crafted a cohesive system anchored directly around your specified color {norm_base}. The secondary tone follows an analogous hue shift, with a split-complementary accent designed for prominent CTA visibility.",
        "palette": {
            "name": f"Harmonic {norm_base}",
            "mood": ["custom", "harmonized", "balanced"],
            "colors": colors,
            "contrast": contrast
        }
    }

def match_preset_intent(prompt: str) -> Optional[Dict[str, Any]]:
    """Matches query keywords against preset design archetypes."""
    q = prompt.lower()

    if any(k in q for k in ['fintech', 'finance', 'banking', 'crypto', 'wealth', 'trading', 'money', 'ledger']):
        return PALETTE_PRESETS['fintech']
    if any(k in q for k in ['health', 'med', 'clinic', 'calm', 'hospital', 'doctor', 'care', 'wellness', 'pharma']):
        return PALETTE_PRESETS['healthcare']
    if any(k in q for k in ['cyber', 'neon', 'punk', 'synthwave', 'futuristic neon']):
        return PALETTE_PRESETS['cyberpunk']
    if any(k in q for k in ['luxury', 'prestige', 'gold', 'vip', 'elegance', 'jewelry', 'champagne', 'exclusive']):
        return PALETTE_PRESETS['luxury']
    if any(k in q for k in ['game', 'gaming', 'esports', 'fps', 'rpg', 'overdrive', 'tactical']):
        return PALETTE_PRESETS['gaming']
    if any(k in q for k in ['saas', 'software', 'dashboard', 'b2b', 'platform', 'app', 'linear']):
        return PALETTE_PRESETS['saas']
    if any(k in q for k in ['portfolio', 'studio', 'agency', 'designer', 'minimalist', 'architect', 'creative']):
        return PALETTE_PRESETS['portfolio']
    if any(k in q for k in ['ai', 'neural', 'machine learning', 'gpt', 'intelligent', 'quantum', 'algorithm']):
        return PALETTE_PRESETS['ai']
    if any(k in q for k in ['shop', 'ecommerce', 'e-commerce', 'store', 'cart', 'retail', 'fashion', 'warm']):
        return PALETTE_PRESETS['ecommerce']
    if any(k in q for k in ['nature', 'eco', 'green', 'organic', 'forest', 'botanical', 'sustainable']):
        return PALETTE_PRESETS['nature']
    if any(k in q for k in ['volt', 'lime', 'energy', 'athletic', 'sport', 'fitness']):
        return PALETTE_PRESETS['volt']

    return None

def process_color_query(prompt: str) -> Dict[str, Any]:
    """
    Main entry point for local deterministic color synthesis.
    Checks for explicit HEX values, keyword intents, or generates a tailored harmonic theme.
    """
    # 1. Check for explicit HEX code
    hex_match = re.search(r'#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', prompt)
    if hex_match and ('#' in prompt or any(w in prompt.lower() for w in ['hex', 'color', 'match', 'matching'])):
        raw_hex = hex_match.group(1)
        if len(raw_hex) == 3:
            raw_hex = ''.join([c*2 for c in raw_hex])
        full_hex = f"#{raw_hex.upper()}"
        return generate_palette_from_hex(full_hex, prompt)

    # 2. Check for preset keyword match
    preset = match_preset_intent(prompt)
    if preset:
        colors = preset['colors']
        contrast = calculate_palette_contrast(colors)
        return {
            "reply": preset['reply'],
            "palette": {
                "name": preset['name'],
                "mood": preset['mood'],
                "colors": colors,
                "contrast": contrast
            }
        }

    # 3. Intelligent fallback based on general styling adjectives
    q = prompt.lower()
    is_dark = 'dark' in q or 'night' in q or 'black' in q
    if is_dark:
        preset = PALETTE_PRESETS['saas']
        # Convert to dark
        colors = [
            {"role": "background", "hex": "#0F172A", "usage": "Deep slate atmospheric backdrop"},
            {"role": "surface", "hex": "#1E293B", "usage": "Elevated cards and panels"},
            {"role": "primary", "hex": "#38BDF8", "usage": "Vibrant sky blue primary interaction"},
            {"role": "secondary", "hex": "#818CF8", "usage": "Indigo secondary accents"},
            {"role": "accent", "hex": "#34D399", "usage": "Positive and active telemetry"},
            {"role": "text", "hex": "#F8FAFC", "usage": "High-contrast clean content"}
        ]
        return {
            "reply": "Synthesized a dark-mode interface system offering high-contrast typography, deep slate container surfaces, and electric sky-blue accents.",
            "palette": {
                "name": "Slate Nocturne",
                "mood": ["focused", "dark", "tactile"],
                "colors": colors,
                "contrast": calculate_palette_contrast(colors)
            }
        }

    # Default fallback: Royal Studio (Jerryy's AI signature)
    default_colors = [
        {"role": "background", "hex": "#F7FAFC", "usage": "Clean white-slate canvas"},
        {"role": "surface", "hex": "#FFFFFF", "usage": "Elevated frosted glass panels and cards"},
        {"role": "primary", "hex": "#2F69FF", "usage": "Iconic royal blue primary CTA"},
        {"role": "secondary", "hex": "#0E2AC5", "usage": "Deep sapphire secondary links"},
        {"role": "accent", "hex": "#E1FC03", "usage": "Electrifying volt-lime micro-indicator"},
        {"role": "text", "hex": "#0A0A0A", "usage": "Crisp editorial text with peak contrast"}
    ]
    return {
        "reply": f"Built a versatile digital system for '{prompt}'. Grounded in clean white-slate ergonomics, vivid primary controls, and an energetic accent highlight.",
        "palette": {
            "name": "Jerryy's AI Royal",
            "mood": ["versatile", "refined", "impactful"],
            "colors": default_colors,
            "contrast": calculate_palette_contrast(default_colors)
        }
    }
