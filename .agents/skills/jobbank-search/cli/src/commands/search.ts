import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { rssFetch, parseRssDescription, extractJobIdFromUrl } from "../helpers"

export const search = defineCommand({
  name: "search",
  description: "Search job listings via RSS feed",
  options: {
    key: option(z.string().optional().describe("Keyword search")),
    exclude: option(z.string().optional().describe("Exclude keywords")),
    type: option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Job type code")),
    education: option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Education field code")),
    location: option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Region code")),
    "work-area": option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Work area code")),
    industry: option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Industry code")),
    "suitable-for": option(z.preprocess(v => Array.isArray(v) ? v : [v], z.array(z.coerce.number())).optional().describe("Suitable-for code")),
    company: option(z.coerce.number().optional().describe("Company ID")),
    remote: option(z.string().optional().describe("Remote work: helt or delvist")),
    since: option(z.string().optional().describe("Posted on or after YYYY-MM-DD")),
    limit: option(z.coerce.number().optional().describe("Cap total results")),
  },
  handler: async ({ flags, output }) => {
    const params: Record<string, string | string[]> = {}
    if (flags.key) params.key = flags.key
    if (flags.exclude) params.antikey = flags.exclude
    if (flags.type) params.cvtype = flags.type.map(String)
    if (flags.education) params.udd = flags.education.map(String)
    if (flags.location) params.amt = flags.location.map(String)
    if (flags["work-area"]) params.erf = flags["work-area"].map(String)
    if (flags.industry) params.branche = flags.industry.map(String)
    if (flags["suitable-for"]) params.andet = flags["suitable-for"].map(String)
    if (flags.company) params.virk = flags.company.toString()
    if (flags.remote) params.fjernarbejde = flags.remote
    if (flags.since) params.oprettet = flags.since

    const items = await rssFetch(params)
    
    const results = items.map(item => {
      const parsed = parseRssDescription(item.description)
      return {
        id: extractJobIdFromUrl(item.link),
        title: item.title,
        company: parsed.company,
        location: parsed.location,
        jobType: parsed.jobType,
        description: item.description,
        url: item.link,
        posted: item.pubDate,
        deadline: parsed.deadline
      }
    })

    output({
      meta: { total: results.length },
      results: flags.limit ? results.slice(0, flags.limit) : results
    })
  },
})
