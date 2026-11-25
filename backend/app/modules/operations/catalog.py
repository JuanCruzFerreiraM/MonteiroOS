from app.modules.production.rules import DomainError

OPERATION_TYPES = (
    "irrigation",
    "artificial_lighting",
    "black_nylon",
    "cold_protection_heating",
    "product_application",
    "manual_labor",
    "observation",
)
INTERVAL_TYPES = frozenset({"artificial_lighting", "black_nylon"})
SCHEDULE_TYPES = INTERVAL_TYPES

OPERATION_LABELS = {
    "irrigation": "Riego",
    "artificial_lighting": "Iluminación artificial",
    "black_nylon": "Cobertura con nylon negro",
    "cold_protection_heating": "Calefacción contra el frío",
    "product_application": "Aplicación de productos",
    "manual_labor": "Mano de obra",
    "observation": "Observación",
}


def require_operation_type(value: object) -> str:
    if not isinstance(value, str) or value not in OPERATION_TYPES:
        raise DomainError(422, "El tipo de operación no es válido.")
    return value


def require_schedule_type(value: object) -> str:
    if not isinstance(value, str) or value not in SCHEDULE_TYPES:
        raise DomainError(
            422,
            "Solo la iluminación artificial y el nylon negro tienen programación.",
        )
    return value
