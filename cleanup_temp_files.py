import os

# Archivos temporales que se pueden eliminar después de la configuración
temp_files = [
    'create_carousel_slides.py',
    'check_carousel.py',
    'create_placeholder_image.py'
]

print("=== LIMPIEZA DE ARCHIVOS TEMPORALES ===\n")

for file in temp_files:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"✓ Eliminado: {file}")
        except Exception as e:
            print(f"✗ Error eliminando {file}: {e}")
    else:
        print(f"- No encontrado: {file}")

print("\n¡Limpieza completada!")
print("\nEl sistema de carrusel está listo para usar:")
print("1. Ve al admin de Django: http://127.0.0.1:8000/admin/")
print("2. Busca la sección 'Slides del Carrusel'")
print("3. Agrega, edita o administra los slides")
print("4. Los cambios se reflejarán inmediatamente en la página principal")