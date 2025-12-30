"""
Entrenamiento de Red Neuronal para Inferencia de Parámetros de Microcemento
==========================================================================

Entrena una CNN que recibe una imagen de textura y predice los parámetros
del shader procedural de Blender.

Uso:
    python train_microcemento.py --dataset /path/to/dataset --epochs 100

Requisitos:
    pip install torch torchvision pillow tqdm tensorboard
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from tqdm import tqdm
import numpy as np

# =============================================================================
# DATASET
# =============================================================================

class MicrocementoDataset(Dataset):
    """Dataset de texturas de microcemento con sus parámetros."""
    
    def __init__(self, dataset_path: str, transform=None):
        self.dataset_path = Path(dataset_path)
        self.images_dir = self.dataset_path / "images"
        self.transform = transform
        
        # Cargar metadata
        with open(self.dataset_path / "dataset.json", 'r') as f:
            data = json.load(f)
        
        self.samples = data["samples"]
        self.param_ranges = data["parameters_ranges"]
        self.param_names = list(self.param_ranges.keys())
        self.num_params = len(self.param_names)
        
        print(f"Dataset cargado: {len(self.samples)} muestras, {self.num_params} parámetros")
    
    def normalize_params(self, params: Dict) -> torch.Tensor:
        """Normaliza los parámetros al rango [0, 1] para el entrenamiento."""
        normalized = []
        for name in self.param_names:
            value = params[name]
            min_val = self.param_ranges[name]["min"]
            max_val = self.param_ranges[name]["max"]
            norm = (value - min_val) / (max_val - min_val)
            normalized.append(norm)
        return torch.tensor(normalized, dtype=torch.float32)
    
    def denormalize_params(self, normalized: torch.Tensor) -> Dict:
        """Convierte parámetros normalizados de vuelta a valores reales."""
        params = {}
        for i, name in enumerate(self.param_names):
            min_val = self.param_ranges[name]["min"]
            max_val = self.param_ranges[name]["max"]
            params[name] = normalized[i].item() * (max_val - min_val) + min_val
        return params
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Cargar imagen
        img_path = self.images_dir / sample["filename"]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        # Normalizar parámetros
        params = self.normalize_params(sample["parameters"])
        
        return image, params


# =============================================================================
# MODELO
# =============================================================================

class MicrocementoNet(nn.Module):
    """
    Red neuronal para inferir parámetros de textura procedural.
    
    Usa un backbone preentrenado (EfficientNet) con una cabeza de regresión
    personalizada para predecir los N parámetros del shader.
    """
    
    def __init__(self, num_params: int, backbone: str = "efficientnet_b0"):
        super().__init__()
        
        self.num_params = num_params
        
        # Backbone preentrenado
        if backbone == "efficientnet_b0":
            self.backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
            num_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        elif backbone == "resnet34":
            self.backbone = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        else:
            raise ValueError(f"Backbone no soportado: {backbone}")
        
        # Cabeza de regresión
        self.head = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_params),
            nn.Sigmoid()  # Output en [0, 1] para parámetros normalizados
        )
    
    def forward(self, x):
        features = self.backbone(x)
        return self.head(features)


# =============================================================================
# ENTRENAMIENTO
# =============================================================================

class Trainer:
    """Gestor de entrenamiento con logging y checkpoints."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = "cuda",
        lr: float = 1e-4,
        output_dir: str = "./checkpoints"
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.criterion = nn.MSELoss()
        self.optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        self.best_val_loss = float('inf')
        self.history = {"train_loss": [], "val_loss": []}
    
    def train_epoch(self) -> float:
        """Entrena una época y devuelve la loss media."""
        self.model.train()
        total_loss = 0.0
        
        pbar = tqdm(self.train_loader, desc="Training")
        for images, params in pbar:
            images = images.to(self.device)
            params = params.to(self.device)
            
            self.optimizer.zero_grad()
            predictions = self.model(images)
            loss = self.criterion(predictions, params)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})
        
        return total_loss / len(self.train_loader)
    
    @torch.no_grad()
    def validate(self) -> Tuple[float, Dict]:
        """Valida el modelo y devuelve métricas."""
        self.model.eval()
        total_loss = 0.0
        all_errors = []
        
        for images, params in tqdm(self.val_loader, desc="Validating"):
            images = images.to(self.device)
            params = params.to(self.device)
            
            predictions = self.model(images)
            loss = self.criterion(predictions, params)
            total_loss += loss.item()
            
            # Error absoluto por parámetro
            errors = torch.abs(predictions - params).mean(dim=0).cpu().numpy()
            all_errors.append(errors)
        
        avg_loss = total_loss / len(self.val_loader)
        avg_errors = np.mean(all_errors, axis=0)
        
        return avg_loss, avg_errors
    
    def save_checkpoint(self, epoch: int, val_loss: float, is_best: bool = False):
        """Guarda checkpoint del modelo."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "val_loss": val_loss,
            "history": self.history
        }
        
        # Guardar último
        torch.save(checkpoint, self.output_dir / "last.pth")
        
        # Guardar mejor
        if is_best:
            torch.save(checkpoint, self.output_dir / "best.pth")
            print(f"  ✓ Nuevo mejor modelo guardado (val_loss: {val_loss:.4f})")
    
    def train(self, epochs: int):
        """Entrena el modelo durante N épocas."""
        print(f"\nIniciando entrenamiento por {epochs} épocas")
        print(f"Device: {self.device}")
        print(f"Output: {self.output_dir}\n")
        
        for epoch in range(epochs):
            print(f"\n{'='*60}")
            print(f"Época {epoch + 1}/{epochs}")
            print('='*60)
            
            # Train
            train_loss = self.train_epoch()
            self.history["train_loss"].append(train_loss)
            
            # Validate
            val_loss, param_errors = self.validate()
            self.history["val_loss"].append(val_loss)
            
            # Scheduler
            self.scheduler.step(val_loss)
            
            # Logging
            print(f"\n  Train Loss: {train_loss:.4f}")
            print(f"  Val Loss:   {val_loss:.4f}")
            print(f"  Error medio por parámetro: {param_errors.mean():.4f}")
            
            # Checkpoint
            is_best = val_loss < self.best_val_loss
            if is_best:
                self.best_val_loss = val_loss
            self.save_checkpoint(epoch, val_loss, is_best)
        
        print(f"\n{'='*60}")
        print("Entrenamiento completado")
        print(f"Mejor val_loss: {self.best_val_loss:.4f}")
        print('='*60)


# =============================================================================
# INFERENCIA
# =============================================================================

class MicrocementoInference:
    """Clase para inferir parámetros de nuevas imágenes."""
    
    def __init__(self, checkpoint_path: str, dataset_path: str, device: str = "cuda"):
        self.device = device
        
        # Cargar metadata del dataset para normalización
        with open(Path(dataset_path) / "dataset.json", 'r') as f:
            data = json.load(f)
        self.param_ranges = data["parameters_ranges"]
        self.param_names = list(self.param_ranges.keys())
        
        # Cargar modelo
        self.model = MicrocementoNet(num_params=len(self.param_names))
        checkpoint = torch.load(checkpoint_path, map_location=device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(device)
        self.model.eval()
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def denormalize_params(self, normalized: torch.Tensor) -> Dict:
        """Convierte parámetros normalizados a valores reales."""
        params = {}
        normalized = normalized.cpu().numpy()
        for i, name in enumerate(self.param_names):
            min_val = self.param_ranges[name]["min"]
            max_val = self.param_ranges[name]["max"]
            params[name] = float(normalized[i] * (max_val - min_val) + min_val)
        return params
    
    @torch.no_grad()
    def predict(self, image_path: str) -> Dict:
        """Predice los parámetros para una imagen."""
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        prediction = self.model(image)[0]
        return self.denormalize_params(prediction)
    
    @torch.no_grad()
    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """Predice los parámetros para múltiples imágenes."""
        images = []
        for path in image_paths:
            image = Image.open(path).convert('RGB')
            images.append(self.transform(image))
        
        batch = torch.stack(images).to(self.device)
        predictions = self.model(batch)
        
        return [self.denormalize_params(pred) for pred in predictions]


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Entrenar modelo de microcemento")
    parser.add_argument("--dataset", type=str, required=True, help="Ruta al dataset")
    parser.add_argument("--epochs", type=int, default=100, help="Número de épocas")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--backbone", type=str, default="efficientnet_b0", 
                        choices=["efficientnet_b0", "resnet34"])
    parser.add_argument("--output", type=str, default="./checkpoints", help="Directorio de salida")
    parser.add_argument("--device", type=str, default="cuda", help="Device (cuda/cpu)")
    args = parser.parse_args()
    
    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(90),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Dataset y split
    full_dataset = MicrocementoDataset(args.dataset, transform=train_transform)
    
    train_size = int(0.9 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size]
    )
    
    # Aplicar transform de validación al subset de validación
    val_dataset.dataset.transform = val_transform
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    
    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")
    
    # Modelo
    model = MicrocementoNet(num_params=full_dataset.num_params, backbone=args.backbone)
    
    # Entrenar
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=args.device,
        lr=args.lr,
        output_dir=args.output
    )
    
    trainer.train(args.epochs)


if __name__ == "__main__":
    main()
