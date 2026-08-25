from typing import List
from app.models.docket import RoadDocket
from app.schemas.analytics import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry

class GeoJSONService:
    """Generates RFC 7946 compliant GeoJSON payloads for GIS mapping applications (ESRI ArcGIS, QGIS, Leaflet)."""

    @staticmethod
    def dockets_to_geojson(dockets: List[RoadDocket]) -> GeoJSONFeatureCollection:
        features = []
        for d in dockets:
            feat = GeoJSONFeature(
                type="Feature",
                geometry=GeoJSONGeometry(
                    type="Point",
                    coordinates=[d.lng, d.lat] # Standard GeoJSON: [Longitude, Latitude]
                ),
                properties={
                    "id": d.id,
                    "defect_type": d.defect_type,
                    "severity": d.severity,
                    "status": d.status,
                    "location_name": d.location_name,
                    "ward_number": d.ward_number,
                    "corridor": d.corridor,
                    "confidence": d.confidence,
                    "depth_cm": d.depth_cm,
                    "tonnage_mt": d.asphalt_tonnage_mt,
                    "repair_cost_inr": d.repair_cost_inr,
                    "assigned_contractor": d.assigned_contractor,
                    "detected_by_bus": d.detected_by_bus,
                    "detected_at": d.detected_at.isoformat() if d.detected_at else None
                }
            )
            features.append(feat)

        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features
        )
