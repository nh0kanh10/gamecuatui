"""
World Database - Load và quản lý dữ liệu thế giới
Dựa trên thiết kế: Entity-Component, JSON-based, Modding-friendly
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class WorldDatabase:
    """
    World Database - Load toàn bộ dữ liệu thế giới vào RAM
    
    Tối ưu: O(1) lookup bằng dictionary
    Modding-friendly: Chỉ cần sửa JSON, không cần sửa code
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.sects: Dict[str, Dict] = {}
        self.techniques: Dict[str, Dict] = {}
        self.races: Dict[str, Dict] = {}
        self.clans: Dict[str, Dict] = {}
        self.locations: Dict[str, Dict] = {}
        self.artifacts: Dict[str, Dict] = {}
        self.items: Dict[str, Dict] = {}
        self.regional_cultures: Dict[str, Dict] = {}
        self.spirit_beasts: Dict[str, Dict] = {}
        self.spirit_herbs: Dict[str, Dict] = {}
        
        self.load_all_data()
    
    def load_all_data(self):
        """Load tất cả dữ liệu từ JSON files"""
        try:
            # Load Sects
            sects_path = self.data_dir / "sects.json"
            if sects_path.exists():
                with open(sects_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.sects[item['id']] = item
            
            # Load Techniques
            techniques_path = self.data_dir / "techniques.json"
            if techniques_path.exists():
                with open(techniques_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.techniques[item['id']] = item
            
            # Load Races
            races_path = self.data_dir / "races.json"
            if races_path.exists():
                with open(races_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.races[item['id']] = item
            
            # Load Clans
            clans_path = self.data_dir / "clans.json"
            if clans_path.exists():
                with open(clans_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.clans[item['id']] = item
            
            # Load Locations
            locations_path = self.data_dir / "locations.json"
            if locations_path.exists():
                with open(locations_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.locations[item['id']] = item
            
            # Load Artifacts
            artifacts_path = self.data_dir / "artifacts.json"
            if artifacts_path.exists():
                with open(artifacts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.artifacts[item['id']] = item
            
            # Load Items
            items_path = self.data_dir / "items.json"
            if items_path.exists():
                with open(items_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.items[item['id']] = item
            
            # Load Regional Cultures
            cultures_path = self.data_dir / "regional_cultures.json"
            if cultures_path.exists():
                with open(cultures_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.regional_cultures[item['region_id']] = item
            
            # Load Spirit Beasts
            beasts_path = self.data_dir / "spirit_beasts.json"
            if beasts_path.exists():
                with open(beasts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.spirit_beasts[item['id']] = item
            
            # Load Spirit Herbs
            herbs_path = self.data_dir / "spirit_herbs.json"
            if herbs_path.exists():
                with open(herbs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.spirit_herbs[item['id']] = item
            
            print(f"✅ Loaded: {len(self.sects)} sects, {len(self.techniques)} techniques, "
                  f"{len(self.races)} races, {len(self.clans)} clans, {len(self.locations)} locations, "
                  f"{len(self.artifacts)} artifacts, {len(self.items)} items, {len(self.regional_cultures)} regional cultures, "
                  f"{len(self.spirit_beasts)} spirit beasts, {len(self.spirit_herbs)} spirit herbs")
        
        except Exception as e:
            print(f"❌ Error loading world data: {e}")
    
    # --- SECT METHODS ---
    
    def get_sect(self, sect_id: str) -> Optional[Dict]:
        """Get sect by ID"""
        return self.sects.get(sect_id)
    
    def get_sect_bonus(self, sect_id: str) -> str:
        """Get sect bonus description"""
        sect = self.sects.get(sect_id)
        if sect:
            return f"Gia nhập {sect['name']}, bạn được học: {sect.get('exclusive_techniques', [])}"
        return "Tông môn không tồn tại."
    
    def check_sect_requirements(
        self,
        sect_id: str,
        attributes: Dict[str, float],
        traits: List[str]
    ) -> Dict[str, Any]:
        """
        Kiểm tra xem có đủ điều kiện gia nhập tông môn không
        
        Returns:
            {
                "eligible": bool,
                "missing_requirements": List[str],
                "bonuses": Dict[str, Any]
            }
        """
        sect = self.sects.get(sect_id)
        if not sect:
            return {
                "eligible": False,
                "missing_requirements": ["Sect not found"],
                "bonuses": {}
            }
        
        requirements = sect.get("requirements", {})
        missing = []
        
        # Check min attributes
        for attr_name, min_value in requirements.items():
            if attr_name.startswith("min_"):
                attr_key = attr_name.replace("min_", "").upper()
                if attributes.get(attr_key, 0) < min_value:
                    missing.append(f"{attr_key} < {min_value} (need {min_value})")
        
        # Check preferred traits
        preferred = requirements.get("preferred_traits", [])
        has_preferred = any(trait in traits for trait in preferred)
        if preferred and not has_preferred:
            missing.append(f"Missing preferred trait: {preferred}")
        
        # Check forbidden traits
        forbidden = requirements.get("forbidden_traits", [])
        has_forbidden = any(trait in traits for trait in forbidden)
        if forbidden and has_forbidden:
            missing.append(f"Has forbidden trait: {forbidden}")
        
        eligible = len(missing) == 0
        
        return {
            "eligible": eligible,
            "missing_requirements": missing,
            "bonuses": {
                "exclusive_techniques": sect.get("exclusive_techniques", []),
                "resources": sect.get("resources", {}),
                "sect_type": sect.get("type", "Unknown")
            }
        }
    
    def get_sects_by_region(self, region: str) -> List[Dict]:
        """Get all sects in a region"""
        return [s for s in self.sects.values() if s.get("location_zone") == region]
    
    # --- TECHNIQUE METHODS ---
    
    def get_technique(self, tech_id: str) -> Optional[Dict]:
        """Get technique by ID"""
        return self.techniques.get(tech_id)
    
    def check_technique_requirements(
        self,
        tech_id: str,
        realm: str,
        attributes: Dict[str, float],
        sect_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kiểm tra xem có thể học kỹ thuật không
        """
        tech = self.techniques.get(tech_id)
        if not tech:
            return {
                "can_learn": False,
                "missing_requirements": ["Technique not found"]
            }
        
        requirements = tech.get("requirements", {})
        missing = []
        
        # Check realm
        min_realm = requirements.get("min_realm", "")
        if min_realm and realm < min_realm:
            missing.append(f"Realm too low: need {min_realm}, have {realm}")
        
        # Check attributes
        for attr_name, min_value in requirements.items():
            if attr_name.startswith("min_"):
                attr_key = attr_name.replace("min_", "").upper()
                if attributes.get(attr_key, 0) < min_value:
                    missing.append(f"{attr_key} < {min_value}")
        
        # Check sect
        required_sect = requirements.get("required_sect")
        if required_sect and sect_id != required_sect:
            missing.append(f"Must be member of {required_sect}")
        
        return {
            "can_learn": len(missing) == 0,
            "missing_requirements": missing,
            "effects": tech.get("effects", {}),
            "special_abilities": tech.get("special_abilities", [])
        }
    
    # --- RACE METHODS ---
    
    def get_race(self, race_id: str) -> Optional[Dict]:
        """Get race by ID"""
        return self.races.get(race_id)
    
    def get_race_base_stats(self, race_id: str) -> Dict[str, float]:
        """Get base stats for a race"""
        race = self.races.get(race_id)
        if race:
            return race.get("base_stats", {})
        return {}
    
    def get_race_growth_modifiers(self, race_id: str) -> Dict[str, float]:
        """Get growth modifiers for a race"""
        race = self.races.get(race_id)
        if race:
            return race.get("growth_modifiers", {})
        return {}
    
    # --- CLAN METHODS ---
    
    def get_clan(self, clan_id: str) -> Optional[Dict]:
        """Get clan by ID"""
        return self.clans.get(clan_id)
    
    def get_clan_starting_perks(self, clan_id: str) -> Dict[str, Any]:
        """Get starting perks for a clan"""
        clan = self.clans.get(clan_id)
        if clan:
            return clan.get("starting_perks", {})
        return {}
    
    def get_clan_relationships(self, clan_id: str) -> Dict[str, List[str]]:
        """Get clan relationships (rivals, allies)"""
        clan = self.clans.get(clan_id)
        if clan:
            return {
                "rivals": clan.get("rivals", []),
                "allies": clan.get("allies", [])
            }
        return {"rivals": [], "allies": []}
    
    # --- LOCATION METHODS ---
    
    def get_location(self, loc_id: str) -> Optional[Dict]:
        """Get location by ID"""
        return self.locations.get(loc_id)
    
    def get_locations_by_region(self, region: str) -> List[Dict]:
        """Get all locations in a region"""
        return [l for l in self.locations.values() if l.get("region") == region]
    
    def get_connected_locations(self, loc_id: str) -> List[Dict]:
        """Get connected locations"""
        location = self.locations.get(loc_id)
        if not location:
            return []
        
        connected_ids = location.get("connected_to", [])
        return [self.locations.get(cid) for cid in connected_ids if self.locations.get(cid)]
    
    def can_access_location(
        self,
        loc_id: str,
        current_realm: str,
        attributes: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Kiểm tra xem có thể vào địa điểm không
        
        Returns:
            {
                "can_access": bool,
                "danger_level": str,
                "recommended_level": List[int],
                "warnings": List[str]
            }
        """
        location = self.locations.get(loc_id)
        if not location:
            return {
                "can_access": False,
                "danger_level": "Unknown",
                "recommended_level": [],
                "warnings": ["Location not found"]
            }
        
        level_range = location.get("level_range", [1, 1])
        danger_level = location.get("danger_level", "Unknown")
        debuffs = location.get("debuffs", [])
        
        warnings = []
        if danger_level == "Extreme":
            warnings.append("⚠️ Cực kỳ nguy hiểm! Có thể tử vong!")
        elif danger_level == "High":
            warnings.append("⚠️ Rất nguy hiểm! Cần chuẩn bị kỹ!")
        
        if debuffs:
            warnings.append(f"⚠️ Debuffs: {', '.join(debuffs)}")
        
        return {
            "can_access": True,
            "danger_level": danger_level,
            "recommended_level": level_range,
            "warnings": warnings,
            "qi_density": location.get("qi_density", 0.0),
            "services": location.get("services", [])
        }
    
    # --- UTILITY METHODS ---
    
    def get_all_sects(self) -> List[Dict]:
        """Get all sects"""
        return list(self.sects.values())
    
    def get_all_techniques(self) -> List[Dict]:
        """Get all techniques"""
        return list(self.techniques.values())
    
    def get_all_races(self) -> List[Dict]:
        """Get all races"""
        return list(self.races.values())
    
    def get_all_clans(self) -> List[Dict]:
        """Get all clans"""
        return list(self.clans.values())
    
    def get_all_locations(self) -> List[Dict]:
        """Get all locations"""
        return list(self.locations.values())
    
    # --- ARTIFACT METHODS ---
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get artifact by ID"""
        return self.artifacts.get(artifact_id)
    
    def get_artifacts_by_tier(self, tier: str) -> List[Dict]:
        """Get all artifacts of a specific tier"""
        return [a for a in self.artifacts.values() if a.get("tier") == tier]
    
    def get_artifacts_by_realm(self, realm: str) -> List[Dict]:
        """Get all artifacts usable at a specific realm"""
        return [a for a in self.artifacts.values() if a.get("realm_requirement") == realm]
    
    def check_artifact_requirements(
        self,
        artifact_id: str,
        current_realm: str,
        attributes: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check if player can use artifact"""
        artifact = self.artifacts.get(artifact_id)
        if not artifact:
            return {
                "can_use": False,
                "missing_requirements": ["Artifact not found"]
            }
        
        required_realm = artifact.get("realm_requirement", "")
        missing = []
        
        # Check realm (simplified - can be enhanced with realm hierarchy)
        if required_realm and current_realm != required_realm:
            # TODO: Implement realm hierarchy check
            missing.append(f"Realm too low: need {required_realm}, have {current_realm}")
        
        return {
            "can_use": len(missing) == 0,
            "missing_requirements": missing,
            "artifact": artifact
        }
    
    # --- ITEM METHODS ---
    
    def get_item(self, item_id: str) -> Optional[Dict]:
        """Get item by ID"""
        return self.items.get(item_id)
    
    def get_items_by_type(self, item_type: str) -> List[Dict]:
        """Get all items of a specific type"""
        return [i for i in self.items.values() if i.get("type") == item_type]
    
    def get_items_by_rarity(self, rarity: str) -> List[Dict]:
        """Get all items of a specific rarity"""
        return [i for i in self.items.values() if i.get("rarity") == rarity]
    
    def get_materials_by_location(self, location_id: str) -> List[Dict]:
        """Get materials that can be found at a location"""
        materials = self.get_items_by_type("Material")
        result = []
        for m in materials:
            locations = m.get("locations", [])
            if isinstance(locations, list) and location_id in locations:
                result.append(m)
        return result
    
    # --- REGIONAL CULTURE METHODS ---
    
    def get_regional_culture(self, region_id: str) -> Optional[Dict]:
        """Get regional culture by region ID"""
        return self.regional_cultures.get(region_id)
    
    def get_culture_by_location(self, location_id: str) -> Optional[Dict]:
        """Get regional culture for a location"""
        location = self.locations.get(location_id)
        if location:
            region = location.get("region")
            return self.regional_cultures.get(region)
        return None
    
    def get_npc_behavior(
        self,
        region_id: str,
        player_reputation: int = 0,
        player_realm: str = "Qi_Refining"
    ) -> Dict[str, Any]:
        """
        Generate NPC behavior based on regional culture
        
        Returns:
            {
                "attitude": "Neutral|Hostile|Friendly|Respectful",
                "greeting": str,
                "interaction_style": str
            }
        """
        culture = self.regional_cultures.get(region_id)
        if not culture:
            return {
                "attitude": "Neutral",
                "greeting": "Xin chào",
                "interaction_style": "Standard"
            }
        
        social_rules = culture.get("social_rules", {})
        traits = culture.get("cultural_traits", [])
        
        # Determine attitude based on region
        attitude = "Neutral"
        if region_id == "region_central_plains":
            if player_reputation < 0:
                attitude = "Hostile_Hidden"
            else:
                attitude = "Polite"
        elif region_id == "region_northern_tundra":
            if player_reputation > 1000:
                attitude = "Respectful"
            else:
                attitude = "Aggressive_Test"
        elif region_id == "region_southern_border":
            attitude = "Cautious"
        elif region_id == "region_western_desert":
            attitude = "Merchant_Focused"
        elif region_id == "region_eastern_sea":
            attitude = "Adventurous"
        
        return {
            "attitude": attitude,
            "greeting": social_rules.get("greeting_style", "Standard"),
            "interaction_style": culture.get("vibe", "Neutral"),
            "cultural_traits": traits,
            "unique_activities": culture.get("unique_activities", [])
        }
    
    # --- UTILITY METHODS (Updated) ---
    
    def search_by_name(self, name: str) -> Dict[str, List[Dict]]:
        """
        Tìm kiếm theo tên (fuzzy search)
        """
        results = {
            "sects": [],
            "techniques": [],
            "races": [],
            "clans": [],
            "locations": [],
            "artifacts": [],
            "items": []
        }
        
        name_lower = name.lower()
        
        for sect in self.sects.values():
            if name_lower in sect.get("name", "").lower():
                results["sects"].append(sect)
        
        for tech in self.techniques.values():
            if name_lower in tech.get("name", "").lower():
                results["techniques"].append(tech)
        
        for race in self.races.values():
            if name_lower in race.get("name", "").lower():
                results["races"].append(race)
        
        for clan in self.clans.values():
            if name_lower in clan.get("name", "").lower():
                results["clans"].append(clan)
        
        for loc in self.locations.values():
            if name_lower in loc.get("name", "").lower():
                results["locations"].append(loc)
        
        for artifact in self.artifacts.values():
            if name_lower in artifact.get("name", "").lower():
                results["artifacts"].append(artifact)
        
        for item in self.items.values():
            if name_lower in item.get("name", "").lower():
                results["items"].append(item)
        
        for beast in self.spirit_beasts.values():
            if name_lower in beast.get("name", "").lower():
                results["beasts"] = results.get("beasts", [])
                results["beasts"].append(beast)
        
        for herb in self.spirit_herbs.values():
            if name_lower in herb.get("name", "").lower():
                results["herbs"] = results.get("herbs", [])
                results["herbs"].append(herb)
        
        return results
    
    # --- SPIRIT BEAST METHODS ---
    
    def get_spirit_beast(self, beast_id: str) -> Optional[Dict]:
        """Get spirit beast template by ID"""
        return self.spirit_beasts.get(beast_id)
    
    def get_beasts_by_tier(self, tier: str) -> List[Dict]:
        """Get all beasts of a specific tier"""
        return [
            b for b in self.spirit_beasts.values()
            if b.get("taxonomy", {}).get("tier") == tier
        ]
    
    def get_beasts_by_family(self, family: str) -> List[Dict]:
        """Get all beasts of a specific family"""
        return [
            b for b in self.spirit_beasts.values()
            if b.get("taxonomy", {}).get("family") == family
        ]
    
    def get_beasts_by_region(self, region_id: str) -> List[Dict]:
        """Get beasts that can spawn in a region"""
        # This will be used with spawn tables
        # For now, return all beasts (filtering done by spawn table)
        return list(self.spirit_beasts.values())
    
    # --- SPIRIT HERB METHODS ---
    
    def get_spirit_herb(self, herb_id: str) -> Optional[Dict]:
        """Get spirit herb template by ID"""
        return self.spirit_herbs.get(herb_id)
    
    def get_herbs_by_element(self, element: str) -> List[Dict]:
        """Get all herbs of a specific element"""
        return [
            h for h in self.spirit_herbs.values()
            if h.get("element") == element
        ]
    
    def get_herbs_by_type(self, herb_type: str) -> List[Dict]:
        """Get all herbs of a specific type"""
        return [
            h for h in self.spirit_herbs.values()
            if h.get("type") == herb_type
        ]
    
    def get_herbs_for_alchemy(self, pill_id: str) -> List[Dict]:
        """Get herbs that can be used to craft a specific pill"""
        # Check which herbs have this pill in alchemy_uses
        return [
            h for h in self.spirit_herbs.values()
            if pill_id in h.get("alchemy_uses", [])
        ]

