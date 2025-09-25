"""
Building Configuration System
Handles building-specific scanning parameters
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

@dataclass
class FontSizeRange:
    """Font size range configuration"""
    min_size: float
    max_size: float
    
    def contains(self, size: float) -> bool:
        return self.min_size <= size <= self.max_size

@dataclass
class RoomPattern:
    """Room text pattern configuration"""
    pattern: str
    description: str
    enabled: bool = True
    
    def matches(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            return bool(re.match(self.pattern, text, re.IGNORECASE))
        except re.error:
            return False

@dataclass
class BuildingConfig:
    """Configuration for a specific building"""
    building_name: str
    font_size_ranges: List[FontSizeRange]
    room_patterns: List[RoomPattern]
    entrance_keywords: List[str]
    exclude_patterns: List[RoomPattern]
    
    # Advanced options
    min_text_length: int = 1
    max_text_length: int = 15
    case_sensitive: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'building_name': self.building_name,
            'font_size_ranges': [{'min_size': r.min_size, 'max_size': r.max_size} for r in self.font_size_ranges],
            'room_patterns': [{'pattern': p.pattern, 'description': p.description, 'enabled': p.enabled} for p in self.room_patterns],
            'entrance_keywords': self.entrance_keywords,
            'exclude_patterns': [{'pattern': p.pattern, 'description': p.description, 'enabled': p.enabled} for p in self.exclude_patterns],
            'min_text_length': self.min_text_length,
            'max_text_length': self.max_text_length,
            'case_sensitive': self.case_sensitive
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildingConfig':
        """Create BuildingConfig from dictionary"""
        return cls(
            building_name=data['building_name'],
            font_size_ranges=[FontSizeRange(**r) for r in data.get('font_size_ranges', [])],
            room_patterns=[RoomPattern(**p) for p in data.get('room_patterns', [])],
            entrance_keywords=data.get('entrance_keywords', []),
            exclude_patterns=[RoomPattern(**p) for p in data.get('exclude_patterns', [])],
            min_text_length=data.get('min_text_length', 1),
            max_text_length=data.get('max_text_length', 15),
            case_sensitive=data.get('case_sensitive', False)
        )

class ConfigurationManager:
    """Manages building configurations"""
    
    def __init__(self, buildings_path: str):
        self.buildings_path = buildings_path
        self.configs_path = os.path.join(buildings_path, "_configs")
        self.ensure_configs_directory()
    
    def ensure_configs_directory(self):
        """Ensure the configs directory exists"""
        if not os.path.exists(self.configs_path):
            os.makedirs(self.configs_path)
    
    def get_config_file_path(self, building_name: str) -> str:
        """Get path to config file for a building"""
        return os.path.join(self.configs_path, f"{building_name}.json")
    
    def load_config(self, building_name: str) -> BuildingConfig:
        """Load configuration for a building, create default if not exists"""
        config_file = self.get_config_file_path(building_name)
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return BuildingConfig.from_dict(data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error loading config for {building_name}: {e}")
                # Fall through to create default
        
        # Create and save default configuration
        default_config = self.create_default_config(building_name)
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: BuildingConfig):
        """Save configuration to file"""
        config_file = self.get_config_file_path(config.building_name)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Saved config for {config.building_name}")
        except Exception as e:
            print(f"Error saving config for {config.building_name}: {e}")
    
    def create_default_config(self, building_name: str) -> BuildingConfig:
        """Create default configuration for a building"""
        return BuildingConfig(
            building_name=building_name,
            font_size_ranges=[
                FontSizeRange(3.2, 3.6),  # Normal room font size
                FontSizeRange(49.0, 49.4)  # Special font size for some floors
            ],
            room_patterns=[
                RoomPattern(r'^[A-Z0-9]{1,4}[-._][A-Z0-9]{1,4}', "Format som PH-D1, A-01", True),
                RoomPattern(r'^\d{2}_\d{2}$', "Format som 01_02", True),
                RoomPattern(r'^[A-Z]\.\d\.\d{2}$', "Format som A.1.01", True),
                RoomPattern(r'^PH-D\d+\.?\d*_?\d*$', "Format som PH-D1.11_01", True),
                RoomPattern(r'^[A-Z]{1,2}\d{2,4}$', "Format som A101, AB123", True),
                RoomPattern(r'^\d{2,4}[A-Z]?$', "Format som 101, 202A", True),
                RoomPattern(r'^[A-Z0-9]{2,8}$', "Korte alfanumeriske koder", True),
                RoomPattern(r'^[A-Z0-9.-_]{2,10}$', "Generelle alfanumeriske kombinationer", True)
            ],
            entrance_keywords=['indgang', 'entrance', 'entry'],
            exclude_patterns=[
                RoomPattern(r'^\d+\.\d+m2$', "Arealmål", True),
                RoomPattern(r'^(Area|Type|Room \d+\.\d+m2):', "Metadata", True),
                RoomPattern(r'^\d+\.\d+$', "Lange decimal tal (over 6 cifre)", True),
                RoomPattern(r'^(width|height|scale|rotation|metadata|properties)$', "Tekniske termer", True),
                RoomPattern(r'^[\d.]+$', "Kun tal og punktummer", True)
            ],
            min_text_length=1,
            max_text_length=15,
            case_sensitive=False
        )
    
    def get_all_building_configs(self) -> List[str]:
        """Get list of buildings with existing configurations"""
        if not os.path.exists(self.configs_path):
            return []
        
        configs = []
        for file in os.listdir(self.configs_path):
            if file.endswith('.json'):
                building_name = file[:-5]  # Remove .json
                configs.append(building_name)
        
        return sorted(configs)
    
    def delete_config(self, building_name: str) -> bool:
        """Delete configuration file for a building"""
        config_file = self.get_config_file_path(building_name)
        if os.path.exists(config_file):
            try:
                os.remove(config_file)
                print(f"Deleted config for {building_name}")
                return True
            except Exception as e:
                print(f"Error deleting config for {building_name}: {e}")
        return False