import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../auth/[...nextauth]/route.js';

const BACKEND = 'http://localhost:8000';
export const dynamic = 'force-dynamic';

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const res = await fetch(`${BACKEND}/exam/my-certificates?user_id=${session.user.id}`);
  const data = await res.json();
  if (!res.ok) return NextResponse.json({ error: data.detail || 'Failed' }, { status: res.status });
  return NextResponse.json(data);
}
