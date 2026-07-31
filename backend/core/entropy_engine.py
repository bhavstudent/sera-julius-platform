import math
import random
import logging
from collections import deque, defaultdict
from datetime import datetime
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger("sera.entropy_engine")

class EntropyEngine:
    """
    AXIOM-Φ Entropy Analysis Engine.
    Maintains a sliding window of events per entity and computes Shannon entropy.
    Detects entropy spikes that signal a behavioral state transition.
    """

    def __init__(self, window_size: int = 50, alert_threshold: float = 2.0, 
                 entropy_alert_threshold: float = 1.1):
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        self.entropy_alert_threshold = entropy_alert_threshold
        
        # Each entity gets its own event type deque
        self.entity_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
        # Track historical entropy mean and variance for z-score computation
        self.entity_entropy_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        
        # Cache for computed entropy values to avoid recalculation
        self._entropy_cache: Dict[str, Tuple[float, float]] = {}  # entity_id -> (entropy, timestamp)
        self._cache_ttl: float = 0.5  # Cache TTL in seconds
        
        # Track total events processed
        self.total_events_processed: int = 0
        self.alerts_triggered: int = 0

    def ingest(self, entity_id: str, event_type: str, protocol: str) -> dict:
        """
        Ingest one event signal and return updated entropy metrics.
        Returns a dict with entropy score, z_score, and whether an alert was triggered.
        """
        if not entity_id:
            logger.warning("[ENTROPY] ingest called with empty entity_id")
            return {
                "entropy": 0.0,
                "z_score": 0.0,
                "alert_triggered": False,
                "window_size": 0,
                "error": "Missing entity_id"
            }
        
        signal = f"{protocol}:{event_type}"
        self.entity_windows[entity_id].append(signal)
        
        entropy = self._compute_entropy(entity_id)
        z_score = self._compute_z_score(entity_id, entropy)
        self.entity_entropy_history[entity_id].append(entropy)
        
        # Alert conditions
        z_score_alert = abs(z_score) > self.alert_threshold
        entropy_alert = entropy > self.entropy_alert_threshold
        alert_triggered = z_score_alert or entropy_alert
        
        # Update statistics
        self.total_events_processed += 1
        if alert_triggered:
            self.alerts_triggered += 1
        
        # Invalidate cache
        self._entropy_cache.pop(entity_id, None)
        
        return {
            "entropy": round(entropy, 4),
            "z_score": round(z_score, 4),
            "alert_triggered": alert_triggered,
            "alert_reason": self._get_alert_reason(z_score_alert, entropy_alert, entropy, z_score),
            "window_size": len(self.entity_windows[entity_id]),
        }

    def _get_alert_reason(self, z_score_alert: bool, entropy_alert: bool, entropy: float, z_score: float) -> str:
        """Get human-readable alert reason."""
        reasons = []
        if z_score_alert:
            reasons.append(f"Z-score spike ({z_score:.2f} > {self.alert_threshold})")
        if entropy_alert:
            reasons.append(f"High entropy ({entropy:.2f} > {self.entropy_alert_threshold})")
        return ", ".join(reasons) if reasons else "No alert"

    def _compute_entropy(self, entity_id: str) -> float:
        """Compute Shannon entropy for an entity's event window with caching."""
        window = self.entity_windows[entity_id]
        
        if not window:
            return 0.0
        
        # Check cache
        if entity_id in self._entropy_cache:
            cached_entropy, cached_time = self._entropy_cache[entity_id]
            # Simple cache validation - if window hasn't changed, return cached
            # For now, we'll just recompute for simplicity and accuracy
        
        counts = {}
        for signal in window:
            counts[signal] = counts.get(signal, 0) + 1
        
        total = len(window)
        entropy = 0.0
        
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalize entropy to [0, 1] for better interpretability
        max_entropy = math.log2(min(total, len(counts))) if total > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return normalized_entropy

    def _compute_z_score(self, entity_id: str, current_entropy: float) -> float:
        """Compute z-score for an entity's entropy relative to its history."""
        history = self.entity_entropy_history[entity_id]
        
        if len(history) < 3:
            return 0.0
        
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std = math.sqrt(variance)
        
        if std == 0:
            return 0.0
        
        return (current_entropy - mean) / std

    def get_entity_entropy(self, entity_id: str) -> float:
        """Get current entropy for an entity."""
        if not entity_id:
            return 0.0
        return round(self._compute_entropy(entity_id), 4)

    def get_entity_z_score(self, entity_id: str) -> float:
        """Get current z-score for an entity."""
        if not entity_id:
            return 0.0
        entropy = self._compute_entropy(entity_id)
        return round(self._compute_z_score(entity_id, entropy), 4)

    def get_entity_stats(self, entity_id: str) -> dict:
        """Get comprehensive stats for an entity."""
        entropy = self._compute_entropy(entity_id)
        z_score = self._compute_z_score(entity_id, entropy)
        history = self.entity_entropy_history[entity_id]
        
        return {
            "entity_id": entity_id,
            "entropy": round(entropy, 4),
            "z_score": round(z_score, 4),
            "window_size": len(self.entity_windows[entity_id]),
            "history_length": len(history),
            "history_mean": round(sum(history) / len(history), 4) if history else 0.0,
            "history_std": round(math.sqrt(sum((x - sum(history)/len(history)) ** 2 for x in history) / len(history)), 4) if history and len(history) > 1 else 0.0,
            "alert_triggered": abs(z_score) > self.alert_threshold or entropy > self.entropy_alert_threshold
        }

    def get_global_stats(self) -> dict:
        """Get global entropy engine statistics."""
        total_entities = len(self.entity_windows)
        active_entities = sum(1 for w in self.entity_windows.values() if w)
        
        # Compute average entropy across all entities
        entropies = []
        for eid in self.entity_windows:
            if self.entity_windows[eid]:
                entropies.append(self._compute_entropy(eid))
        
        avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0
        max_entropy = max(entropies) if entropies else 0.0
        min_entropy = min(entropies) if entropies else 0.0
        
        # Get entities with alerts
        alert_entities = []
        for eid in self.entity_windows:
            stats = self.get_entity_stats(eid)
            if stats["alert_triggered"]:
                alert_entities.append({
                    "entity_id": eid,
                    "entropy": stats["entropy"],
                    "z_score": stats["z_score"]
                })
        
        return {
            "total_entities": total_entities,
            "active_entities": active_entities,
            "total_events_processed": self.total_events_processed,
            "alerts_triggered": self.alerts_triggered,
            "avg_entropy": round(avg_entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "min_entropy": round(min_entropy, 4),
            "alert_entities_count": len(alert_entities),
            "alert_entities": alert_entities[:10],  # Limit to first 10
            "window_size": self.window_size,
            "alert_threshold": self.alert_threshold
        }

    def reset_entity(self, entity_id: str) -> bool:
        """Reset an entity's entropy history."""
        if entity_id in self.entity_windows:
            self.entity_windows[entity_id].clear()
            self.entity_entropy_history[entity_id].clear()
            self._entropy_cache.pop(entity_id, None)
            return True
        return False

    def reset_all(self) -> None:
        """Reset all entity histories."""
        self.entity_windows.clear()
        self.entity_entropy_history.clear()
        self._entropy_cache.clear()
        self.total_events_processed = 0
        self.alerts_triggered = 0
        logger.info("[ENTROPY] All entity histories reset")

    def get_entropy_trend(self, entity_id: str, n: int = 10) -> List[float]:
        """Get recent entropy history for an entity."""
        if entity_id not in self.entity_entropy_history:
            return []
        history = list(self.entity_entropy_history[entity_id])
        return history[-n:] if history else []

    def get_window_distribution(self, entity_id: str) -> Dict[str, int]:
        """Get the distribution of event types in an entity's window."""
        if entity_id not in self.entity_windows or not self.entity_windows[entity_id]:
            return {}
        
        counts = {}
        for signal in self.entity_windows[entity_id]:
            counts[signal] = counts.get(signal, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


# Singleton instance used across the app
entropy_engine = EntropyEngine()