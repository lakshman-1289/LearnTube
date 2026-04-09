import { NextResponse } from 'next/server';
const BACKEND = 'http://localhost:8000';
export const dynamic = 'force-dynamic';

export async function GET(req, { params }) {
  const { id } = params;
  const res = await fetch(`${BACKEND}/exam/certificate/${id}`);
  const data = await res.json();
  if (!res.ok) return NextResponse.json({ error: data.detail || 'Not found' }, { status: res.status });
  return NextResponse.json(data);
}
