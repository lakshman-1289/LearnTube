import { NextResponse } from 'next/server';

const BACKEND = 'http://localhost:8000';

export async function POST(req) {
  try {
    const body = await req.json();
    const { url } = body;
    if (!url) {
      return NextResponse.json({ error: 'Missing YouTube URL' }, { status: 400 });
    }

    // Start an async background job — returns immediately with job_id
    const response = await fetch(`${BACKEND}/generate-course-async`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: err.detail || `Backend error ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json(); // { status: "processing", job_id: "..." }
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ error: 'Failed to reach backend', details: err.message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ error: 'Use POST' }, { status: 405 });
}
