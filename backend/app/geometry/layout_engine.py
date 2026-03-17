from app.schemas import GeometryResponse, LayoutSpec


class GeometryError(Exception):
    pass


def _point_from_wall(wall: str, position: float, width: float, height: float) -> list[float]:
    wall_name = wall.lower()
    if wall_name == 'south':
        return [position, 0.0]
    if wall_name == 'north':
        return [position, height]
    if wall_name == 'west':
        return [0.0, position]
    if wall_name == 'east':
        return [width, position]
    raise GeometryError(f'Invalid wall value: {wall}')


def build_geometry(spec: LayoutSpec) -> GeometryResponse:
    walls = [
        [0.0, 0.0, spec.width, 0.0],
        [spec.width, 0.0, spec.width, spec.height],
        [spec.width, spec.height, 0.0, spec.height],
        [0.0, spec.height, 0.0, 0.0],
    ]

    doors = [_point_from_wall(item.wall, item.position, spec.width, spec.height) for item in spec.doors]
    windows = [_point_from_wall(item.wall, item.position, spec.width, spec.height) for item in spec.windows]

    return GeometryResponse(walls=walls, doors=doors, windows=windows)
