"""
Script generador del icono oficial de la aplicación Gestión de Usuarios.
Crea app_icon.png y app_icon.ico con múltiples resoluciones (16, 24, 32, 48, 64, 128, 256).
"""

from pathlib import Path
from PIL import Image, ImageDraw

def create_user_management_icon():
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Fondo: Cuadrado con esquinas muy redondeadas (estilo Fluent / iOS moderno)
    pad = 12
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=54,
        fill=(15, 35, 60, 255),  # Azul marino corporativo (#0f233c)
        outline=(56, 189, 248, 220),  # Borde cian sutil
        width=5
    )

    # 2. Resplandor superior suave
    for i in range(15):
        alpha = int(35 - i * 2)
        if alpha > 0:
            draw.rounded_rectangle(
                [pad + i + 2, pad + i + 2, size - pad - i - 2, 110 - i * 3],
                radius=45,
                fill=(255, 255, 255, alpha)
            )

    # 3. Avatar de usuario estilizado (Blanco nítido)
    center_x = size // 2
    
    # Cabeza (Círculo)
    head_radius = 38
    head_cy = 92
    draw.ellipse(
        [center_x - head_radius, head_cy - head_radius, center_x + head_radius, head_cy + head_radius],
        fill=(255, 255, 255, 255)
    )

    # Torso (Hombros curvos elegantes)
    torso_top = 144
    torso_bottom = 212
    torso_w = 66
    draw.chord(
        [center_x - torso_w, torso_top, center_x + torso_w, torso_bottom + 40],
        start=180,
        end=360,
        fill=(255, 255, 255, 255)
    )

    # 4. Insignia lateral de gestión / verificación (Azul turquesa y blanco)
    badge_x = 192
    badge_y = 192
    badge_r = 28
    draw.ellipse(
        [badge_x - badge_r, badge_y - badge_r, badge_x + badge_r, badge_y + badge_r],
        fill=(14, 165, 233, 255),
        outline=(15, 35, 60, 255),
        width=4
    )
    # Checkmark blanco en la insignia
    draw.line([(badge_x - 12, badge_y), (badge_x - 4, badge_y + 9), (badge_x + 13, badge_y - 8)], fill=(255, 255, 255, 255), width=5)

    # Guardar versión PNG a 256x256
    png_path = assets_dir / "app_icon.png"
    img.save(png_path, format="PNG")
    print(f"Icono PNG creado: {png_path}")

    # Guardar versión ICO con todas las dimensiones estándar de Windows
    ico_path = assets_dir / "app_icon.ico"
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Icono ICO multipágina creado: {ico_path}")

if __name__ == "__main__":
    create_user_management_icon()
