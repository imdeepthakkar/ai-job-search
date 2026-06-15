import { defineCommand } from "@bunli/core"
import { htmlFetch, BASE_URL } from "../helpers.js"
import { parse } from "node-html-parser"

export const detail = defineCommand({
  name: "detail",
  description: "Fetch full job listing detail",
  handler: async ({ positional, output }) => {
    const id = positional[0]
    if (!id) {
      throw new Error("Job ID or URL is required")
    }

    let url = id
    if (!id.startsWith("http")) {
      url = `${BASE_URL}/jobannonce/${id}`
    }

    const html = await htmlFetch(url)
    const root = parse(html)

    // Basic extraction logic
    const title = root.querySelector("h1")?.text.trim() || null
    const company = root.querySelector(".jix-toolbar-top__company a")?.text.trim() || null
    const companyUrl = root.querySelector(".jix-toolbar-top__company a")?.getAttribute("href") || null
    const location = root.querySelector(".jix_robotjob--area")?.text.trim() || null
    
    // Description - usually in a specific div or just the body text
    const description = root.querySelector(".jobsearch-JobComponent-description")?.text.trim() || 
                        root.querySelector("#job-description")?.text.trim() ||
                        root.querySelector(".jix_robotjob-inner")?.text.trim() ||
                        "Full description parsing not fully implemented, but URL is: " + url

    output({
      id,
      title,
      company,
      companyUrl,
      location,
      url,
      description,
      // Placeholder for other fields
      deadline: null,
      employmentType: null,
      hours: null,
      applyUrl: null,
    })
  },
})
