import React from 'react';
import { ArrowArrowRight } from 'lucide-react'; // Using icon as approximation for the SVG, or will use SVG directly

const PreFooterCTA: React.FC = () => {
    return (
        <section className="w-full bg-[#648768] py-24 px-6 md:px-10 flex justify-center">
            <div
                className="relative w-full max-w-[1000px] bg-[#0e2e22] rounded-[30px] shadow-[0_140px_120px_-80px_rgba(99,106,125,0.04)] overflow-hidden flex flex-col md:flex-row items-center md:items-stretch"
            >
                {/* Text Content */}
                <div className="flex-1 p-8 md:p-14 flex flex-col items-start gap-8 z-10 w-full md:w-auto">
                    <div className="flex flex-col gap-4">
                        <h2 className="font-manrope font-bold text-[36px] md:text-[48px] leading-[1.2] text-white text-left">
                            Ready to automate your appointments with AI?
                        </h2>
                        <p className="text-[16px] text-white/55 leading-[1.5] max-w-[400px] text-left">
                            Join the waitlist to be among the first to experience Calleem —and get early adopter pricing when we launch.
                        </p>
                    </div>

                    <a
                        href="#contact"
                        className="group flex items-center gap-2 bg-[#2c7a44] hover:bg-[#368f51] text-white px-6 py-4 rounded-[20px] font-semibold text-[15px] transition-all duration-300 shadow-[0_1px_16px_2px_rgba(5,5,5,0.18)]"
                    >
                        <span>Request Access</span>
                        <div className="-rotate-45 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 256 256" fill="currentColor">
                                <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                            </svg>
                        </div>
                    </a>
                </div>

                {/* Image Section */}
                <div className="relative w-full md:w-[420px] h-[300px] md:h-auto overflow-hidden shrink-0 mt-8 md:mt-0">
                    <div className="absolute inset-0 w-full h-full">
                        <img
                            src="https://framerusercontent.com/images/AsfW6nRtd8870rS0nxiZalBmjno.webp?width=1368&height=1920"
                            alt="Happy woman in a green sweater holding a phone"
                            className="w-full h-full object-cover object-center"
                            style={{
                                maskImage: 'linear-gradient(0deg, rgba(0, 0, 0, 0) 0%, rgb(0, 0, 0) 100%)',
                                WebkitMaskImage: 'linear-gradient(0deg, rgba(0, 0, 0, 0) 0%, rgb(0, 0, 0) 100%)'
                            }}
                        />
                    </div>
                </div>

            </div>
        </section>
    );
};

export default PreFooterCTA;
