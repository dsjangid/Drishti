import math
from app.config import settings

class IRCCostCalculator:
    """
    Indian Roads Congress (IRC:SP:72 & IRC:82) Standard Asphalt Repair & Pothole Patching Engine.
    
    Formula:
    - Crater Area = Length × Width (m²)
    - Volume = Area × Depth (m³)
    - Compacted Asphalt Density = 2.4 MT / m³
    - Compaction & Wastage Factor = 1.15 (15% safety margin)
    - Tonnage = Volume × 2.4 × 1.15
    - Repair Cost = (Tonnage × Rate_per_MT) + Base_Mobilization_Fee
    """

    @staticmethod
    def calculate_repair_metrics(depth_cm: float, estimated_diameter_m: float = 1.2, defect_type: str = "POTHOLE"):
        # Depth in meters
        depth_m = max(0.02, depth_cm / 100.0)
        
        # Approximate circular/elliptical crater area
        radius_m = estimated_diameter_m / 2.0
        area_m2 = math.pi * (radius_m ** 2)
        
        # Volume in cubic meters
        volume_m3 = round(area_m2 * depth_m, 3)
        
        # Tonnage computation (2.4 MT per m3 density + 15% compaction buffer)
        density_factor = 2.4
        compaction_factor = 1.15
        
        # For non-pothole defect types (e.g. waterlogging / raveling), adjust area footprint
        if defect_type == "WATERLOGGED_SHOULDER":
            volume_m3 *= 1.8
        elif defect_type == "RAVELING":
            volume_m3 *= 0.8
            
        tonnage_mt = round(volume_m3 * density_factor * compaction_factor, 2)
        
        # Ensure minimum patch order (0.5 MT)
        tonnage_mt = max(0.5, tonnage_mt)
        
        # Budget calculation using IRC standard rates
        material_cost = tonnage_mt * settings.IRC_ASPHALT_RATE_PER_MT
        total_estimated_cost = round(material_cost + settings.BASE_MOBILIZATION_FEE, -2) # Round to nearest 100
        
        return {
            "depth_cm": depth_cm,
            "volume_m3": volume_m3,
            "tonnage_mt": tonnage_mt,
            "estimated_cost_inr": total_estimated_cost
        }

