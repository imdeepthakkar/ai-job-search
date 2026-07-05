import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const locations = defineCommand({
  name: "locations",
  description: "Suggest location filters",
  options: {
    query: option(z.string().describe("Location text to search"), { short: "q" }),
    limit: option(z.coerce.number().optional().describe("Cap total suggestions")),
  },
  handler: async ({ flags, output }) => {
    const data = await apiFetch<any[]>("/api/search/locations", { q: flags.query || "" })
    output(flags.limit ? data.slice(0, flags.limit) : data)
  },
})
