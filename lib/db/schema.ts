import { pgTable, text, integer, real, bigint, timestamp, serial, jsonb } from 'drizzle-orm/pg-core';
import type { GameConfig } from '@/types/game';

export const games = pgTable('games', {
    id: text('id').primaryKey(),
    visitorId: text('visitor_id'),
    sentence: text('sentence').notNull(),
    config: jsonb('config').$type<GameConfig>(),
    wpm: real('wpm'),
    accuracy: real('accuracy'),
    duration: real('duration'), // in milliseconds
    correctCount: integer('correct_count'),
    errorCount: integer('error_count'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const keystrokes = pgTable('keystrokes', {
    id: serial('id').primaryKey(),
    gameId: text('game_id').notNull().references(() => games.id, { onDelete: 'cascade' }),
    visitorId: text('visitor_id'),
    key: text('key').notNull(),
    expectedKey: text('expected_key').notNull(),
    isCorrect: integer('is_correct').notNull(), // 0 or 1 for boolean
    shiftPressed: text('shift_pressed'), // 'left' | 'right' | null
    timestamp: bigint('timestamp', { mode: 'number' }).notNull(), // milliseconds since epoch
    createdAt: timestamp('created_at').defaultNow().notNull(),
});
