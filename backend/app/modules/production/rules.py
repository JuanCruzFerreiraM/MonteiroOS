import re

QUINTA_CODE = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")
VIDRIERA_CODE = re.compile(r"^([A-Z][A-Z0-9]{1,11})-V([0-9]+)$")
CANTERO_NUMBERS = (1, 2, 3, 4)
NAME_MAX_LENGTH = 200
NOTES_MAX_LENGTH = 4000


class DomainError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def normalize_quinta_code(value: str) -> str:
    code = value.strip().upper()
    if QUINTA_CODE.fullmatch(code) is None:
        raise DomainError(
            422,
            "El código de la quinta debe tener de 2 a 12 letras o dígitos, "
            "empezar con una letra y no contener espacios. Ejemplo: VE.",
        )
    return code


def format_vidriera_code(quinta_code: str, number: int) -> str:
    if number < 1:
        raise DomainError(422, "El número de vidriera debe ser mayor que cero.")
    return f"{quinta_code}-V{number:03d}"


def parse_vidriera_code(value: str, quinta_code: str) -> int:
    code = value.strip().upper()
    match = VIDRIERA_CODE.fullmatch(code)
    expected = f"{quinta_code}-V001"
    if match is None or match.group(1) != quinta_code:
        raise DomainError(
            422,
            "El código de la vidriera debe usar el prefijo de su quinta, "
            f"como {expected}.",
        )
    number = int(match.group(2))
    if format_vidriera_code(quinta_code, number) != code:
        raise DomainError(
            422,
            "El código de la vidriera debe numerarse sin ceros de más, "
            f"con al menos tres dígitos. Ejemplo: {expected}.",
        )
    return number


def normalize_name(value: str) -> str:
    name = " ".join(value.strip().split())
    if not name:
        raise DomainError(422, "El nombre es obligatorio.")
    if len(name) > NAME_MAX_LENGTH:
        raise DomainError(422, "El nombre admite hasta 200 caracteres.")
    return name


def name_key(value: str) -> str:
    return normalize_name(value).casefold()


def normalize_optional_name(value: str | None) -> str | None:
    if value is None:
        return None
    name = " ".join(value.strip().split())
    if not name:
        return None
    if len(name) > NAME_MAX_LENGTH:
        raise DomainError(422, "El nombre admite hasta 200 caracteres.")
    return name


def optional_name_key(value: str | None) -> str | None:
    name = normalize_optional_name(value)
    if name is None:
        return None
    return name.casefold()


def normalize_notes(value: str | None) -> str | None:
    if value is None:
        return None
    notes = value.strip()
    if not notes:
        return None
    if len(notes) > NOTES_MAX_LENGTH:
        raise DomainError(422, "Las notas admiten hasta 4000 caracteres.")
    return notes


def display_cantero_code(vidriera_code: str, number: int) -> str:
    return f"{vidriera_code}-C{number}"
