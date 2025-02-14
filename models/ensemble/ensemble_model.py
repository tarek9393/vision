"""Ensemble model that combines predictions from multiple models"""

import numpy as np
from typing import Any, Dict, List
import torch
from ..base_model import BaseVisionModel
from ..vgg.vgg_model import VGGModel
from ..resnet.resnet_model import ResNetModel
from ..yolo.yolo_model import YOLOModel

class EnsembleModel(BaseVisionModel):
    """Ensemble model that combines predictions from multiple models"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.models: List[BaseVisionModel] = []
        self.weights = config.get('model_weights', None)
        self.ensemble_method = config.get('ensemble_method', 'weighted_average')
        self._initialize_models(config)
        
    def _initialize_models(self, config: Dict[str, Any]) -> None:
        """Initialize individual models in the ensemble"""
        model_configs = config.get('models', [])
        
        for model_config in model_configs:
            model_type = model_config['type']
            if model_type == 'vgg':
                model = VGGModel(model_config)
            elif model_type == 'resnet':
                model = ResNetModel(model_config)
            elif model_type == 'yolo':
                model = YOLOModel(model_config)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
            model.load_model()
            self.models.append(model)
            
        if self.weights is None:
            self.weights = [1.0 / len(self.models)] * len(self.models)
        
    def load_model(self) -> None:
        """Load all models in the ensemble"""
        for model in self.models:
            model.load_model()
            
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for all models"""
        # Each model handles its own preprocessing
        return image
        
    def _combine_predictions(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine predictions from multiple models"""
        if self.ensemble_method == 'weighted_average':
            combined_probs = np.zeros_like(predictions[0]['probabilities'])
            for pred, weight in zip(predictions, self.weights):
                combined_probs += weight * pred['probabilities']
                
            class_id = np.argmax(combined_probs)
            confidence = combined_probs[class_id]
            
        elif self.ensemble_method == 'max_confidence':
            confidences = [pred['confidence'] for pred in predictions]
            max_conf_idx = np.argmax(confidences)
            return predictions[max_conf_idx]
            
        elif self.ensemble_method == 'voting':
            class_votes = {}
            for pred, weight in zip(predictions, self.weights):
                class_id = pred['class_id']
                votes = weight * pred['confidence']
                class_votes[class_id] = class_votes.get(class_id, 0) + votes
                
            class_id = max(class_votes.items(), key=lambda x: x[1])[0]
            confidence = class_votes[class_id] / sum(self.weights)
            combined_probs = np.mean([pred['probabilities'] for pred in predictions], axis=0)
            
        else:
            raise ValueError(f"Unsupported ensemble method: {self.ensemble_method}")
            
        return {
            'class_id': int(class_id),
            'confidence': float(confidence),
            'probabilities': combined_probs,
            'individual_predictions': predictions
        }
        
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Make predictions using all models in the ensemble"""
        predictions = []
        for model in self.models:
            pred = model.predict(image)
            predictions.append(pred)
            
        return self._combine_predictions(predictions)
        
    def train(self, train_data: Any, val_data: Any) -> None:
        """Train all models in the ensemble"""
        for i, model in enumerate(self.models):
            print(f"\nTraining model {i+1}/{len(self.models)}")
            model.train(train_data, val_data)
            
    def update_weights(self, new_weights: List[float]) -> None:
        """Update the weights for ensemble prediction"""
        if len(new_weights) != len(self.models):
            raise ValueError("Number of weights must match number of models")
        if not np.isclose(sum(new_weights), 1.0):
            raise ValueError("Weights must sum to 1.0")
        self.weights = new_weights
