import React from 'react';
import Link from 'next/link';
import Navbar from '@/components/landing/Navbar';
import Footer from '@/components/landing/Footer';
import { LEGAL } from '@/lib/legal';

export interface LegalSection {
    /** Anchor id, used by the table of contents (e.g. "billing"). */
    id: string;
    title: string;
    content: React.ReactNode;
}

interface LegalPageProps {
    title: string;
    /** Short summary shown under the title. */
    intro: React.ReactNode;
    sections: LegalSection[];
    /** Path of the current page, used to hide it from the "related policies" list. */
    currentPath: '/terms' | '/privacy' | '/refund';
}

const LEGAL_LINKS = [
    { href: '/terms', label: 'Terms of Service' },
    { href: '/privacy', label: 'Privacy Policy' },
    { href: '/refund', label: 'Refund Policy' },
] as const;

/** Link to the contact form, the way to reach us about anything legal, billing or privacy. */
export function ContactLink() {
    return <a href={LEGAL.contactUrl}>our contact form</a>;
}

// Prose styles applied to the plain HTML each page passes in (p, ul, ol, li, a, strong, h3).
const proseClasses = [
    'flex flex-col gap-4 text-[15px] md:text-base leading-[1.75] text-white/75 break-words',
    '[&_strong]:font-semibold [&_strong]:text-white',
    '[&_a]:text-[#a8d48a] [&_a]:underline [&_a]:underline-offset-4 [&_a]:decoration-[#a8d48a]/40 [&_a:hover]:text-white [&_a:hover]:decoration-white/60',
    '[&_ul]:list-disc [&_ul]:pl-5 [&_ul]:flex [&_ul]:flex-col [&_ul]:gap-2 [&_ul]:marker:text-[#7fb069]',
    '[&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:flex [&_ol]:flex-col [&_ol]:gap-2 [&_ol]:marker:text-[#7fb069]',
    '[&_li]:pl-1',
    '[&_h3]:font-manrope [&_h3]:font-bold [&_h3]:text-white [&_h3]:text-[17px] [&_h3]:mt-2',
].join(' ');

export default function LegalPage({ title, intro, sections, currentPath }: LegalPageProps) {
    const related = LEGAL_LINKS.filter((link) => link.href !== currentPath);

    return (
        <div className="min-h-screen w-full bg-[#648768] overflow-x-hidden text-white">
            <Navbar />

            <main className="pt-32 md:pt-40 pb-20 px-4 md:px-6">
                <div className="w-full max-w-[760px] mx-auto flex flex-col gap-8 md:gap-10">

                    {/* Header */}
                    <header className="flex flex-col gap-5">
                        <div className="inline-flex w-fit items-center gap-2 px-3 py-1 rounded-full border border-[#1c1c1c] shadow-lg backdrop-blur-sm">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#1e5438] shadow-[0_0_8px_rgba(30,84,56,0.8)]"></div>
                            <span className="text-[12px] font-medium text-[#184a27] font-manrope">Legal</span>
                        </div>
                        <h1 className="font-manrope font-bold text-[36px] leading-[1.1] md:text-[52px] text-white">
                            {title}
                        </h1>
                        <div className="text-[16px] md:text-[18px] text-white/80 leading-[1.6]">
                            {intro}
                        </div>
                        <p className="text-sm text-white/70 font-manrope">
                            Last updated: <time>{LEGAL.lastUpdated}</time>
                        </p>
                    </header>

                    {/* Table of contents */}
                    <nav
                        aria-label="On this page"
                        className="bg-[#153629] rounded-[24px] border border-white/10 p-6 md:p-8"
                    >
                        <h2 className="font-manrope font-bold text-white text-sm uppercase tracking-wider mb-4">
                            On this page
                        </h2>
                        <ol className="columns-1 sm:columns-2 gap-x-8 text-[15px]">
                            {sections.map((section, index) => (
                                <li key={section.id} className="flex gap-1 min-w-0 mb-2.5 break-inside-avoid">
                                    <span className="text-[#7fb069] font-manrope font-semibold tabular-nums shrink-0 min-w-[1.75rem]">
                                        {index + 1}.
                                    </span>
                                    <a
                                        href={`#${section.id}`}
                                        className="text-white/75 hover:text-white transition-colors break-words"
                                    >
                                        {section.title}
                                    </a>
                                </li>
                            ))}
                        </ol>
                    </nav>

                    {/* Sections */}
                    <article className="bg-forest rounded-[30px] border border-white/5 shadow-2xl px-5 py-8 sm:p-8 md:p-12 flex flex-col">
                        {sections.map((section, index) => (
                            <section
                                key={section.id}
                                id={section.id}
                                aria-labelledby={`${section.id}-title`}
                                className="scroll-mt-32 py-8 first:pt-0 last:pb-0 border-t border-white/10 first:border-t-0"
                            >
                                <h2
                                    id={`${section.id}-title`}
                                    className="font-manrope font-bold text-white text-[22px] md:text-[26px] leading-[1.25] mb-5 flex gap-3"
                                >
                                    <span className="text-[#7fb069] tabular-nums">{index + 1}.</span>
                                    <span>{section.title}</span>
                                </h2>
                                <div className={proseClasses}>{section.content}</div>
                            </section>
                        ))}
                    </article>

                    {/* Related policies */}
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 text-[15px]">
                        <span className="text-white/70 font-manrope">Related policies:</span>
                        {related.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="text-white font-semibold underline underline-offset-4 decoration-white/40 hover:decoration-white transition-colors"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>

                </div>
            </main>

            <Footer />
        </div>
    );
}
