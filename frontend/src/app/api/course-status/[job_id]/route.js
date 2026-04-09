import { NextResponse } from 'next/server';

const BACKEND = 'http://localhost:8000';

export async function GET(req, { params }) {
  try {
    const { job_id } = await params;
    const response = await fetch(`${BACKEND}/course-status/${job_id}`);

    if (!response.ok) {
      return NextResponse.json({ error: `Backend error ${response.status}` }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ error: 'Failed to reach backend', details: err.message }, { status: 500 });
  }
}
