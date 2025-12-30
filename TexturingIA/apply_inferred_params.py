"""
Aplicador de Parámetros Inferidos a Blender
===========================================

Este script carga un modelo entrenado, infiere parámetros de una imagen
de textura real, y los aplica al material de microcemento en Blender.

Uso desde línea de comandos:
    blender --background --python apply_inferred_params.py -- \
        --checkpoint /path/to/best.pth \
        --dataset /path/to/dataset \
        --image /path/to/real_texture.jpg \
        --output /path/to/output.blend

Uso desde Blender (editar las rutas abajo):
    1. Abre Blender
    2. Ve a Scripting
    3. Abre este archivo
    4. Edita PATHS
    5. Run Script
"""

import sys
import json
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN - EDITAR ESTAS RUTAS SI USAS DESDE BLENDER
# =============================================================================

PATHS = {
    "checkpoint": "/path/to/checkpoints/best.pth",
    "dataset": "/path/to/microcemento_dataset",
    "image": "/path/to/real_texture.jpg",
    "output_blend": "/path/to/output.blend"  # Opcional
}

# =============================================================================
# IMPORTS CONDICIONALES
# =============================================================================

try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    print("Este script debe ejecutarse dentro de Blender")

try:
    import torch
    from torchvision import transforms, models
    from PIL import Image
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch no disponible. Instalar con: pip install torch torchvision pillow")


# =============================================================================
# MODELO (duplicado del script de entrenamiento para standalone)
# =============================================================================

if TORCH_AVAILABLE:
    class MicrocementoNet(nn.Module):
        def __init__(self, num_params: int, backbone: str = "efficientnet_b0"):
            super().__init__()
            self.num_params = num_params
            
            if backbone == "efficientnet_b0":
                self.backbone = models.efficientnet_b0(weights=None)
                num_features = self.backbone.classifier[1].in_features
                self.backbone.classifier = nn.Identity()
            elif backbone == "resnet34":
                self.backbone = models.resnet34(weights=None)
                num_features = self.backbone.fc.in_features
                self.backbone.fc = nn.Identity()
            
            self.head = nn.Sequential(
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, num_params),
                nn.Sigmoid()
            )
        
        def forward(self, x):
            features = self.backbone(x)
            return self.head(features)


# =============================================================================
# INFERENCIA
# =============================================================================

def load_model_and_metadata(checkpoint_path: str, dataset_path: str, device: str = "cuda"):
    """Carga el modelo y los rangos de parámetros."""
    
    # Metadata
    with open(Path(dataset_path) / "dataset.json", 'r') as f:
        data = json.load(f)
    param_ranges = data["parameters_ranges"]
    param_names = list(param_ranges.keys())
    
    # Modelo
    model = MicrocementoNet(num_params=len(param_names))
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    
    return model, param_ranges, param_names


def infer_parameters(model, image_path: str, param_ranges: dict, param_names: list, device: str = "cuda"):
    """Infiere los parámetros de una imagen."""
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        normalized = model(image)[0].cpu().numpy()
    
    # Denormalizar
    params = {}
    for i, name in enumerate(param_names):
        min_val = param_ranges[name]["min"]
        max_val = param_ranges[name]["max"]
        params[name] = float(normalized[i] * (max_val - min_val) + min_val)
    
    return params


# =============================================================================
# CREACIÓN Y APLICACIÓN EN BLENDER
# =============================================================================

def create_microcemento_material():
    """Crea el material de microcemento (igual que en el generador)."""
    
    mat = bpy.data.materials.get("Microcemento_Inferred")
    if mat:
        bpy.data.materials.remove(mat)
    
    mat = bpy.data.materials.new(name="Microcemento_Inferred")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Coordenadas
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    # Ruido base
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-600, 200)
    noise_base.name = "NoiseBase"
    links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])
    
    # Wave (llana)
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-600, -100)
    wave.name = "WaveLlana"
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.wave_profile = 'SIN'
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    
    # Mix ruido + wave
    mix_noise_wave = nodes.new('ShaderNodeMixRGB')
    mix_noise_wave.location = (-300, 100)
    mix_noise_wave.name = "MixNoiseWave"
    mix_noise_wave.blend_type = 'OVERLAY'
    links.new(noise_base.outputs['Fac'], mix_noise_wave.inputs['Color1'])
    links.new(wave.outputs['Fac'], mix_noise_wave.inputs['Color2'])
    
    # Voronoi
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-600, -400)
    voronoi.name = "VoronoiManchas"
    voronoi.feature = 'SMOOTH_F1'
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    
    # Mix voronoi
    mix_voronoi = nodes.new('ShaderNodeMixRGB')
    mix_voronoi.location = (-100, 0)
    mix_voronoi.name = "MixVoronoi"
    mix_voronoi.blend_type = 'SOFT_LIGHT'
    links.new(mix_noise_wave.outputs['Color'], mix_voronoi.inputs['Color1'])
    links.new(voronoi.outputs['Distance'], mix_voronoi.inputs['Color2'])
    
    # Color Ramp
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (150, 0)
    ramp.name = "ColorRamp"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements.new(1.0)
    links.new(mix_voronoi.outputs['Color'], ramp.inputs['Fac'])
    
    # BSDF y output
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (450, 0)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (700, 0)
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def apply_parameters_to_material(mat, params: dict):
    """Aplica los parámetros inferidos al material."""
    nodes = mat.node_tree.nodes
    
    # Ruido base
    noise = nodes["NoiseBase"]
    noise.inputs['Scale'].default_value = params["noise_scale"]
    noise.inputs['Detail'].default_value = params["noise_detail"]
    noise.inputs['Roughness'].default_value = params["noise_roughness"]
    
    # Wave
    wave = nodes["WaveLlana"]
    wave.inputs['Scale'].default_value = params["wave_scale"]
    wave.inputs['Distortion'].default_value = params["wave_distortion"]
    wave.inputs['Detail'].default_value = params["wave_detail"]
    
    # Mix wave
    mix_wave = nodes["MixNoiseWave"]
    mix_wave.inputs['Fac'].default_value = params["wave_intensity"]
    
    # Voronoi
    voronoi = nodes["VoronoiManchas"]
    voronoi.inputs['Scale'].default_value = params["voronoi_scale"]
    
    # Mix voronoi
    mix_voronoi = nodes["MixVoronoi"]
    mix_voronoi.inputs['Fac'].default_value = params["voronoi_intensity"]
    
    # Color ramp
    ramp = nodes["ColorRamp"]
    
    v1 = params["color1_value"]
    w1 = params["color1_warmth"]
    ramp.color_ramp.elements[0].color = (v1 + w1, v1, v1 - w1 * 0.5, 1.0)
    
    v_mid = (params["color1_value"] + params["color2_value"]) / 2
    w_mid = (params["color1_warmth"] + params["color2_warmth"]) / 2
    ramp.color_ramp.elements[1].color = (v_mid + w_mid, v_mid, v_mid - w_mid * 0.5, 1.0)
    ramp.color_ramp.elements[1].position = params["ramp_midpoint"]
    
    v2 = params["color2_value"]
    w2 = params["color2_warmth"]
    ramp.color_ramp.elements[2].color = (v2 + w2, v2, v2 - w2 * 0.5, 1.0)
    
    print("\n✓ Parámetros aplicados al material:")
    for name, value in params.items():
        print(f"  {name}: {value:.4f}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Flujo principal: cargar modelo, inferir, aplicar a Blender."""
    
    if not IN_BLENDER:
        print("Error: Este script debe ejecutarse dentro de Blender")
        return
    
    if not TORCH_AVAILABLE:
        print("Error: PyTorch no está disponible")
        print("Instalar: pip install torch torchvision pillow")
        return
    
    # Parsear argumentos si viene de línea de comandos
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--checkpoint", required=True)
        parser.add_argument("--dataset", required=True)
        parser.add_argument("--image", required=True)
        parser.add_argument("--output", default=None)
        args = parser.parse_args(argv)
        
        checkpoint_path = args.checkpoint
        dataset_path = args.dataset
        image_path = args.image
        output_path = args.output
    else:
        # Usar configuración manual
        checkpoint_path = PATHS["checkpoint"]
        dataset_path = PATHS["dataset"]
        image_path = PATHS["image"]
        output_path = PATHS.get("output_blend")
    
    # Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    # Cargar modelo
    print(f"\nCargando modelo desde {checkpoint_path}")
    model, param_ranges, param_names = load_model_and_metadata(
        checkpoint_path, dataset_path, device
    )
    
    # Inferir parámetros
    print(f"Infiriendo parámetros de {image_path}")
    params = infer_parameters(model, image_path, param_ranges, param_names, device)
    
    # Crear y configurar material
    print("\nCreando material en Blender...")
    mat = create_microcemento_material()
    apply_parameters_to_material(mat, params)
    
    # Asignar a objeto activo si existe
    if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
        obj = bpy.context.active_object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        print(f"\n✓ Material asignado a: {obj.name}")
    
    # Guardar .blend si se especificó
    if output_path:
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"✓ Archivo guardado: {output_path}")
    
    print("\n" + "="*50)
    print("¡Listo! El material está configurado con los parámetros inferidos.")
    print("="*50)


if __name__ == "__main__":
    main()
