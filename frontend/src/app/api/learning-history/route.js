import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]/route.js';
import dbConnect from '../../../lib/mongodb.js';
import LearningHistory from '../../../models/LearningHistory.js';

// Never cache this route — progress must always be fresh
export const dynamic = 'force-dynamic';

// GET /api/learning-history — fetch current user's history
export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    await dbConnect();
    const history = await LearningHistory.find({ userId: session.user.id })
      .sort({ lastAccessedAt: -1 })
      .limit(50);
    return NextResponse.json({ success: true, history });
  } catch (err) {
    console.error('GET learning-history error:', err);
    return NextResponse.json({ error: 'Failed to fetch history' }, { status: 500 });
  }
}

// DELETE /api/learning-history?id=xxx — remove a history entry
export async function DELETE(req) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { searchParams } = new URL(req.url);
    const id = searchParams.get('id');
    if (!id) return NextResponse.json({ error: 'id is required' }, { status: 400 });

    await dbConnect();
    await LearningHistory.findOneAndDelete({ _id: id, userId: session.user.id });
    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('DELETE learning-history error:', err);
    return NextResponse.json({ error: 'Failed to delete' }, { status: 500 });
  }
}

// POST /api/learning-history — upsert a history entry
export async function POST(req) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await req.json();
    const { videoUrl, courseTitle, courseSubtitle, totalLessons, completedLessons, completedLessonIds, lastLessonId } = body;

    if (!videoUrl) {
      return NextResponse.json({ error: 'videoUrl is required' }, { status: 400 });
    }

    await dbConnect();

    const setData = {
      courseTitle: courseTitle || 'Untitled Course',
      courseSubtitle: courseSubtitle || '',
      totalLessons: totalLessons || 0,
      completedLessons: completedLessons ?? 0,
      completedLessonIds: completedLessonIds ?? [],
      lastLessonId: lastLessonId ?? null,
      lastAccessedAt: new Date(),
    };

    await LearningHistory.findOneAndUpdate(
      { userId: session.user.id, videoUrl },
      {
        $set: setData,
        $setOnInsert: { createdAt: new Date() },
      },
      { upsert: true, new: true }
    );

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('POST learning-history error:', err);
    return NextResponse.json({ error: 'Failed to save history' }, { status: 500 });
  }
}
