import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const suggestions = defineCommand({
  name: "suggestions",
  description: "Typeahead suggestions",
  options: {
    query: option(z.string().describe("Partial search string"), { short: "q" }),
    limit: option(z.coerce.number().optional().describe("Cap results")),
  },
  handler: async ({ flags, output }) => {
    const data = await apiFetch<any>("/FindJob/GetTypeaheadSuggestions", { query: flags.query })
    output(flags.limit ? data.slice(0, flags.limit) : data)
  },
})
