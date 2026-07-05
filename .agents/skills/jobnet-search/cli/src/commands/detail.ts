import { defineCommand } from "@bunli/core"
import { apiFetch, stripHtml } from "../helpers.js"

export const detail = defineCommand({
  name: "detail",
  description: "Full detail for a single job ad",
  handler: async ({ positional, format, output }) => {
    const id = positional[0]
    if (!id) throw new Error("Job ID is required")

    const data = await apiFetch<any>(`/FindJob/JobAdDetails/${id}`)
    
    if (format === "plain" && data.body) {
      data.body = stripHtml(data.body)
    }

    output(data)
  },
})
