import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { htmlFetch, parseJobCards, parseHitCount, BASE_URL } from "../helpers.js"

export const search = defineCommand({
  name: "search",
  description: "Search for job listings",
  options: {
    query: option(z.string().describe("Keyword search query").optional(), {
      short: "q",
    }),
    page: option(z.coerce.number().default(1).describe("Page number")),
    jobage: option(z.coerce.number().default(9999).describe("Max age of posting in days")),
    sort: option(z.enum(["score", "date"]).default("score").describe("Sort order")),
    limit: option(z.coerce.number().optional().describe("Cap total results")),
  },
  handler: async ({ flags, output }) => {
    const params: Record<string, string> = {
      q: flags.query || "",
      page: flags.page.toString(),
      sort: flags.sort,
    }
    if (flags.jobage !== 9999) {
      params.jobage = flags.jobage.toString()
    }

    const qs = new URLSearchParams(params)
    const url = `${BASE_URL}/jobsoegning?${qs.toString()}`

    const html = await htmlFetch(url)

    // Fallback for null data or missing properties
    if (!html) {
        output({ meta: { total: 0, page: flags.page, perPage: 20 }, results: [] })
        return
    }

    // Extract Stash object from HTML
    const stashMatch = html.match(/var Stash = (\{.*?\});/s)
    if (!stashMatch) {
        // Fallback to old regex parsing if Stash is missing
        const results = parseJobCards(html)
        const total = parseHitCount(html) || results.length
        output({ meta: { total, page: flags.page, perPage: 20 }, results })
        return
    }

    try {
        const stash = JSON.parse(stashMatch[1])
        const resultApp = stash?.["jobsearch/result_app"] || stash?.jobsearch?.result_app
        const searchResponse = resultApp?.storeData?.searchResponse
        const rawResults = searchResponse?.results || []
        const total = searchResponse?.hitcount || rawResults.length

        // Combine all HTML snippets from the JSON results for the parser
        const combinedHtml = rawResults.map((r: any) => r.html).filter(Boolean).join("\n")
        const results = parseJobCards(combinedHtml)

        output({
          meta: {
            total,
            page: flags.page,
            perPage: 20,
          },
          results: flags.limit ? results.slice(0, flags.limit) : results,
        })
    } catch (e) {
        // Fallback to old regex parsing on error
        const results = parseJobCards(html)
        output({ meta: { total: results.length, page: flags.page, perPage: 20 }, results })
    }
  },
})

