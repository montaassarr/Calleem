import ScrollingLogos from "@/components/scrolling-logos"
import { sampleLogos } from "@/lib/sample-logos"

export default function Home() {
  return (
    <div className="bg-background antialiased py-12">
      <div className="container mx-auto px-6">
        <div className="text-center mx-auto max-w-lg mb-8">
          <h1 className="font-mono font-medium text-muted-foreground uppercase text-xs tracking-widest">
            Trusted by Leading Companies
          </h1>
        </div>
        <ScrollingLogos logos={sampleLogos} />
      </div>
    </div>
  )
}
