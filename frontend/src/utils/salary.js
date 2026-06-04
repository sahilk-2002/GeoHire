const INDIAN_CITIES = [
  "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "ahmedabad",
  "chennai", "kolkata", "pune", "jaipur", "lucknow", "noida", "gurgaon",
  "indore", "bhopal", "surat", "chandigarh", "thane", "navi mumbai",
  "kochi", "coimbatore", "visakhapatnam", "vadodara", "nagpur", "india",
]

export function formatSalary(job) {
  if (!job.salary) return null
  const isIndia = INDIAN_CITIES.some(c => job.location?.toLowerCase().includes(c))
  if (isIndia && job.salary.includes("$")) {
    const nums = job.salary.match(/[\d,]+/g)
    if (nums) {
      const converted = nums.map(n => {
        const val = parseInt(n.replace(/,/g, "")) * 85
        return "₹" + (val >= 100000 ? (val / 100000).toFixed(1) + "L" : val.toLocaleString("en-IN"))
      })
      return converted.join(" – ")
    }
  }
  return job.salary
}
