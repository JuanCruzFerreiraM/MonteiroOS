import "server-only";

import {
  geocodeSearchUrl,
  isEsriTokenError,
  isImageContentType,
  missingImageryConfig,
  nominatimSearchUrl,
  openImageryConfig,
  parseGeocodeCandidates,
  parseNominatimResults,
  parseWorldImageryMetadata,
  providerErrorConfig,
  readyImageryConfig,
  rejectedImageryConfig,
  type ImageryPublicConfig,
  type PlaceSearchResult,
  worldImageryMetadataUrl,
  worldImageryTileUrl,
} from "./imagery";

const TILE_BYTE_LIMIT = 2_000_000;

export function esriApiKey(): string {
  return process.env.ESRI_API_KEY?.trim() ?? "";
}

export async function loadImageryConfig(): Promise<ImageryPublicConfig> {
  const apiKey = esriApiKey();
  if (!apiKey) {
    return openImageryConfig();
  }
  try {
    const response = await fetch(worldImageryMetadataUrl(), {
      headers: esriHeaders(apiKey),
      cache: "no-store",
    });
    const payload: unknown = await response.json().catch(() => null);
    if (isEsriTokenError(payload)) {
      return rejectedImageryConfig();
    }
    const metadata = parseWorldImageryMetadata(payload);
    if (!metadata) {
      return providerErrorConfig();
    }
    return readyImageryConfig(metadata);
  } catch {
    return providerErrorConfig();
  }
}

export async function fetchImageryTile(
  z: number,
  y: number,
  x: number,
): Promise<{ bytes: ArrayBuffer; contentType: string } | { error: string }> {
  const apiKey = esriApiKey();
  if (!apiKey) {
    return {
      error: missingImageryConfig().message ?? "Falta la clave de Esri.",
    };
  }
  try {
    const response = await fetch(worldImageryTileUrl(z, y, x), {
      headers: esriHeaders(apiKey),
      cache: "no-store",
    });
    const contentType = response.headers.get("content-type");
    if (!response.ok || !isImageContentType(contentType)) {
      return { error: "No se pudo obtener la imagen satelital." };
    }
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength === 0 || bytes.byteLength > TILE_BYTE_LIMIT) {
      return { error: "La imagen satelital recibida no se puede mostrar." };
    }
    return { bytes, contentType: contentType ?? "image/jpeg" };
  } catch {
    return { error: "No se pudo contactar el servicio de imágenes." };
  }
}

export async function searchPlaces(
  query: string,
): Promise<
  { results: PlaceSearchResult[] } | { error: string; status: number }
> {
  const apiKey = esriApiKey();
  if (!apiKey) {
    return searchNominatim(query);
  }
  try {
    const response = await fetch(geocodeSearchUrl(query), {
      headers: esriHeaders(apiKey),
      cache: "no-store",
    });
    const payload: unknown = await response.json().catch(() => null);
    if (isEsriTokenError(payload)) {
      return {
        error: rejectedImageryConfig().message ?? "Esri rechazó la clave.",
        status: 502,
      };
    }
    if (!response.ok) {
      return { error: "La búsqueda geográfica no respondió.", status: 502 };
    }
    return { results: parseGeocodeCandidates(payload) };
  } catch {
    return {
      error: "No se pudo contactar el servicio de búsqueda.",
      status: 502,
    };
  }
}

const NOMINATIM_USER_AGENT = "MonteiroOS/1.0 (mapa de produccion local)";

async function searchNominatim(
  query: string,
): Promise<
  { results: PlaceSearchResult[] } | { error: string; status: number }
> {
  try {
    const response = await fetch(nominatimSearchUrl(query), {
      headers: {
        "User-Agent": NOMINATIM_USER_AGENT,
        "Accept-Language": "es",
      },
      cache: "no-store",
    });
    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      return { error: "La búsqueda geográfica no respondió.", status: 502 };
    }
    return { results: parseNominatimResults(payload) };
  } catch {
    return {
      error: "No se pudo contactar el servicio de búsqueda.",
      status: 502,
    };
  }
}

function esriHeaders(apiKey: string): Headers {
  return new Headers({ Authorization: `Bearer ${apiKey}` });
}
