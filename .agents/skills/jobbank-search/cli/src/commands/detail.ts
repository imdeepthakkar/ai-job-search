import { defineCommand } from "@bunli/core"
import { fetchWithUA, BASE_URL } from "../helpers"
import { parse } from "node-html-parser"

export const detail = defineCommand({
  name: "detail",
  description: "Full detail for a single job posting",
  handler: async ({ positional, output }) => {
    const id = positional[0]
    if (!id) throw new Error("Job ID is required")

    const url = `${BASE_URL}/job/${id}/`
    const response = await fetchWithUA(url)
    const html = await response.text()
    const root = parse(html)

    const ldJsonScript = root.querySelector('script[type="application/ld+json"]')
    if (!ldJsonScript) throw new Error("No JSON-LD found on job page")

    const ldJson = JSON.parse(ldJsonScript.text)
    const jobData = Array.isArray(ldJson) ? ldJson.find((x: any) => x["@type"] === "JobPosting") : ldJson

    output({
      id: jobData.identifier?.value || id,
      url: jobData.url || url,
      title: jobData.title,
      description: jobData.description,
      datePosted: jobData.datePosted,
      deadline: jobData.validThrough || null,
      employmentType: jobData.employmentType || [],
      company: {
        name: jobData.hiringOrganization?.name,
        logo: jobData.hiringOrganization?.logo
      },
      location: {
        streetAddress: jobData.jobLocation?.address?.streetAddress || "",
        city: jobData.jobLocation?.address?.addressLocality || "",
        postalCode: jobData.jobLocation?.address?.postalCode || "",
        country: jobData.jobLocation?.address?.addressCountry || "DK"
      }
    })
  },
})
