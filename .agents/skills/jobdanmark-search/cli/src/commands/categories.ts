import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const categories = defineCommand({
  name: "categories",
  description: "List all job categories with live counts",
  options: {
    limit: option(z.coerce.number().optional().describe("Cap total results")),
  },
  handler: async ({ flags, output }) => {
    const data = await apiFetch<any[]>("/api/categorycount/getcounts")
    output(flags.limit ? data.slice(0, flags.limit) : data)
  },
})
