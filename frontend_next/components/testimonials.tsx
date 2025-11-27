import { Marquee } from "@/components/magicui/marquee"
import { GlassCard } from "@/components/ui/glass-card"

const testimonials = [
  {
    name: "Sarah Jenkins",
    username: "@sarahj_realtor",
    body: "AIM² has completely transformed how I handle client calls. I never miss a lead now, even when I'm showing properties.",
    img: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
  },
  {
    name: "Dr. Michael Chen",
    username: "@mchen_dds",
    body: "The appointment scheduling is flawless. My patients love that they can book anytime, and my staff can focus on in-office care.",
    img: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
  },
  {
    name: "Elena Rodriguez",
    username: "@elena_salon",
    body: "It sounds so natural! Most of my clients don't even realize they're talking to an AI. Best investment for my salon.",
    img: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
  },
  {
    name: "Mark Thompson",
    username: "@mark_legal",
    body: "AIM² handles our intake calls professionally and efficiently. It saves us hours of phone time every week.",
    img: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
  },
  {
    name: "Jessica Lee",
    username: "@jess_fitness",
    body: "Setting up was a breeze. I had my AI receptionist running in minutes. It handles all my class bookings perfectly.",
    img: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face",
  },
  {
    name: "David Wilson",
    username: "@dwilson_consulting",
    body: "The integration with my calendar is seamless. No more double bookings or back-and-forth emails.",
    img: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
  },
]

const firstColumn = testimonials.slice(0, 3)
const secondColumn = testimonials.slice(3, 6)
const thirdColumn = testimonials.slice(6, 9)

const TestimonialCard = ({
  img,
  name,
  username,
  body,
}: {
  img: string
  name: string
  username: string
  body: string
}) => {
  return (
    <GlassCard className="w-full max-w-xs p-10">
      <div className="absolute -top-5 -left-5 -z-10 h-40 w-40 rounded-full bg-gradient-to-b from-[#0891b2]/10 to-transparent blur-md"></div>
      <div className="absolute -bottom-5 -right-5 -z-10 h-40 w-40 rounded-full bg-gradient-to-t from-[#0891b2]/10 to-transparent blur-md"></div>
      <div className="relative h-full rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:bg-white/10">
        <div className="mb-4 flex gap-1">
          {/* Assuming Star component is defined elsewhere or will be added */}
          {/* {[...Array(5)].map((_, i) => (
            <Star key={i} className="h-4 w-4 fill-[#0891b2] text-[#0891b2]" />
          ))} */}
        </div>
        <div className="text-white/90 leading-relaxed">{body}</div>

        <div className="mt-5 flex items-center gap-2">
          <img src={img || "/placeholder.svg"} alt={name} height="40" width="40" className="h-10 w-10 rounded-full" />
          <div className="flex flex-col">
            <div className="leading-5 font-medium tracking-tight text-white">{name}</div>
            <div className="leading-5 tracking-tight text-white/60">{username}</div>
          </div>
        </div>
      </div>
    </GlassCard>
  )
}

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="mb-24">
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-[540px]">
          <div className="flex justify-center">
            <GlassCard variant="button" className="z-[60]">
              <span className="text-white">Testimonials</span>
            </GlassCard>
          </div>
          <h2 className="from-foreground/60 via-foreground to-foreground/60 dark:from-muted-foreground/55 dark:via-foreground dark:to-muted-foreground/55 mt-5 bg-gradient-to-r bg-clip-text text-center text-4xl font-semibold tracking-tighter text-transparent md:text-[54px] md:leading-[60px] __className_bb4e88 relative z-10">
            What our users say
          </h2>

          <p className="mt-5 relative z-10 text-center text-lg text-zinc-500">
            From intuitive design to powerful features, our app has become an essential tool for users around the world.
          </p>
        </div>

        <div className="my-16 flex max-h-[738px] justify-center gap-6 overflow-hidden [mask-image:linear-gradient(to_bottom,transparent,black_25%,black_75%,transparent)]">
          <div>
            <Marquee pauseOnHover vertical className="[--duration:20s]">
              {firstColumn.map((testimonial) => (
                <TestimonialCard key={testimonial.username} {...testimonial} />
              ))}
            </Marquee>
          </div>

          <div className="hidden md:block">
            <Marquee reverse pauseOnHover vertical className="[--duration:25s]">
              {secondColumn.map((testimonial) => (
                <TestimonialCard key={testimonial.username} {...testimonial} />
              ))}
            </Marquee>
          </div>

          <div className="hidden lg:block">
            <Marquee pauseOnHover vertical className="[--duration:30s]">
              {thirdColumn.map((testimonial) => (
                <TestimonialCard key={testimonial.username} {...testimonial} />
              ))}
            </Marquee>
          </div>
        </div>

        <div className="-mt-8 flex justify-center">
          <GlassCard variant="button" className="inline-flex items-center gap-2 py-3">
            <svg className="h-4 w-4 text-[#0891b2]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"></path>
            </svg>
            <span>Share your experience</span>
          </GlassCard>
        </div>
      </div>
    </section>
  )
}
