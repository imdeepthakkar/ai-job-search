import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const autocomplete = defineCommand({
  name: "autocomplete",
  description: "Suggest job titles and categories",
  options: {
    query: option(z.string().describe("Search text to autocomplete"), { short: "q" }),
    limit: option(z.coerce.number().optional().describe("Cap total suggestions")),
  },
  handler: async ({ flags, output }) => {
    const data = await apiFetch<any[]>("/api/search/autocomplete", { q: flags.query || "" })
    output(flags.limit ? data.slice(0, flags.limit) : data)
  },
})
