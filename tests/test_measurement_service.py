from shapely.geometry import Polygon, LineString, Point
from app.services.measurement_service import measure_geometry

def test_polygon_area():
    typ, value, status, err = measure_geometry(Polygon([(0,0),(10,0),(10,10),(0,10)]))
    assert typ == "area" and value == 100 and status == "COMPLETED"

def test_line_length():
    typ, value, status, err = measure_geometry(LineString([(0,0),(3,4)]))
    assert typ == "length" and value == 5

def test_point_no_measurement():
    typ, value, status, err = measure_geometry(Point(0,0))
    assert typ is None and value is None and status == "NO_MEASUREMENT"
