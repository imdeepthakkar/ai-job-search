import { defineCommand, option } from "@bunli/core"
import { z } from "zod"
import { apiFetch } from "../helpers.js"

export const search = defineCommand({
  name: "search",
  description: "Search for job ads with filters",
  options: {
    "search-string": option(z.string().optional().describe("Free-text keyword search")),
    region: option(z.string().optional().describe("Region filter")),
    "postal-code": option(z.string().optional().describe("Postal code")),
    radius: option(z.coerce.number().default(50).describe("Radius in km")),
    "work-hours": option(z.string().optional().describe("FullTime or PartTime")),
    duration: option(z.string().optional().describe("Permanent or Temporary")),
    "job-type": option(z.string().optional().describe("Announcement type")),
    "occupation-area": option(z.string().optional().describe("Occupation area identifier")),
    "occupation-group": option(z.string().optional().describe("Occupation group identifier")),
    page: option(z.coerce.number().default(1).describe("Page number")),
    "per-page": option(z.coerce.number().default(10).describe("Results per page")),
    limit: option(z.coerce.number().optional().describe("Cap total results")),
    order: option(z.string().default("PublicationDate").describe("Sort order")),
  },
  handler: async ({ flags, output }) => {
    const params: Record<string, string> = {
      PageNumber: flags.page.toString(),
      ResultsPerPage: flags["per-page"].toString(),
      Order: flags.order,
      IncludeFacets: "false",
    }

    if (flags["search-string"]) params.SearchString = flags["search-string"]
    if (flags.region) params.Region = flags.region
    if (flags["postal-code"]) {
      params.PostalCode = flags["postal-code"]
      params.Radius = flags.radius.toString()
    }
    if (flags["work-hours"]) params.WorkHours = flags["work-hours"]
    if (flags.duration) params.EmploymentDuration = flags.duration
    if (flags["job-type"]) params.JobType = flags["job-type"]
    if (flags["occupation-area"]) params.OccupationAreaIdentifier = flags["occupation-area"]
    if (flags["occupation-group"]) params.OccupationGroupIdentifier = flags["occupation-group"]

    const data = await apiFetch<any>("/FindJob/Search", params)
    
    let results = data.results || data.JobAds || []
    if (flags.limit) {
      results = results.slice(0, flags.limit)
    }

    output({
      meta: {
        totalJobAdCount: data.TotalJobAdCount,
        pageNumber: flags.page,
        resultsPerPage: flags["per-page"],
        searchString: flags["search-string"],
      },
      results,
    })
  },
})
