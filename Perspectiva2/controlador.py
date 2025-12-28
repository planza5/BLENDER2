"""
Controlador que ejecuta genera_habitacion.py en bucle,
analiza el resultado y ajusta parámetros hasta conseguir
5 intentos seguidos válidos.
"""
import subprocess
import json
import random
import time
import winsound
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


class RoomController:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.params_file = self.project_dir / "room_params.json"
        self.output_image = self.project_dir / "output.png"
        self.success_count = 0
        self.total_attempts = 0

    def generate_random_params(self):
        """Genera parámetros aleatorios para la habitación."""
        return {
            "room_width": random.uniform(3.0, 6.0),
            "room_depth": random.uniform(3.0, 6.0),
            "room_height": random.uniform(2.2, 3.5),
            # Cámara en una esquina (entre 0.15 y 0.45)
            "cam_x_ratio": random.uniform(0.15, 0.45),
            "cam_y_ratio": random.uniform(0.15, 0.45),
            "cam_z_ratio": random.uniform(0.4, 0.7),
            # Target en esquina opuesta (entre 0.55 y 0.85)
            "target_x_ratio": random.uniform(0.55, 0.85),
            "target_y_ratio": random.uniform(0.55, 0.85),
            "target_z_ratio": random.uniform(0.4, 0.6),
            "fov": random.randint(60, 85),
            "bg_strength": random.uniform(0.6, 1.2),
            "light_energy": random.randint(250, 450)
        }

    def adjust_params(self, params, reason):
        """Ajusta parámetros basándose en el fallo detectado."""
        print(f"  Ajustando parámetros: {reason}")

        if "exterior" in reason or "negro" in reason:
            # Si se ve el exterior, reducir FOV y ajustar cámara más hacia adentro
            params["fov"] = max(50, params["fov"] - 5)
            params["cam_x_ratio"] = min(0.45, params["cam_x_ratio"] + 0.05)
            params["cam_y_ratio"] = min(0.45, params["cam_y_ratio"] + 0.05)

        if "uniones" in reason or "bordes" in reason:
            # Si no se ven uniones, aumentar FOV o ajustar ángulo
            params["fov"] = min(90, params["fov"] + 3)
            params["target_z_ratio"] = random.uniform(0.3, 0.7)

        if "oscuro" in reason or "uniforme" in reason:
            params["bg_strength"] = min(2.0, params["bg_strength"] + 0.3)
            params["light_energy"] = min(800, params["light_energy"] + 100)

        return params

    def save_params(self, params):
        """Guarda parámetros en JSON."""
        with open(self.params_file, 'w') as f:
            json.dump(params, f, indent=2)

    def run_blender(self):
        """Ejecuta Blender con el script."""
        cmd = [
            "blender",
            "--background",
            "--python",
            str(self.project_dir / "genera_habitacion.py")
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return result.returncode == 0

    def analyze_image(self):
        """
        Analiza la imagen para verificar que cumple los requisitos:
        - Solo se ve el interior (no píxeles negros/muy oscuros)
        - Se ven uniones de paredes
        - Se ven uniones techo-paredes
        - Se ven uniones suelo-paredes

        Returns:
            (bool, str): (es_válida, razón_fallo)
        """
        if not self.output_image.exists():
            return False, "Imagen no generada"

        img = Image.open(self.output_image)
        img_array = np.array(img)

        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array

        # 1. Verificar que no hay píxeles muy oscuros (exterior)
        # Umbral: menos del 5% de píxeles con brillo < 30
        dark_pixels = np.sum(gray < 30)
        dark_ratio = dark_pixels / gray.size

        if dark_ratio > 0.05:
            return False, f"Se ve exterior/negro ({dark_ratio*100:.1f}% píxeles oscuros)"

        # 2. Detectar bordes para verificar uniones
        img_pil = Image.fromarray(gray.astype(np.uint8))
        edges = img_pil.filter(ImageFilter.FIND_EDGES)
        edges_array = np.array(edges)

        # Dividir imagen en regiones para verificar uniones
        h, w = edges_array.shape

        # Región superior (20% superior) - debe tener bordes (techo-pared)
        top_region = edges_array[:int(h*0.2), :]
        top_edges = np.sum(top_region > 30)

        # Región inferior (20% inferior) - debe tener bordes (suelo-pared)
        bottom_region = edges_array[int(h*0.8):, :]
        bottom_edges = np.sum(bottom_region > 30)

        # Regiones laterales (20% izq/der) - deben tener bordes (unión paredes)
        left_region = edges_array[:, :int(w*0.2)]
        left_edges = np.sum(left_region > 30)

        right_region = edges_array[:, int(w*0.8):]
        right_edges = np.sum(right_region > 30)

        # Verificar que hay suficientes bordes en cada región
        min_edges = 30  # Mínimo de píxeles de borde por región (reducido para habitaciones simples)

        if top_edges < min_edges:
            return False, "No se ve unión techo-pared suficiente"

        if bottom_edges < min_edges:
            return False, "No se ve unión suelo-pared suficiente"

        if left_edges < min_edges and right_edges < min_edges:
            return False, "No se ven suficientes uniones de paredes laterales"

        # 3. Verificar variación de brillo (debe haber contraste)
        brightness_std = np.std(gray)
        brightness_mean = np.mean(gray)

        if brightness_std < 8:
            return False, "Imagen demasiado uniforme/oscura"

        # Verificar que no esté completamente oscura
        if brightness_mean < 40:
            return False, "Imagen demasiado oscura"

        # Todo OK
        return True, "Válida"

    def beep(self):
        """Emite un beep sonoro."""
        # Beep a 1000Hz durante 500ms
        winsound.Beep(1000, 500)
        time.sleep(0.2)
        winsound.Beep(1200, 500)
        time.sleep(0.2)
        winsound.Beep(1400, 800)

    def run(self):
        """Ejecuta el bucle principal."""
        print("="*60)
        print("CONTROLADOR DE GENERACIÓN DE HABITACIONES")
        print("="*60)
        print("Objetivo: 5 intentos válidos consecutivos\n")

        params = self.generate_random_params()

        while self.success_count < 5:
            self.total_attempts += 1

            print(f"\n[Intento #{self.total_attempts}] Éxitos consecutivos: {self.success_count}/5")

            # Guardar parámetros
            self.save_params(params)

            # Ejecutar Blender
            print("  Ejecutando Blender...")
            if not self.run_blender():
                print("  ❌ Error al ejecutar Blender")
                params = self.generate_random_params()
                continue

            # Analizar resultado
            print("  Analizando imagen...")
            is_valid, reason = self.analyze_image()

            if is_valid:
                self.success_count += 1
                print(f"  OK VALIDA! ({reason}) - Racha: {self.success_count}/5")

                if self.success_count < 5:
                    # Generar nuevos parámetros para siguiente intento
                    params = self.generate_random_params()
            else:
                print(f"  XX FALLO: {reason}")
                self.success_count = 0  # Reiniciar contador

                # Ajustar parámetros basándose en el fallo
                params = self.adjust_params(params, reason)

            # Pequeña pausa para no saturar
            time.sleep(0.5)

        # ¡Éxito! 5 seguidos
        print("\n" + "="*60)
        print("*** OBJETIVO CONSEGUIDO! ***")
        print(f"5 intentos validos consecutivos en {self.total_attempts} intentos totales")
        print("="*60 + "\n")

        print("Emitiendo beep...")
        self.beep()
        print("OK Completado!")


if __name__ == "__main__":
    controller = RoomController()
    controller.run()
