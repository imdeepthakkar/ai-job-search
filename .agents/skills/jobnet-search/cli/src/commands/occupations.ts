import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const occupations = defineCommand({
  name: "occupations",
  description: "Search occupation types",
  options: {
    "search-string": option(z.string().describe("Search term"), { short: "q" }),
    "per-page": option(z.coerce.number().default(10).describe("Max results")),
  },
  handler: async ({ flags, output }) => {
    const params = {
      searchString: flags["search-string"],
      perPage: flags["per-page"].toString(),
    }
    const data = await apiFetch<any>("/OccupationSearch", params)
    output(data)
  },
})
