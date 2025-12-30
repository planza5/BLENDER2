#!/bin/bash
# Añade Blender al PATH para la sesión actual y futuras

BLENDER_PATH="/workspace/blender"

# Añadir al PATH de la sesión actual
export PATH="$BLENDER_PATH:$PATH"

# Añadir a .bashrc para sesiones futuras (si no está ya)
if ! grep -q "$BLENDER_PATH" ~/.bashrc 2>/dev/null; then
    echo "export PATH=\"$BLENDER_PATH:\$PATH\"" >> ~/.bashrc
    echo "✓ Blender añadido a ~/.bashrc"
fi

# Verificar
if command -v blender &> /dev/null; then
    echo "✓ Blender disponible: $(blender --version | head -1)"
else
    echo "✗ Error: Blender no encontrado en $BLENDER_PATH"
fi
