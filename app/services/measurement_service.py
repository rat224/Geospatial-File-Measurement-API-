from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString

SUPPORTED = (Polygon, MultiPolygon, LineString, MultiLineString)

def measure_geometry(geometry):
    if geometry is None or geometry.is_empty:
        return None, None, "UNSUPPORTED_GEOMETRY", "Geometry is empty or missing."
    if isinstance(geometry, (Polygon, MultiPolygon)):
        return "area", float(geometry.area), "COMPLETED", None
    if isinstance(geometry, (LineString, MultiLineString)):
        return "length", float(geometry.length), "COMPLETED", None
    return None, None, "NO_MEASUREMENT", None
