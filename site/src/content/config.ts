import { defineCollection, z } from "astro:content";

const chapters = defineCollection({
  type: "content",
  schema: z.object({
    order: z.number(),
    title: z.string(),
    dateStart: z.string(),
    dateEnd: z.string(),
    cover: z.string().optional(),
    summary: z.string().optional()
  })
});

export const collections = { chapters };
