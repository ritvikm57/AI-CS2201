import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ message: "Hello from Next.js API!" });
}

export async function POST(request) {
  const body = await request.json();
  return NextResponse.json({ received: body });
}
