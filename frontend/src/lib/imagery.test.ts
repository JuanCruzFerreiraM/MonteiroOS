import { describe, expect, it } from "vitest";

import {
  DOCUMENTED_WORLD_IMAGERY_ATTRIBUTION,
  IGN_ORTHOPHOTO_TILE_URL,
  geocodeSearchUrl,
  isEsriTokenError,
  isImageContentType,
  missingImageryConfig,
  nominatimSearchUrl,
  normalizeSearchQuery,
  openImageryConfig,
  parseGeocodeCandidates,
  parseNominatimResults,
  parseTileCoordinate,
  parseWorldImageryMetadata,
  worldImageryTileUrl,
} from "./imagery";

describe("imagery provider helpers", () => {
  it("describes a missing Esri key without exposing a secret", () => {
    const config = missingImageryConfig();

    expect(config.configured).toBe(false);
    expect(config.reason).toBe("missing_credentials");
    expect(config.message).toContain("ESRI_API_KEY");
    expect(config.tileUrl).toBeNull();
    expect(config.searchEnabled).toBe(false);
    expect(JSON.stringify(config)).not.toContain("secret-value");
  });

  it("uses the IGN orthophoto when Esri credentials are absent", () => {
    const config = openImageryConfig();

    expect(config.configured).toBe(true);
    expect(config.reason).toBe("ok");
    expect(config.tileUrl).toBe(IGN_ORTHOPHOTO_TILE_URL);
    expect(config.tileUrl).toContain("{z}/{y}/{x}");
    expect(config.minZoom).toBe(11);
    expect(config.maxZoom).toBe(20);
    expect(config.attribution).toContain("Instituto Geográfico Nacional");
    expect(config.searchEnabled).toBe(true);
    expect(config.searchAttribution).toContain("OpenStreetMap");
  });

  it("builds World Imagery requests without putting a token in the URL", () => {
    const tile = worldImageryTileUrl(12, 2345, 1456);
    const search = geocodeSearchUrl("Villa Elisa");

    expect(tile).toBe(
      "https://ibasemaps-api.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/12/2345/1456",
    );
    expect(tile).not.toContain("token");
    expect(search).toContain("forStorage=false");
    expect(search).toContain("sourceCountry=ARG");
    expect(search).not.toContain("ESRI_API_KEY");

    const places = nominatimSearchUrl("Villa Elisa");
    expect(places).toContain("nominatim.openstreetmap.org");
    expect(places).toContain("countrycodes=ar");
    expect(places).not.toContain("ESRI_API_KEY");
  });

  it("rejects tile indexes outside the web mercator grid", () => {
    expect(parseTileCoordinate("12", "2345", "1456")).toEqual({
      z: 12,
      y: 2345,
      x: 1456,
    });
    expect(parseTileCoordinate("2", "4", "0")).toBeNull();
    expect(parseTileCoordinate("-1", "0", "0")).toBeNull();
    expect(parseTileCoordinate("12", "a", "1")).toBeNull();
  });

  it("recognizes an Esri token error even when HTTP status is 200", () => {
    expect(
      isEsriTokenError({ error: { code: 499, message: "Token Required." } }),
    ).toBe(true);
    expect(isImageContentType("image/jpeg")).toBe(true);
    expect(isImageContentType("text/plain")).toBe(false);
  });

  it("reads attribution and zoom from World Imagery metadata", () => {
    const metadata = parseWorldImageryMetadata({
      copyrightText: "Esri, Maxar",
      tileInfo: { rows: 256, lods: [{ level: 0 }, { level: 18 }] },
    });

    expect(metadata).toEqual({
      attribution: "Esri, Maxar",
      maxZoom: 18,
      tileSize: 256,
    });
    expect(DOCUMENTED_WORLD_IMAGERY_ATTRIBUTION).toContain("Maxar");
  });

  it("keeps only finite WGS84 geocode candidates", () => {
    expect(normalizeSearchQuery("  Villa   Elisa ")).toBe("Villa Elisa");
    expect(normalizeSearchQuery(" ")).toBeNull();
    expect(
      parseGeocodeCandidates({
        candidates: [
          { address: "Villa Elisa", location: { x: -58.08, y: -34.86 } },
          { address: "Mal", location: { x: -58, y: -120 } },
        ],
      }),
    ).toEqual([{ label: "Villa Elisa", latitude: -34.86, longitude: -58.08 }]);
    expect(
      parseNominatimResults([
        {
          display_name: "Villa Elisa, Buenos Aires, Argentina",
          lat: "-34.851",
          lon: "-58.089",
        },
        { display_name: "Mal", lat: "no", lon: "-58" },
      ]),
    ).toEqual([
      {
        label: "Villa Elisa, Buenos Aires, Argentina",
        latitude: -34.851,
        longitude: -58.089,
      },
    ]);
  });
});
