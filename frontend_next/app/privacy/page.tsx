import type { Metadata } from 'next';
import Link from 'next/link';
import LegalPage, { ContactLink, type LegalSection } from '@/components/legal/LegalPage';
import { LEGAL, SELLER_NAME, WEBSITE_HOST } from '@/lib/legal';

export const metadata: Metadata = {
    title: 'Privacy Policy',
    description: `How ${LEGAL.brand} collects, uses, shares and protects personal data, including call recordings and transcripts handled for the businesses we serve.`,
    alternates: { canonical: '/privacy' },
};

const SUB_PROCESSORS: { name: string; purpose: string }[] = [
    { name: 'Vapi', purpose: 'Voice AI platform that runs the AI receptionist and processes call audio, recordings and transcripts.' },
    { name: 'Twilio', purpose: 'Telephony: phone numbers, call routing and SMS confirmations.' },
    { name: 'OpenAI (via Vapi)', purpose: 'Language model that understands callers and generates the assistant’s replies.' },
    { name: 'Deepgram (via Vapi)', purpose: 'Speech-to-text transcription of calls.' },
    { name: 'ElevenLabs (via Vapi)', purpose: 'Text-to-speech for the assistant’s voice.' },
    { name: 'Amazon Web Services', purpose: 'Application hosting, and Amazon Bedrock for the chatbot on our website.' },
    { name: 'MongoDB Atlas', purpose: 'Database that stores account data, business settings, call records and appointments.' },
    { name: 'Vercel', purpose: 'Hosting of our website and dashboard.' },
    { name: 'Stripe', purpose: 'Checkout, card payments, subscriptions and receipts.' },
];

const sections: LegalSection[] = [
    {
        id: 'introduction',
        title: 'Introduction',
        content: (
            <>
                <p>
                    This Privacy Policy explains how <strong>{SELLER_NAME}</strong>, established in {LEGAL.country}{' '}
                    (&ldquo;{LEGAL.brand}&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;), handles personal data when you
                    visit <a href={LEGAL.website}>{WEBSITE_HOST}</a>, use the {LEGAL.brand} dashboard, or call a
                    business that uses {LEGAL.brand} as its AI receptionist.
                </p>
                <p>
                    We do not sell personal data, and we only use it for the purposes described in this policy.
                </p>
            </>
        ),
    },
    {
        id: 'roles',
        title: 'Our role: controller and processor',
        content: (
            <ul>
                <li>
                    <strong>Account and website data.</strong> For data about our customers and website visitors
                    (for example your account details and messages you send us), {LEGAL.brand} is the controller.
                </li>
                <li>
                    <strong>Caller data.</strong> When someone calls a business that uses {LEGAL.brand}, that
                    business is the controller of the caller&rsquo;s personal data and {LEGAL.brand} is its
                    processor. We process caller data only on the business&rsquo;s instructions and to provide the
                    Service to it. If you called a business and have a question about your data, please contact that
                    business directly; if you contact us, we will pass your request on to it.
                </li>
            </ul>
        ),
    },
    {
        id: 'data-we-collect',
        title: 'Data we collect',
        content: (
            <>
                <h3>Account data</h3>
                <p>
                    Your name, email address, phone number, business name, login credentials and account settings,
                    and records of your plan, minute balance and usage.
                </p>
                <h3>Business configuration</h3>
                <p>
                    The information you give your assistant, such as opening hours, services, prices, staff names,
                    frequently asked questions, greeting messages, booking settings and the phone numbers connected to
                    the Service.
                </p>
                <h3>Caller data (processed on behalf of the business)</h3>
                <p>
                    Caller phone numbers, call recordings, transcripts, AI-generated call summaries, details the
                    caller gives during the call (such as their name and reason for calling), booked appointments, SMS
                    confirmations sent to callers, and call metadata such as date, time and duration.
                </p>
                <h3>Website, contact form and chatbot data</h3>
                <p>
                    Information you submit through our contact form (such as your name, email, business name, phone
                    number and message), messages you send to the chatbot on our website, and basic technical data
                    such as IP address, browser type, device information and server logs.
                </p>
                <h3>Payment data</h3>
                <p>
                    Payments made through our checkout are processed by Stripe. Stripe collects your card details
                    directly. <strong>We never see or store your full card number.</strong> We receive limited
                    information from Stripe, such as your name, email, billing country, the plan or top-up
                    purchased, amounts and payment status.
                </p>
                <h3>Support communications</h3>
                <p>The content of emails and other messages you send us, and our replies.</p>
            </>
        ),
    },
    {
        id: 'how-we-use-data',
        title: 'How we use data',
        content: (
            <>
                <p>We use personal data to:</p>
                <ul>
                    <li>
                        provide the Service: answer calls, book appointments, send SMS confirmations, and show calls,
                        transcripts, summaries and appointments in your dashboard (performance of our contract with
                        you);
                    </li>
                    <li>
                        manage your account, minutes, subscriptions and billing (contract, and our legal obligations
                        for tax and accounting);
                    </li>
                    <li>answer contact form, chatbot and support requests (our legitimate interest in responding);</li>
                    <li>
                        keep the Service secure, prevent fraud and abuse, and fix problems (our legitimate interests);
                    </li>
                    <li>
                        improve the Service using usage statistics and feedback (our legitimate interests);
                    </li>
                    <li>
                        send you service messages, and product news where you have agreed or where the law allows it.
                        You can unsubscribe from marketing emails at any time;
                    </li>
                    <li>comply with legal obligations and respond to lawful requests from authorities.</li>
                </ul>
                <p>
                    Caller data is used only to provide and support the Service for the business the call belongs to.
                </p>
            </>
        ),
    },
    {
        id: 'sub-processors',
        title: 'Sub-processors and sharing',
        content: (
            <>
                <p>
                    We use the following service providers (sub-processors) to run {LEGAL.brand}. They process
                    personal data only to provide their services to us and under contracts that protect the data.
                </p>
                <ul>
                    {SUB_PROCESSORS.map((sp) => (
                        <li key={sp.name}>
                            <strong>{sp.name}</strong> &mdash; {sp.purpose}
                        </li>
                    ))}
                </ul>
                <p>We may also share personal data:</p>
                <ul>
                    <li>with the business you called, which can see your call details in its dashboard;</li>
                    <li>
                        when required by law, or to protect the rights, safety and security of our users, callers, us
                        or others;
                    </li>
                    <li>
                        with a buyer or successor if we are involved in a merger, acquisition or sale of assets, who
                        must keep protecting the data in line with this policy.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'international-transfers',
        title: 'International transfers',
        content: (
            <p>
                We are based in {LEGAL.country}, and several of our sub-processors are located in, or process data
                in, the United States and other countries. These countries may not have the same data protection laws
                as yours. When we transfer personal data from the European Economic Area, the United Kingdom or
                Switzerland to other countries, we rely on appropriate safeguards such as the European
                Commission&rsquo;s Standard Contractual Clauses, the UK addendum to them, or the EU-US Data Privacy
                Framework where a provider is certified under it.
            </p>
        ),
    },
    {
        id: 'retention',
        title: 'How long we keep data',
        content: (
            <ul>
                <li>
                    <strong>Call recordings, transcripts, summaries and appointments</strong> are kept while the
                    business&rsquo;s account is active and deleted within 90 days after the account is closed, unless
                    the business deletes them earlier.
                </li>
                <li>
                    <strong>Account data</strong> is kept while your account is active and deleted within 90 days
                    after it is closed, except for records we must keep longer by law, such as invoices and tax
                    records.
                </li>
                <li>
                    <strong>Contact form, chatbot and support messages</strong> are kept for as long as needed to
                    answer and follow up on your request, and then deleted or anonymized.
                </li>
                <li>
                    <strong>Technical logs</strong> are kept for a limited period for security and troubleshooting.
                </li>
            </ul>
        ),
    },
    {
        id: 'security',
        title: 'Security',
        content: (
            <p>
                We protect personal data with technical and organizational measures, including encryption in
                transit (HTTPS/TLS), authentication for the dashboard, access controls that limit access to people
                and systems that need it, and choosing providers with strong security practices. No system is
                completely secure, but if a personal data breach affects you, we will notify you and the relevant
                authorities as required by law.
            </p>
        ),
    },
    {
        id: 'your-rights',
        title: 'Your privacy rights',
        content: (
            <>
                <h3>EU, EEA and UK (GDPR)</h3>
                <p>
                    You have the right to access your personal data, correct it, have it deleted, restrict or object
                    to its processing, receive it in a portable format, and withdraw consent at any time where we rely
                    on consent. You also have the right to complain to your local data protection authority.
                </p>
                <h3>California (CCPA/CPRA)</h3>
                <p>
                    California residents have the right to know what personal information we collect and how we use
                    and disclose it, to request deletion and correction, and not to be discriminated against for
                    exercising these rights. We do not sell personal information or share it for cross-context
                    behavioral advertising. You can use an authorized agent to make a request for you.
                </p>
                <h3>How to exercise your rights</h3>
                <p>
                    Send us a message through <ContactLink />. We may need to verify your identity before
                    acting on a request, and we will reply within the time the law requires (usually within one month
                    under the GDPR and 45 days under the CCPA). If you are a caller, your request is usually best sent
                    to the business you called, as it controls your data; if you contact us, we will forward it.
                </p>
            </>
        ),
    },
    {
        id: 'cookies',
        title: 'Cookies',
        content: (
            <p>
                We use essential cookies and similar browser storage that are needed for the website and dashboard
                to work, for example to keep you signed in and to protect your account. We do not use advertising or
                cross-site tracking cookies. If we use basic analytics to understand how our website is used, it is
                limited to aggregated usage statistics, and we will update this policy and ask for consent where the
                law requires it. You can control cookies in your browser settings, but blocking essential cookies may
                stop parts of the Service from working.
            </p>
        ),
    },
    {
        id: 'children',
        title: 'Children',
        content: (
            <p>
                {LEGAL.brand} is a business service and is not directed at children. Accounts are only for people
                aged 18 or older, and we do not knowingly collect personal data from children for our own purposes.
                If you believe a child has given us personal data, contact us and we will delete it.
            </p>
        ),
    },
    {
        id: 'changes',
        title: 'Changes to this policy',
        content: (
            <p>
                We may update this Privacy Policy from time to time. We will post the new version on this page and
                update the &ldquo;Last updated&rdquo; date. If the changes are significant, we will also notify
                customers by email or in the dashboard.
            </p>
        ),
    },
    {
        id: 'contact',
        title: 'Contact',
        content: (
            <p>
                For privacy questions or requests, write to us through <ContactLink />. You can also read
                our <Link href="/terms">Terms of Service</Link> and <Link href="/refund">Refund Policy</Link>.
            </p>
        ),
    },
];

export default function PrivacyPage() {
    return (
        <LegalPage
            title="Privacy Policy"
            currentPath="/privacy"
            intro={
                <p>
                    How we collect, use and protect personal data, for our customers, their callers and visitors to
                    our website.
                </p>
            }
            sections={sections}
        />
    );
}
