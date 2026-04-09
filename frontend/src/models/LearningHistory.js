import mongoose from 'mongoose';

const LearningHistorySchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  videoUrl: { type: String, required: true },
  courseTitle: { type: String, default: 'Untitled Course' },
  courseSubtitle: { type: String, default: '' },
  totalLessons: { type: Number, default: 0 },
  completedLessons: { type: Number, default: 0 },
  completedLessonIds: { type: [Number], default: [] },
  lastLessonId: { type: Number, default: null },
  lastAccessedAt: { type: Date, default: Date.now },
  createdAt: { type: Date, default: Date.now },
});

// Unique per user+video — upsert on each visit
LearningHistorySchema.index({ userId: 1, videoUrl: 1 }, { unique: true });

export default mongoose.models.LearningHistory ||
  mongoose.model('LearningHistory', LearningHistorySchema);
