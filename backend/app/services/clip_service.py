"""
CLIP service for video scene analysis and matching
"""
import clip
import torch
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
from app.models.summary import SceneData
from config import get_settings, SUMMARIZATION_CATEGORIES
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class CLIPService:
    """Service for CLIP embeddings and scene matching"""
    
    def __init__(self):
        self.model = None
        self.preprocess = None
        self.device = None
        
    def load_clip_model(self) -> bool:
        """Load CLIP model once on startup"""
        try:
            if self.model is not None:
                return True
                
            logger.info(f"Loading CLIP model: {settings.CLIP_MODEL_NAME}")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load(settings.CLIP_MODEL_NAME, device=self.device)
            logger.info(f"CLIP model loaded on device: {self.device}")
            return True
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            return False
    
    def extract_frame_embeddings(self, frames: List[Tuple[float, np.ndarray]]) -> List[Tuple[float, np.ndarray]]:
        """
        Extract embeddings for video frames
        
        Args:
            frames: List of (timestamp, frame_array) tuples
            
        Returns:
            List of (timestamp, embedding) tuples
        """
        if not self.model:
            self.load_clip_model()
        
        embeddings = []
        
        try:
            for timestamp, frame in frames:
                # Convert numpy array to PIL Image
                if frame.shape[0] == 3:  # If channels first
                    frame = np.transpose(frame, (1, 2, 0))
                
                # Ensure uint8 format
                if frame.dtype != np.uint8:
                    frame = (frame * 255).astype(np.uint8)
                
                # Convert to RGB if needed
                if frame.shape[2] == 4:  # RGBA
                    frame = frame[:, :, :3]
                
                image = Image.fromarray(frame)
                
                # Preprocess and get embedding
                image_input = self.preprocess(image).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    image_features = self.model.encode_image(image_input)
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                embedding = image_features.cpu().numpy().flatten()
                embeddings.append((timestamp, embedding))
                
            logger.info(f"Extracted {len(embeddings)} frame embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error extracting frame embeddings: {e}")
            raise
    
    def compute_text_embedding(self, text: str) -> np.ndarray:
        """
        Compute embedding for text prompt
        
        Args:
            text: Text prompt
            
        Returns:
            Text embedding as numpy array
        """
        if not self.model:
            self.load_clip_model()
        
        try:
            text_input = clip.tokenize([text]).to(self.device)
            
            with torch.no_grad():
                text_features = self.model.encode_text(text_input)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Error computing text embedding: {e}")
            raise
    
    def find_matching_scenes(
        self, 
        frame_embeddings: List[Tuple[float, np.ndarray]], 
        text_embedding: np.ndarray,
        threshold: Optional[float] = None,
        matched_text: Optional[str] = None
    ) -> List[SceneData]:
        """
        Find frames matching text prompt
        
        Args:
            frame_embeddings: List of (timestamp, embedding) tuples
            text_embedding: Text embedding to match against
            threshold: Similarity threshold (default from settings)
            matched_text: Text that was matched (for SceneData)
            
        Returns:
            List of SceneData objects for matching scenes
        """
        if threshold is None:
            threshold = settings.SCENE_SIMILARITY_THRESHOLD
        
        matching_scenes = []
        
        try:
            # Calculate similarities
            similarities = []
            for timestamp, frame_embedding in frame_embeddings:
                similarity = np.dot(frame_embedding, text_embedding)
                similarities.append((timestamp, similarity))
            
            # Group consecutive matching frames into scenes
            current_scene_start = None
            current_scene_end = None
            scene_scores = []
            
            for timestamp, similarity in similarities:
                if similarity >= threshold:
                    if current_scene_start is None:
                        current_scene_start = timestamp
                        current_scene_end = timestamp
                        scene_scores = [similarity]
                    else:
                        current_scene_end = timestamp
                        scene_scores.append(similarity)
                else:
                    if current_scene_start is not None:
                        # End of scene
                        avg_score = np.mean(scene_scores)
                        duration = current_scene_end - current_scene_start
                        
                        scene = SceneData(
                            start_time=current_scene_start,
                            end_time=current_scene_end,
                            duration=duration,
                            confidence_score=float(avg_score),
                            matched_text=matched_text
                        )
                        matching_scenes.append(scene)
                        
                        current_scene_start = None
                        current_scene_end = None
                        scene_scores = []
            
            # Handle last scene if still open
            if current_scene_start is not None:
                avg_score = np.mean(scene_scores)
                duration = current_scene_end - current_scene_start
                
                scene = SceneData(
                    start_time=current_scene_start,
                    end_time=current_scene_end,
                    duration=duration,
                    confidence_score=float(avg_score),
                    matched_text=matched_text
                )
                matching_scenes.append(scene)
            
            logger.info(f"Found {len(matching_scenes)} matching scenes")
            return matching_scenes
            
        except Exception as e:
            logger.error(f"Error finding matching scenes: {e}")
            raise
    
    def match_category_scenes(
        self, 
        frame_embeddings: List[Tuple[float, np.ndarray]], 
        category: str
    ) -> List[SceneData]:
        """
        Match scenes to preset category
        
        Args:
            frame_embeddings: List of (timestamp, embedding) tuples
            category: Category name
            
        Returns:
            List of SceneData objects for matching scenes
        """
        if category not in SUMMARIZATION_CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        
        category_description = SUMMARIZATION_CATEGORIES[category]
        text_embedding = self.compute_text_embedding(category_description)
        
        scenes = self.find_matching_scenes(
            frame_embeddings, 
            text_embedding,
            matched_text=category
        )
        
        # Update matched_category
        for scene in scenes:
            scene.matched_category = category
        
        return scenes
    
    def select_best_scenes(
        self, 
        scenes: List[SceneData], 
        target_duration: Optional[int] = None
    ) -> List[SceneData]:
        """
        Select key scenes to fit target duration
        
        Args:
            scenes: List of SceneData objects
            target_duration: Target duration in seconds (default from settings)
            
        Returns:
            Selected scenes sorted by start time
        """
        if target_duration is None:
            target_duration = settings.TARGET_SUMMARY_DURATION_SECONDS
        
        if not scenes:
            return []
        
        # Sort scenes by confidence score (descending)
        sorted_scenes = sorted(scenes, key=lambda s: s.confidence_score, reverse=True)
        
        # Select scenes until we reach target duration
        selected_scenes = []
        total_duration = 0
        
        for scene in sorted_scenes:
            if total_duration + scene.duration <= target_duration:
                selected_scenes.append(scene)
                total_duration += scene.duration
            elif total_duration < target_duration:
                # Trim the last scene to fit
                remaining = target_duration - total_duration
                if remaining > 1.0:  # Only add if at least 1 second
                    trimmed_scene = SceneData(
                        start_time=scene.start_time,
                        end_time=scene.start_time + remaining,
                        duration=remaining,
                        confidence_score=scene.confidence_score,
                        matched_text=scene.matched_text,
                        matched_category=scene.matched_category
                    )
                    selected_scenes.append(trimmed_scene)
                break
        
        # Sort selected scenes by start time for proper playback
        selected_scenes.sort(key=lambda s: s.start_time)
        
        logger.info(f"Selected {len(selected_scenes)} scenes, total duration: {sum(s.duration for s in selected_scenes):.2f}s")
        return selected_scenes
    
    def calculate_scene_importance(self, scenes: List[SceneData]) -> List[SceneData]:
        """
        Score scenes by importance (already done via confidence_score)
        
        Args:
            scenes: List of SceneData objects
            
        Returns:
            Same list (confidence_score is already the importance metric)
        """
        return scenes


# Global instance
clip_service = CLIPService()
