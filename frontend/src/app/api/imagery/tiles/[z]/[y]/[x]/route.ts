import { NextResponse } from "next/server";

import { fetchImageryTile } from "@/lib/imagery-server";
import { parseTileCoordinate } from "@/lib/imagery";

export async function GET(
  _request: Request,
  context: { params: Promise<{ z: string; y: string; x: string }> },
) {
  const params = await context.params;
  const tile = parseTileCoordinate(params.z, params.y, params.x);
  if (!tile) {
    return NextResponse.json(
      { detail: "La tesela pedida no es válida." },
      { status: 400 },
    );
  }
  const result = await fetchImageryTile(tile.z, tile.y, tile.x);
  if ("error" in result) {
    return NextResponse.json({ detail: result.error }, { status: 502 });
  }
  return new NextResponse(result.bytes, {
    status: 200,
    headers: {
      "Content-Type": result.contentType,
      "Cache-Control": "private, max-age=3600",
    },
  });
}
