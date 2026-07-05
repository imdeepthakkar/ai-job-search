import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiPost } from "../helpers.js"

export const search = defineCommand({
  name: "search",
  description: "Search job listings with filters",
  options: {
    text: option(z.string().optional().describe("Free-text keyword search")),
    category: option(z.coerce.number().optional().describe("Category ID")),
    "jobtitle-id": option(z.coerce.number().optional().describe("Job title ID")),
    municipality: option(z.string().optional().describe("Municipality name")),
    zip: option(z.string().optional().describe("Zip code")),
    region: option(z.string().optional().describe("Region name")),
    "job-type": option(z.string().optional().describe("Comma-separated job types")),
    page: option(z.coerce.number().default(1).describe("Page number")),
    limit: option(z.coerce.number().optional().describe("Cap total results")),
  },
  handler: async ({ flags, output }) => {
    const body: any = {
      jobTypes: flags["job-type"] ? flags["job-type"].split(",") : [],
      filters: [],
      locationMode: "Text",
      distance: 50,
    }

    if (flags.text) body.filters.push({ type: "freetext", value: flags.text, displayText: flags.text })
    if (flags.category) body.filters.push({ type: "category", value: flags.category, displayText: flags.category.toString() })
    if (flags["jobtitle-id"]) body.filters.push({ type: "jobtitle", value: flags["jobtitle-id"], displayText: flags["jobtitle-id"].toString() })
    if (flags.municipality) body.filters.push({ type: "municipality", value: flags.municipality, displayText: flags.municipality })
    if (flags.zip) body.filters.push({ type: "zip", value: flags.zip, displayText: flags.zip })
    if (flags.region) body.filters.push({ type: "region", value: flags.region, displayText: flags.region })

    const data = await apiPost<any>(`/api/jobsearch/search/${flags.page}`, body)
    
    let results = data.items || []
    if (flags.limit) results = results.slice(0, flags.limit)

    output({
      meta: {
        currentPage: data.currentPage,
        totalItems: data.totalItems,
        itemsPrPage: data.itemsPrPage,
        totalPages: data.totalPages,
      },
      results,
    })
  },
})
