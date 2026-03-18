import { NextResponse } from "next/server";
import { verifyCaptcha } from "@/lib/captcha-engine";

export async function POST(request) {
  const body = await request.json();
  const { id, answer } = body;

  if (!id || answer === undefined) {
    return NextResponse.json(
      { success: false, message: "Missing id or answer" },
      { status: 400 }
    );
  }

  const result = verifyCaptcha(id, answer);
  return NextResponse.json(result);
}
