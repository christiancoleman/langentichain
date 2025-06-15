"""
AdaptiveClassifier implementation for LoRA-based routing
Based on AgenticSeek's approach using DistilBERT embeddings
"""

import os
import json
import torch
import numpy as np
from typing import List, Tuple, Dict, Optional
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from safetensors import safe_open
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AdaptiveConfig:
    """Configuration for AdaptiveClassifier"""
    model_name: str = "distilbert/distilbert-base-cased"
    embedding_dim: int = 768
    max_length: int = 512
    similarity_threshold: float = 0.7
    min_confidence: float = 0.1
    neural_weight: float = 0.2
    prototype_weight: float = 0.8
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class AdaptiveClassifier:
    """
    Adaptive classifier using DistilBERT embeddings and few-shot learning
    Compatible with AgenticSeek's LoRA-based routing approach
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = AdaptiveConfig()
        self.examples = {"texts": [], "labels": [], "embeddings": []}
        self.label_to_id = {}
        self.id_to_label = {}
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        
        # Initialize model and tokenizer
        logger.info(f"Loading model: {self.config.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModel.from_pretrained(self.config.model_name)
        self.model.to(self.config.device)
        self.model.eval()
        
        # Initialize label mappings
        self.initialize_labels()
    
    def initialize_labels(self):
        """Initialize default label mappings"""
        # Default labels for complexity estimation
        self.label_to_id = {"HIGH": 0, "LOW": 1}
        self.id_to_label = {0: "HIGH", 1: "LOW"}
        
        # Default labels for task classification
        self.task_labels = ["talk", "web", "code", "files", "mcp"]
        for i, label in enumerate(self.task_labels):
            self.label_to_id[label] = i + 2
            self.id_to_label[i + 2] = label
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        config_file = os.path.join(config_path, "config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                data = json.load(f)
                if "model_name" in data:
                    self.config.model_name = data["model_name"]
                if "embedding_dim" in data:
                    self.config.embedding_dim = data["embedding_dim"]
                if "label_to_id" in data:
                    self.label_to_id = data["label_to_id"]
                if "id_to_label" in data:
                    self.id_to_label = {int(k): v for k, v in data["id_to_label"].items()}
                    
                # Load config parameters
                if "config" in data:
                    config_params = data["config"]
                    for key, value in config_params.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
    
    @classmethod
    def from_pretrained(cls, path: str) -> 'AdaptiveClassifier':
        """Load a pretrained classifier"""
        classifier = cls(config_path=path)
        
        # Load saved examples if available
        examples_file = os.path.join(path, "examples.json")
        if os.path.exists(examples_file):
            with open(examples_file, 'r') as f:
                examples_data = json.load(f)
                classifier.load_examples(examples_data)
        
        # Load safetensors if available
        safetensors_file = os.path.join(path, "model.safetensors")
        if os.path.exists(safetensors_file):
            classifier.load_safetensors(safetensors_file)
        
        return classifier
    
    def load_safetensors(self, filepath: str):
        """Load embeddings from safetensors file"""
        logger.info(f"Loading safetensors from: {filepath}")
        
        # This would normally load the safetensors file
        # For now, we'll skip this as it requires the actual file
        # In production, you would use:
        # with safe_open(filepath, framework="pt", device=self.config.device) as f:
        #     for key in f.keys():
        #         tensor = f.get_tensor(key)
        #         # Process tensor as needed
        pass
    
    def load_examples(self, examples_data: List[Dict]):
        """Load examples from data"""
        for example in examples_data:
            if "embedding" in example and "label" in example and "text" in example:
                self.examples["texts"].append(example["text"])
                self.examples["labels"].append(example["label"])
                self.examples["embeddings"].append(torch.tensor(example["embedding"]))
    
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode text to embedding using DistilBERT"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=self.config.max_length,
            truncation=True,
            padding=True
        ).to(self.config.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use CLS token embedding
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()
        
        return embedding
    
    def add_examples(self, texts: List[str], labels: List[str]):
        """Add few-shot examples"""
        logger.info(f"Adding {len(texts)} examples")
        
        for text, label in zip(texts, labels):
            # Encode text to embedding
            embedding = self.encode_text(text)
            
            self.examples["texts"].append(text)
            self.examples["labels"].append(label)
            self.examples["embeddings"].append(embedding)
            
            # Update label mappings if needed
            if label not in self.label_to_id:
                new_id = len(self.label_to_id)
                self.label_to_id[label] = new_id
                self.id_to_label[new_id] = label
    
    def compute_similarity(self, embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
        """Compute cosine similarity between embeddings"""
        similarity = F.cosine_similarity(
            embedding1.unsqueeze(0), 
            embedding2.unsqueeze(0)
        ).item()
        return similarity
    
    def predict(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Predict label for text using few-shot learning"""
        if not self.examples["embeddings"]:
            # No examples, return default
            return [("LOW", 0.5)]
        
        # Encode input text
        query_embedding = self.encode_text(text)
        
        # Compute similarities with all examples
        similarities = []
        for i, example_embedding in enumerate(self.examples["embeddings"]):
            similarity = self.compute_similarity(query_embedding, example_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Aggregate predictions by label
        label_scores = {}
        total_weight = 0
        
        for idx, similarity in similarities[:top_k]:
            if similarity >= self.config.similarity_threshold:
                label = self.examples["labels"][idx]
                weight = similarity
                
                if label not in label_scores:
                    label_scores[label] = 0
                label_scores[label] += weight
                total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for label in label_scores:
                label_scores[label] /= total_weight
        else:
            # No similar examples found, use default
            return [("LOW", self.config.min_confidence)]
        
        # Sort by score
        predictions = [(label, score) for label, score in label_scores.items()]
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Ensure minimum confidence
        if predictions and predictions[0][1] < self.config.min_confidence:
            predictions[0] = (predictions[0][0], self.config.min_confidence)
        
        return predictions
    
    def save(self, path: str):
        """Save the classifier configuration and examples"""
        os.makedirs(path, exist_ok=True)
        
        # Save config
        config_data = {
            "model_name": self.config.model_name,
            "embedding_dim": self.config.embedding_dim,
            "label_to_id": self.label_to_id,
            "id_to_label": self.id_to_label,
            "config": {
                "max_length": self.config.max_length,
                "similarity_threshold": self.config.similarity_threshold,
                "min_confidence": self.config.min_confidence,
                "neural_weight": self.config.neural_weight,
                "prototype_weight": self.config.prototype_weight
            }
        }
        
        with open(os.path.join(path, "config.json"), 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Save examples
        examples_data = []
        for i in range(len(self.examples["texts"])):
            examples_data.append({
                "text": self.examples["texts"][i],
                "label": self.examples["labels"][i],
                "embedding": self.examples["embeddings"][i].cpu().tolist()
            })
        
        with open(os.path.join(path, "examples.json"), 'w') as f:
            json.dump(examples_data, f, indent=2)
        
        logger.info(f"Classifier saved to {path}")
