import { MetadataRoute } from 'next'
import { INDUSTRIES } from '@/lib/industry-data'

export default function sitemap(): MetadataRoute.Sitemap {
    const baseUrl = 'https://calleem.tech'

    const staticRoutes = [
        {
            url: baseUrl,
            lastModified: new Date(),
            changeFrequency: 'monthly' as const,
            priority: 1,
        },
        {
            url: `${baseUrl}/login`,
            lastModified: new Date(),
            changeFrequency: 'monthly' as const,
            priority: 0.8,
        },
        {
            url: `${baseUrl}/contact`,
            lastModified: new Date(),
            changeFrequency: 'monthly' as const,
            priority: 0.9,
        },
    ]

    const industryRoutes = INDUSTRIES.map((industry) => ({
        url: `${baseUrl}/solutions/${industry.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.9,
    }))

    return [...staticRoutes, ...industryRoutes]
}
