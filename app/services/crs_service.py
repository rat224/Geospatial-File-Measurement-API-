import math
import geopandas as gpd
from pyproj import CRS

def choose_projected_crs(gdf: gpd.GeoDataFrame) -> CRS:
    if gdf.crs is None:
        raise ValueError("Input file has no CRS; measurements cannot be calculated safely.")
    source = CRS.from_user_input(gdf.crs)
    if source.is_projected:
        return source
    # Transform only the centroid to WGS84 for UTM zone selection.
    wgs = gdf.to_crs("EPSG:4326")
    # Estimate the centroid in WGS84 for selecting a UTM zone.
    centroid = wgs.geometry.union_all().centroid
    lon, lat = centroid.x, centroid.y
    zone = int((lon + 180) // 6) + 1
    epsg = (32600 if lat >= 0 else 32700) + zone
    return CRS.from_epsg(epsg)

def project_for_measurement(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, str]:
    target = choose_projected_crs(gdf)
    return gdf.to_crs(target), target.to_string()
