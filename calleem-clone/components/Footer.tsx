import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-[#648768]/80 backdrop-blur-md pt-20 pb-10 px-6 md:px-10 border-t border-white/5">
      <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row justify-between gap-12">
        
        {/* Brand Column */}
        <div className="flex flex-col gap-8 max-w-[380px]">
          <a href="/" className="flex items-center gap-2">
             <div className="w-10 h-6 relative text-white">
                <svg viewBox="0 0 41 24" fill="none" className="w-full h-full">
                    <path d="M21.821 0.929C22.354 0.38 23.092 0.068 23.865 0.065L33.762 0.065C40.198 0.065 43.42 8.011 38.869 12.659L28.958 22.783C28.503 23.247 27.725 22.918 27.725 22.26L27.725 13.345L28.87 12.174C29.78 11.245 29.136 9.656 27.848 9.656L13.276 9.656L21.821 0.929Z" fill="currentColor"/>
                    <path d="M19.179 22.071C18.646 22.62 17.908 22.932 17.135 22.935L7.238 22.935C0.802 22.935 -2.42 14.988 2.131 10.341L12.042 0.217C12.497 -0.247 13.276 0.082 13.276 0.739L13.276 9.655L12.13 10.825C11.22 11.755 11.864 13.344 13.152 13.344L27.724 13.344L19.178 22.071Z" fill="currentColor"/>
                </svg>
             </div>
             <span className="font-display font-semibold text-xl tracking-tight text-white">Calleem</span>
          </a>
          <p className="text-[14px] leading-[1.5] text-white/90">
            Your 24/7 AI-powered receptionist.<br/>
            Never miss a call, automate booking, and manage appointments—effortlessly.
          </p>
          <div className="pt-8 mt-auto hidden md:block">
             <div className="flex items-center gap-2 text-[13px] text-white/90 font-medium">
                <div className="w-3 h-3 rounded-full bg-calleem-dark border border-white/20"></div>
                Designed by <span className="text-[#8cff2e]">Calleem</span> 2025
             </div>
          </div>
        </div>

        {/* Links Columns */}
        <div className="flex gap-16 md:gap-24">
          <div className="flex flex-col gap-6">
            <h6 className="font-display font-bold text-[16px] text-white">Quick Menu</h6>
            <div className="flex flex-col gap-4">
              {['How it works', 'Features', 'Testimonials', 'Pricing'].map(link => (
                <a key={link} href="#" className="text-[14px] text-white/60 hover:text-white transition-colors">
                  {link}
                </a>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <h6 className="font-display font-bold text-[16px] text-white">Information</h6>
            <div className="flex flex-col gap-4">
              <a href="#contact" className="text-[14px] text-white/60 hover:text-white transition-colors">
                Request Access
              </a>
            </div>
          </div>
        </div>

        {/* Mobile Copyright */}
        <div className="md:hidden pt-8 border-t border-white/10">
             <div className="flex items-center justify-center gap-2 text-[13px] text-white/90 font-medium">
                <div className="w-3 h-3 rounded-full bg-calleem-dark border border-white/20"></div>
                Designed by <span className="text-[#8cff2e]">Calleem</span> 2025
             </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
