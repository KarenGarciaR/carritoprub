from PIL import Image, ImageDraw, ImageFont
import os

# Crear directorio si no existe
placeholder_dir = "static/images"
os.makedirs(placeholder_dir, exist_ok=True)

# Crear imagen placeholder
width, height = 800, 400
image = Image.new('RGB', (width, height), '#e9ecef')

# Crear objeto para dibujar
draw = ImageDraw.Draw(image)

# Dibujar texto
text = "Imagen no disponible"
try:
    # Intentar usar una fuente más grande
    font = ImageFont.truetype("arial.ttf", 24)
except:
    # Si no encuentra la fuente, usar la predeterminada
    font = ImageFont.load_default()

# Obtener el tamaño del texto
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Calcular posición para centrar el texto
x = (width - text_width) // 2
y = (height - text_height) // 2

# Dibujar el texto
draw.text((x, y), text, fill='#6c757d', font=font)

# Guardar la imagen
placeholder_path = os.path.join(placeholder_dir, 'carousel_placeholder.jpg')
image.save(placeholder_path, 'JPEG', quality=85)

print(f"Imagen placeholder creada: {placeholder_path}")