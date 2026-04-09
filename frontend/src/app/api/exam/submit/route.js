import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../auth/[...nextauth]/route.js';

const BACKEND = 'http://localhost:8000';

export async function POST(req) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const body = await req.json();
  const res = await fetch(`${BACKEND}/exam/submit-exam`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...body,
      user_id: session.user.id,
      user_name: session.user.name || session.user.email?.split('@')[0] || 'Learner',
    }),
  });
  const data = await res.json();
  if (!res.ok) return NextResponse.json({ error: data.detail || 'Failed' }, { status: res.status });
  return NextResponse.json(data);
}
