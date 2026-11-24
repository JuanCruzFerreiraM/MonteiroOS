"""GeoJSON polygon checks for production boundaries.

Topology uses Shapely (GEOS). A bounding box is not treated as an intersection.
Saved coordinates are the ones submitted after structural checks. They are not
rewritten, clipped, or reordered to force a polygon inside its quinta.
"""

import math
import uuid
from dataclasses import dataclass

from shapely.geometry import Polygon
from shapely.validation import explain_validity

from app.modules.production.rules import DomainError

MAX_RING_POSITIONS = 128
MAX_GEOMETRY_CHARS = 16_384
MINOR_OUTSIDE_RATIO = 0.15
INTERSECTION_MIN_RATIO = 0.001
OVERLAP_MIN_RATIO = 0.001
OUTSIDE_EPSILON = 1e-8

NO_INTERSECTION_MESSAGE = (
    "El polígono de la vidriera no intersecta el límite de la quinta. "
    "Dibújelo sobre la quinta. El trazado no se guardó y el límite anterior "
    "no cambió."
)
LARGE_OVERFLOW_MESSAGE = (
    "El polígono se sale de forma considerable del límite de la quinta. "
    "Ajuste los vértices para que la mayor parte quede adentro. "
    "El trazado no se recortó y el límite anterior no cambió."
)
MINOR_OVERFLOW_MESSAGE = (
    "El polígono se extiende un poco fuera de la quinta. "
    "Se guardó el trazado original, sin recortarlo."
)
CONSIDERABLE_OVERFLOW_MESSAGE = (
    "El polígono guardado se extiende bastante fuera del límite actual "
    "de la quinta. No se modificó."
)
DISCONNECTED_MESSAGE = (
    "El polígono guardado ya no intersecta el límite actual de la quinta. "
    "No se modificó."
)


@dataclass(frozen=True)
class GeometryWarning:
    code: str
    message: str
    vidriera_id: uuid.UUID | None = None
    vidriera_code: str | None = None


@dataclass(frozen=True)
class Placement:
    intersects: bool
    outside_ratio: float
    overlaps: tuple[tuple[uuid.UUID, str], ...]


def parse_polygon(value: object) -> dict:
    """Accept one closed WGS84 GeoJSON Polygon and return that same ring."""
    if not isinstance(value, dict):
        raise DomainError(422, "La geometría debe ser un objeto GeoJSON Polygon.")
    if set(value) - {"type", "coordinates"}:
        raise DomainError(
            422,
            "El polígono solo debe incluir type y coordinates. "
            "No envíe posiciones de pantalla ni otro formato.",
        )
    geometry_type = value.get("type")
    if geometry_type == "MultiPolygon":
        raise DomainError(
            422,
            "Solo se admite un polígono simple. No se acepta MultiPolygon.",
        )
    if geometry_type != "Polygon":
        raise DomainError(
            422,
            "La geometría debe ser un GeoJSON Polygon con longitud y latitud.",
        )
    coordinates = value.get("coordinates")
    if isinstance(coordinates, list) and len(coordinates) > 1:
        raise DomainError(
            422,
            "Este mapa solo admite un contorno exterior, sin huecos.",
        )
    if not isinstance(coordinates, list) or len(coordinates) != 1:
        raise DomainError(422, "El polígono debe tener un único contorno exterior.")
    ring = coordinates[0]
    if not isinstance(ring, list):
        raise DomainError(422, "El contorno del polígono no tiene una forma válida.")
    if len(ring) > MAX_RING_POSITIONS:
        raise DomainError(
            422,
            f"El polígono admite hasta {MAX_RING_POSITIONS} posiciones.",
        )
    if len(ring) < 4:
        raise DomainError(
            422,
            "El contorno necesita al menos tres vértices distintos y debe "
            "cerrarse repitiendo el primer punto al final.",
        )

    parsed: list[list[float]] = []
    for position in ring:
        parsed.append(_position(position))
    if parsed[0] != parsed[-1]:
        raise DomainError(
            422,
            "El contorno debe cerrarse: el último punto tiene que ser igual "
            "al primero.",
        )
    distinct = list(dict.fromkeys(tuple(point) for point in parsed[:-1]))
    if len(distinct) < 3:
        raise DomainError(
            422,
            "El polígono necesita al menos tres vértices distintos.",
        )

    polygon = Polygon(parsed)
    if not polygon.is_valid:
        reason = explain_validity(polygon).lower()
        if "self-intersection" in reason:
            raise DomainError(
                422,
                "El polígono se cruza a sí mismo. Separe los lados que se "
                "cruzan. El límite anterior no cambió.",
            )
        raise DomainError(
            422,
            "El polígono no es válido. Revise que el contorno no se cruce "
            "ni se repita. El límite anterior no cambió.",
        )
    if polygon.is_empty or polygon.area <= 0:
        raise DomainError(
            422,
            "El polígono no tiene superficie. Marque tres vértices que no "
            "estén en la misma línea.",
        )

    canonical = {"type": "Polygon", "coordinates": [parsed]}
    encoded_length = len(str(canonical))
    if encoded_length > MAX_GEOMETRY_CHARS:
        raise DomainError(422, "El polígono es demasiado grande para guardarlo.")
    return canonical


def require_vidriera_placement(
    geometry: dict,
    quinta_geometry: dict,
    others: list[tuple[uuid.UUID, str, dict]],
) -> list[GeometryWarning]:
    placement = _placement(geometry, quinta_geometry, others)
    if not placement.intersects:
        raise DomainError(422, NO_INTERSECTION_MESSAGE)
    if placement.outside_ratio > MINOR_OUTSIDE_RATIO:
        raise DomainError(422, LARGE_OVERFLOW_MESSAGE)
    return _write_warnings(placement)


def read_vidriera_warnings(
    geometry: dict,
    quinta_geometry: dict | None,
    others: list[tuple[uuid.UUID, str, dict]],
) -> list[GeometryWarning]:
    """Warnings for a boundary that is already stored. Never rejects it."""
    if quinta_geometry is None:
        return [
            GeometryWarning(
                code="boundary_disconnected",
                message=(
                    "La quinta ya no tiene un límite, pero este polígono "
                    "sigue guardado."
                ),
            )
        ]
    try:
        placement = _placement(geometry, quinta_geometry, others)
    except DomainError:
        return [
            GeometryWarning(
                code="placement_unchecked",
                message=(
                    "No se pudo comparar este polígono con el límite de la "
                    "quinta. El trazado guardado no se modificó."
                ),
            )
        ]
    warnings: list[GeometryWarning] = []
    if not placement.intersects:
        warnings.append(
            GeometryWarning(code="boundary_disconnected", message=DISCONNECTED_MESSAGE)
        )
    elif placement.outside_ratio > MINOR_OUTSIDE_RATIO:
        warnings.append(
            GeometryWarning(
                code="boundary_overflow",
                message=CONSIDERABLE_OVERFLOW_MESSAGE,
            )
        )
    elif placement.outside_ratio >= OUTSIDE_EPSILON:
        warnings.append(
            GeometryWarning(code="boundary_overflow", message=MINOR_OVERFLOW_MESSAGE)
        )
    warnings.extend(_overlap_warnings(placement))
    return warnings


def _write_warnings(placement: Placement) -> list[GeometryWarning]:
    warnings: list[GeometryWarning] = []
    if placement.outside_ratio >= OUTSIDE_EPSILON:
        warnings.append(
            GeometryWarning(code="boundary_overflow", message=MINOR_OVERFLOW_MESSAGE)
        )
    warnings.extend(_overlap_warnings(placement))
    return warnings


def _overlap_warnings(placement: Placement) -> list[GeometryWarning]:
    return [
        GeometryWarning(
            code="vidriera_overlap",
            message=(
                f"El polígono se superpone con {code}. Se conservó el trazado original."
            ),
            vidriera_id=vidriera_id,
            vidriera_code=code,
        )
        for vidriera_id, code in placement.overlaps
    ]


def _placement(
    geometry: dict,
    quinta_geometry: dict,
    others: list[tuple[uuid.UUID, str, dict]],
) -> Placement:
    vidriera = _stored_polygon(geometry)
    quinta = _stored_polygon(quinta_geometry)
    area = vidriera.area
    intersection_ratio = quinta.intersection(vidriera).area / area
    outside_ratio = vidriera.difference(quinta).area / area
    if outside_ratio < OUTSIDE_EPSILON:
        outside_ratio = 0.0
    overlaps: list[tuple[uuid.UUID, str]] = []
    for vidriera_id, code, other_geometry in others:
        other = _stored_polygon(other_geometry)
        shared = vidriera.intersection(other).area
        baseline = min(area, other.area)
        if baseline > 0 and shared / baseline >= OVERLAP_MIN_RATIO:
            overlaps.append((vidriera_id, code))
    overlaps.sort(key=lambda item: item[1])
    return Placement(
        intersects=intersection_ratio >= INTERSECTION_MIN_RATIO,
        outside_ratio=outside_ratio,
        overlaps=tuple(overlaps),
    )


def _stored_polygon(geometry: dict) -> Polygon:
    try:
        polygon = parse_polygon(geometry)
    except DomainError as error:
        raise DomainError(
            422,
            "Hay un límite guardado que no se puede usar para esta "
            "comparación. No se cambió el polígono enviado.",
        ) from error
    shape = Polygon(polygon["coordinates"][0])
    if not shape.is_valid or shape.area <= 0:
        raise DomainError(
            422,
            "Hay un límite guardado que no se puede usar para esta "
            "comparación. No se cambió el polígono enviado.",
        )
    return shape


def _position(value: object) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise DomainError(
            422,
            "Cada vértice debe ser una longitud y una latitud, en ese orden.",
        )
    longitude = _coordinate(value[0], "longitud")
    latitude = _coordinate(value[1], "latitud")
    if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        raise DomainError(
            422,
            "La longitud debe estar entre -180 y 180 y la latitud entre -90 "
            "y 90. El orden es longitud, luego latitud.",
        )
    return [longitude, latitude]


def _coordinate(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DomainError(422, f"La {name} debe ser un número finito.")
    number = float(value)
    if not math.isfinite(number):
        raise DomainError(422, f"La {name} debe ser un número finito.")
    return number
