import { createInsertSchema } from "drizzle-zod";
import { integer, pgTable, real, serial, text, timestamp, uniqueIndex, boolean } from "drizzle-orm/pg-core";
import { z } from "zod/v4";

export const itemsTable = pgTable("findit_items", {
  id: serial("id").primaryKey(),
  type: text("type").notNull(),
  reporter: text("reporter").notNull(),
  title: text("title").notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  location: text("location").notNull(),
  itemDate: timestamp("item_date", { withTimezone: true }).notNull(),
  photoUrl: text("photo_url"),
  privateDetail: text("private_detail").notNull(),
  status: text("status").notNull().default("OPEN"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const matchesTable = pgTable(
  "findit_matches",
  {
    id: serial("id").primaryKey(),
    lostItemId: integer("lost_item_id").notNull().references(() => itemsTable.id, { onDelete: "cascade" }),
    foundItemId: integer("found_item_id").notNull().references(() => itemsTable.id, { onDelete: "cascade" }),
    score: real("score").notNull(),
    verified: boolean("verified").notNull().default(false),
    lostConfirmed: boolean("lost_confirmed").notNull().default(false),
    foundConfirmed: boolean("found_confirmed").notNull().default(false),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    uniqueIndex("findit_matches_lost_found_unique").on(table.lostItemId, table.foundItemId),
  ],
);

export const messagesTable = pgTable("findit_messages", {
  id: serial("id").primaryKey(),
  matchId: integer("match_id").notNull().references(() => matchesTable.id, { onDelete: "cascade" }),
  role: text("role").notNull(),
  senderName: text("sender_name").notNull(),
  text: text("text").notNull(),
  sentAt: timestamp("sent_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertItemSchema = createInsertSchema(itemsTable).omit({
  id: true,
  status: true,
  createdAt: true,
});
export const insertMatchSchema = createInsertSchema(matchesTable).omit({ id: true, createdAt: true });
export const insertMessageSchema = createInsertSchema(messagesTable).omit({ id: true, sentAt: true });

export type InsertFindItItem = z.infer<typeof insertItemSchema>;
export type FindItItem = typeof itemsTable.$inferSelect;
export type InsertFindItMatch = z.infer<typeof insertMatchSchema>;
export type FindItMatch = typeof matchesTable.$inferSelect;
export type InsertFindItMessage = z.infer<typeof insertMessageSchema>;
export type FindItMessage = typeof messagesTable.$inferSelect;
