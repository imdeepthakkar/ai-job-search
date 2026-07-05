import { defineCommand } from "@bunli/core"
import { BASE_URL } from "../helpers.js"
import { parse } from "node-html-parser"

export const detail = defineCommand({
  name: "detail",
  description: "Full detail for a single job posting (by slug)",
  handler: async ({ positional, output }) => {
    const slug = positional[0]
    if (!slug) throw new Error("Slug is required")

    const url = `${BASE_URL}/job/${slug}`
    const response = await fetch(url)
    const html = await response.text()
    const root = parse(html)

    const ldJson = root.querySelector('script[type="application/ld+json"]')?.text
    if (!ldJson) throw new Error("Failed to parse JSON-LD from job page")

    const data = JSON.parse(ldJson)
    output({
      slug,
      url,
      ...data
    })
  },
})
