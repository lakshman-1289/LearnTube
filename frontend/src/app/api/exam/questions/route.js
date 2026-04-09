import { NextResponse } from 'next/server';
const BACKEND = 'http://localhost:8000';
export const dynamic = 'force-dynamic';

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const videoId = searchParams.get('videoId');
  if (!videoId) return NextResponse.json({ error: 'Missing videoId' }, { status: 400 });

  const res = await fetch(`${BACKEND}/exam/questions/${videoId}`);
  const data = await res.json();
  if (!res.ok) return NextResponse.json({ error: data.detail || 'Failed' }, { status: res.status });
  return NextResponse.json(data);
}
