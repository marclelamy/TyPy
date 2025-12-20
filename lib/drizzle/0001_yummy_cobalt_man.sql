ALTER TABLE "games" ADD COLUMN "config" jsonb;--> statement-breakpoint
ALTER TABLE "games" DROP COLUMN "word_count";--> statement-breakpoint
ALTER TABLE "games" DROP COLUMN "difficulty";