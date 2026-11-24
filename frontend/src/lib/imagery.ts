export const IMAGERY_PROVIDER_ID = "esri-world-imagery";

export const IGN_PROVIDER_ID = "ign-orthophoto";

export type ImageryProviderId =
  | typeof IMAGERY_PROVIDER_ID
  | typeof IGN_PROVIDER_ID;

/**
 * Instituto Geográfico Nacional orthophoto mosaic.
 * GeoWebCache only serves zoom 11 through 20 for this layer. Lower and
 * higher levels answer with an HTML error, which Leaflet would treat as a
 * broken tile.
 */
export const IGN_ORTHOPHOTO_TILE_URL =
  "https://imagenes.ign.gob.ar/geoserver/gwc/service/wmts/rest/mosaicos_vuelos/EPSG:3857/EPSG:3857:{z}/{y}/{x}?format=image/png";

export const IGN_ORTHOPHOTO_ATTRIBUTION =
  '<a href="https://www.ign.gob.ar/">Instituto Geográfico Nacional de la República Argentina</a>';

export const IGN_ORTHOPHOTO_MIN_ZOOM = 11;

export const IGN_ORTHOPHOTO_MAX_ZOOM = 20;

export const OPENSTREETMAP_SEARCH_ATTRIBUTION = "Lugares: © OpenStreetMap";

export const WORLD_IMAGERY_SERVICE =
  "https://ibasemaps-api.arcgis.com/arcgis/rest/services/World_Imagery/MapServer";

/**
 * Camera used only when a quinta has no boundary yet.
 * It frames the La Plata area so the operator can move toward Villa Elisa
 * or Arturo Seguí. It is not a production record.
 */
export const INITIAL_CAMERA = {
  latitude: -34.9,
  longitude: -58.1,
  zoom: 12,
} as const;

export const DOCUMENTED_WORLD_IMAGERY_ATTRIBUTION =
  "Esri, Maxar, Earthstar Geographics, and the GIS User Community";

export type ImageryReason =
  "ok" | "missing_credentials" | "rejected_credentials" | "provider_error";

export type ImageryPublicConfig = {
  providerId: ImageryProviderId;
  configured: boolean;
  reason: ImageryReason;
  message: string | null;
  tileUrl: string | null;
  tileSize: number;
  zoomOffset: number;
  minZoom: number;
  maxZoom: number;
  attribution: string | null;
  searchEnabled: boolean;
  searchAttribution: string | null;
};

export type PlaceSearchResult = {
  label: string;
  latitude: number;
  longitude: number;
};

const MISSING_CREDENTIALS_MESSAGE =
  "Falta la clave de Esri (ESRI_API_KEY) en el servidor. " +
  "Sin esa clave no se puede pedir la imagen satelital. " +
  "Los límites ya guardados no se borran.";

const REJECTED_CREDENTIALS_MESSAGE =
  "Esri rechazó la clave de imágenes. Revise ESRI_API_KEY y que tenga " +
  "permiso para mapas base y geocodificación. Los polígonos guardados siguen intactos.";

const PROVIDER_ERROR_MESSAGE =
  "No se pudo consultar el servicio de imágenes de Esri. " +
  "Los límites guardados no se modificaron.";

export function missingImageryConfig(): ImageryPublicConfig {
  return {
    providerId: IMAGERY_PROVIDER_ID,
    configured: false,
    reason: "missing_credentials",
    message: MISSING_CREDENTIALS_MESSAGE,
    tileUrl: null,
    tileSize: 256,
    zoomOffset: 0,
    minZoom: 2,
    maxZoom: 19,
    attribution: null,
    searchEnabled: false,
    searchAttribution: null,
  };
}

export function openImageryConfig(): ImageryPublicConfig {
  return {
    providerId: IGN_PROVIDER_ID,
    configured: true,
    reason: "ok",
    message: null,
    tileUrl: IGN_ORTHOPHOTO_TILE_URL,
    tileSize: 256,
    zoomOffset: 0,
    minZoom: IGN_ORTHOPHOTO_MIN_ZOOM,
    maxZoom: IGN_ORTHOPHOTO_MAX_ZOOM,
    attribution: IGN_ORTHOPHOTO_ATTRIBUTION,
    searchEnabled: true,
    searchAttribution: OPENSTREETMAP_SEARCH_ATTRIBUTION,
  };
}

export function rejectedImageryConfig(): ImageryPublicConfig {
  return {
    ...missingImageryConfig(),
    reason: "rejected_credentials",
    message: REJECTED_CREDENTIALS_MESSAGE,
  };
}

export function providerErrorConfig(): ImageryPublicConfig {
  return readyImageryConfig({
    attribution: DOCUMENTED_WORLD_IMAGERY_ATTRIBUTION,
    maxZoom: 19,
    tileSize: 256,
    message: PROVIDER_ERROR_MESSAGE,
  });
}

export function readyImageryConfig(options: {
  attribution: string;
  maxZoom: number;
  tileSize: number;
  message?: string | null;
}): ImageryPublicConfig {
  return {
    providerId: IMAGERY_PROVIDER_ID,
    configured: true,
    reason: options.message ? "provider_error" : "ok",
    message: options.message ?? null,
    tileUrl: "/api/imagery/tiles/{z}/{y}/{x}",
    tileSize: options.tileSize,
    zoomOffset: 0,
    minZoom: 2,
    maxZoom: options.maxZoom,
    attribution: `Powered by Esri | ${options.attribution}`,
    searchEnabled: true,
    searchAttribution: null,
  };
}

export function parseTileCoordinate(
  z: string,
  y: string,
  x: string,
): { z: number; y: number; x: number } | null {
  if (!isTileIndex(z) || !isTileIndex(y) || !isTileIndex(x)) {
    return null;
  }
  const zoom = Number(z);
  const row = Number(y);
  const column = Number(x);
  if (zoom > 23) {
    return null;
  }
  const limit = 2 ** zoom;
  if (row >= limit || column >= limit) {
    return null;
  }
  return { z: zoom, y: row, x: column };
}

export function worldImageryTileUrl(z: number, y: number, x: number): string {
  return `${WORLD_IMAGERY_SERVICE}/tile/${z}/${y}/${x}`;
}

export function worldImageryMetadataUrl(): string {
  return `${WORLD_IMAGERY_SERVICE}?f=json`;
}

export function nominatimSearchUrl(query: string): string {
  const params = new URLSearchParams({
    q: query,
    format: "jsonv2",
    countrycodes: "ar",
    limit: "5",
    addressdetails: "0",
    viewbox: "-58.6,-34.6,-57.7,-35.3",
    bounded: "0",
  });
  return `https://nominatim.openstreetmap.org/search?${params.toString()}`;
}

export function geocodeSearchUrl(query: string): string {
  const params = new URLSearchParams({
    f: "json",
    singleLine: query,
    sourceCountry: "ARG",
    location: `${INITIAL_CAMERA.longitude},${INITIAL_CAMERA.latitude}`,
    outSR: "4326",
    maxLocations: "5",
    forStorage: "false",
    langCode: "es",
  });
  return (
    "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/" +
    `findAddressCandidates?${params.toString()}`
  );
}

export function normalizeSearchQuery(value: string): string | null {
  const query = value.trim().replace(/\s+/g, " ");
  if (query.length < 2 || query.length > 120) {
    return null;
  }
  return query;
}

export function isImageContentType(value: string | null): boolean {
  return value?.toLowerCase().startsWith("image/") ?? false;
}

export function isEsriTokenError(payload: unknown): boolean {
  if (!isRecord(payload) || !isRecord(payload.error)) {
    return false;
  }
  const code = payload.error.code;
  const message = payload.error.message;
  if (code === 498 || code === 499 || code === 401 || code === 403) {
    return true;
  }
  return typeof message === "string" && /token/i.test(message);
}

export function parseWorldImageryMetadata(payload: unknown): {
  attribution: string;
  maxZoom: number;
  tileSize: number;
} | null {
  if (!isRecord(payload) || isEsriTokenError(payload)) {
    return null;
  }
  const attribution =
    typeof payload.copyrightText === "string"
      ? payload.copyrightText.trim()
      : "";
  if (!attribution) {
    return null;
  }
  const tileInfo = isRecord(payload.tileInfo) ? payload.tileInfo : null;
  const rows =
    tileInfo && typeof tileInfo.rows === "number" ? tileInfo.rows : 256;
  const lods = tileInfo && Array.isArray(tileInfo.lods) ? tileInfo.lods : [];
  const levels = lods
    .map((lod) =>
      isRecord(lod) && typeof lod.level === "number" ? lod.level : null,
    )
    .filter((level): level is number => level !== null);
  const maxZoom = levels.length > 0 ? Math.max(...levels) : 19;
  const tileSize = rows === 512 ? 512 : 256;
  return { attribution, maxZoom, tileSize };
}

export function parseNominatimResults(payload: unknown): PlaceSearchResult[] {
  if (!Array.isArray(payload)) {
    return [];
  }
  const results: PlaceSearchResult[] = [];
  for (const item of payload) {
    if (!isRecord(item) || typeof item.display_name !== "string") {
      continue;
    }
    const latitude = numberOrNull(item.lat);
    const longitude = numberOrNull(item.lon);
    if (latitude === null || longitude === null) {
      continue;
    }
    if (
      longitude < -180 ||
      longitude > 180 ||
      latitude < -90 ||
      latitude > 90
    ) {
      continue;
    }
    const label = item.display_name.trim();
    if (!label) {
      continue;
    }
    results.push({ label, latitude, longitude });
  }
  return results;
}

export function parseGeocodeCandidates(payload: unknown): PlaceSearchResult[] {
  if (!isRecord(payload) || !Array.isArray(payload.candidates)) {
    return [];
  }
  const results: PlaceSearchResult[] = [];
  for (const candidate of payload.candidates) {
    if (!isRecord(candidate) || typeof candidate.address !== "string") {
      continue;
    }
    if (!isRecord(candidate.location)) {
      continue;
    }
    const longitude = candidate.location.x;
    const latitude = candidate.location.y;
    if (typeof longitude !== "number" || typeof latitude !== "number") {
      continue;
    }
    if (
      !Number.isFinite(longitude) ||
      !Number.isFinite(latitude) ||
      longitude < -180 ||
      longitude > 180 ||
      latitude < -90 ||
      latitude > 90
    ) {
      continue;
    }
    const label = candidate.address.trim();
    if (!label) {
      continue;
    }
    results.push({ label, latitude, longitude });
  }
  return results;
}

function numberOrNull(value: unknown): number | null {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function isTileIndex(value: string): boolean {
  return /^\d{1,8}$/.test(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
