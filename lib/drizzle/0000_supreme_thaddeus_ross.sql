CREATE TABLE "games" (
	"id" text PRIMARY KEY NOT NULL,
	"visitor_id" text,
	"sentence" text NOT NULL,
	"word_count" integer NOT NULL,
	"difficulty" text NOT NULL,
	"wpm" real,
	"accuracy" real,
	"duration" real,
	"correct_count" integer,
	"error_count" integer,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "keystrokes" (
	"id" serial PRIMARY KEY NOT NULL,
	"game_id" text NOT NULL,
	"visitor_id" text,
	"key" text NOT NULL,
	"expected_key" text NOT NULL,
	"is_correct" integer NOT NULL,
	"shift_pressed" text,
	"timestamp" bigint NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "keystrokes" ADD CONSTRAINT "keystrokes_game_id_games_id_fk" FOREIGN KEY ("game_id") REFERENCES "public"."games"("id") ON DELETE cascade ON UPDATE no action;