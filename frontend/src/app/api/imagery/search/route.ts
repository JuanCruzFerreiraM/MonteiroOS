import { NextResponse } from "next/server";

import { searchPlaces } from "@/lib/imagery-server";
import { normalizeSearchQuery } from "@/lib/imagery";

export async function GET(request: Request) {
  const query = normalizeSearchQuery(
    new URL(request.url).searchParams.get("q") ?? "",
  );
  if (!query) {
    return NextResponse.json(
      { detail: "Escriba al menos dos caracteres para buscar un lugar." },
      { status: 422 },
    );
  }
  const result = await searchPlaces(query);
  if ("error" in result) {
    return NextResponse.json(
      { detail: result.error },
      { status: result.status },
    );
  }
  return NextResponse.json({ results: result.results });
}
