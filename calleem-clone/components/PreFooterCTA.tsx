import React from 'react';
import { ArrowUpRight } from 'lucide-react';

const PreFooterCTA: React.FC = () => {
  return (
    <section className="w-full bg-calleem-bg py-24 px-6 md:px-10 flex justify-center overflow-visible">
      <div className="relative w-full max-w-[1000px] bg-[#0e2e22] rounded-[30px] shadow-[0_140px_120px_-80px_rgba(99,106,125,0.04)] flex flex-col md:flex-row items-center md:items-stretch overflow-visible">
        
        {/* Left Content */}
        <div className="flex-1 py-14 px-8 md:pl-12 md:pr-0 flex flex-col items-start gap-8 z-10">
          <div className="flex flex-col gap-4">
            <h2 className="font-display font-bold text-[36px] md:text-[48px] leading-[1.2] text-white">
              Ready to automate your appointments with AI?
            </h2>
            <p className="text-[16px] text-white/55 leading-[1.5] max-w-[400px]">
              Join the waitlist to be among the first to experience Calleem —and get early adopter pricing when we launch.
            </p>
          </div>
          
          <a 
            href="#contact" 
            className="group flex items-center gap-2 bg-calleem-accent hover:bg-[#368f51] text-white px-6 py-4 rounded-[23px] font-semibold text-[15px] transition-all duration-300 shadow-[0_1px_16px_2px_rgba(5,5,5,0.18)]"
          >
            Request Access
            <ArrowUpRight className="w-4 h-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </a>
        </div>

        {/* Right Image (Woman) */}
        {/* We need to position this so it looks like it's popping out. 
            On desktop, it sits on the right. 
            On mobile, it might sit below or above. 
            The reference image shows it overlapping the top and bottom.
        */}
        <div className="relative w-full md:w-[400px] h-[300px] md:h-auto flex-shrink-0 mt-8 md:mt-0">
           <div className="absolute bottom-0 md:-top-16 md:-bottom-3 right-0 md:right-10 w-full h-[120%] md:h-[115%] flex items-end justify-center md:justify-end pointer-events-none">
              {/* 
                Using a placeholder that approximates a cutout.
                In a real scenario, this would be a transparent PNG of the woman.
                I'll use a specific image and styling to mimic the cutout feel.
              */}
              <img 
                src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=988&auto=format&fit=crop" 
                alt="Happy woman holding phone"
                className="h-full w-auto object-cover object-top mask-gradient"
                style={{
                    maskImage: 'linear-gradient(to bottom, black 80%, transparent 100%)',
                    WebkitMaskImage: 'linear-gradient(to bottom, black 80%, transparent 100%)',
                    // This creates a makeshift cutout effect by simple masking, ideally we need a transparent png
                    borderRadius: '20px' 
                }}
              />
           </div>
        </div>

      </div>
    </section>
  );
};

export default PreFooterCTA;
