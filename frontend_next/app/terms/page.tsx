import type { Metadata } from 'next';
import Link from 'next/link';
import LegalPage, { ContactLink, type LegalSection } from '@/components/legal/LegalPage';
import { LEGAL, SELLER_NAME, WEBSITE_HOST } from '@/lib/legal';

export const metadata: Metadata = {
    title: 'Terms of Service',
    description: `The terms that apply when businesses use ${LEGAL.brand}, the AI voice receptionist that answers calls, books appointments and logs calls in a dashboard.`,
    alternates: { canonical: '/terms' },
};

const sections: LegalSection[] = [
    {
        id: 'who-we-are',
        title: 'Who we are and this agreement',
        content: (
            <>
                <p>
                    {LEGAL.brand} is an AI voice receptionist service operated by <strong>{SELLER_NAME}</strong>,
                    established in {LEGAL.country} (&ldquo;{LEGAL.brand}&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;).
                    These Terms of Service (&ldquo;Terms&rdquo;) govern your use of our website at{' '}
                    <a href={LEGAL.website}>{WEBSITE_HOST}</a>, the {LEGAL.brand} dashboard and the AI
                    receptionist service (together, the &ldquo;Service&rdquo;).
                </p>
                <p>
                    By creating an account, starting a subscription or otherwise using the Service, you agree to
                    these Terms, our <Link href="/privacy">Privacy Policy</Link> and our{' '}
                    <Link href="/refund">Refund Policy</Link>. If you do not agree, do not use the Service.
                </p>
                <p>
                    The Service is built for businesses and professionals, not for personal or household use. If
                    you accept these Terms on behalf of a company or other organization, you confirm that you have
                    the authority to bind it, and &ldquo;you&rdquo; means that organization.
                </p>
            </>
        ),
    },
    {
        id: 'the-service',
        title: 'The Service',
        content: (
            <>
                <p>
                    {LEGAL.brand} gives your business an AI voice assistant that answers your phone calls. Depending
                    on how you configure it, the assistant can answer common questions, take messages, collect caller
                    details and book appointments. Calls are recorded and transcribed, and call summaries,
                    transcripts, caller phone numbers and booked appointments are shown to you in your dashboard. You
                    can optionally have the Service send SMS confirmations to your callers.
                </p>
                <p>
                    The Service relies on third-party providers for telephony, speech recognition, speech
                    synthesis, language models, hosting and payments. The current list is in our{' '}
                    <Link href="/privacy#sub-processors">Privacy Policy</Link>.
                </p>
            </>
        ),
    },
    {
        id: 'accounts',
        title: 'Your account',
        content: (
            <ul>
                <li>You must be at least 18 years old and give us accurate, complete account information.</li>
                <li>
                    Keep your login details secure and do not share them outside your organization. You are
                    responsible for all activity under your account.
                </li>
                <li>
                    Tell us promptly through <ContactLink /> if you believe your account has been accessed without your
                    permission.
                </li>
                <li>
                    You are responsible for the people you give access to your account, and for making sure they
                    follow these Terms.
                </li>
            </ul>
        ),
    },
    {
        id: 'plans-and-billing',
        title: 'Plans, minutes and billing',
        content: (
            <>
                <ul>
                    <li>
                        <strong>Subscriptions.</strong> The Service is sold as monthly subscription plans. Each plan
                        includes a number of call minutes for each billing period. Subscriptions renew automatically
                        every month until you cancel.
                    </li>
                    <li>
                        <strong>Top-ups.</strong> You can buy optional prepaid minute top-ups to add minutes to your
                        balance.
                    </li>
                    <li>
                        <strong>How minutes are used.</strong> Minutes are deducted from your balance for each call
                        handled by your AI receptionist and are billed per second of call time.
                    </li>
                    <li>
                        <strong>Running out of minutes.</strong> When your balance reaches zero, your AI receptionist
                        pauses and stops answering calls until you add minutes or your plan renews. You are
                        responsible for keeping a sufficient balance and for having another way to handle calls while
                        the assistant is paused.
                    </li>
                    <li>
                        <strong>Prices.</strong> Prices are shown on our website or at checkout and may exclude
                        applicable taxes. We may change our prices with at least 30 days&rsquo; notice. A new price
                        applies from your next renewal after the notice period, and you can cancel before then if you
                        do not accept it.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'payments',
        title: 'Payments',
        content: (
            <>
                <p>
                    You buy the Service from {SELLER_NAME}. Card payments made through our checkout are processed by
                    Stripe, which also handles your subscription renewals and receipts. You authorise us, through
                    Stripe, to charge your card for your plan at the start of each billing period and for any
                    top-ups you buy, until you cancel.
                </p>
                <p>
                    Some customers may instead be invoiced directly by {SELLER_NAME}. In that case, payment is due by
                    the date and in the way stated on the invoice, and these Terms apply in the same way.
                </p>
                <p>
                    If a payment fails or an invoice is overdue, we may suspend the Service until the amount is paid.
                </p>
            </>
        ),
    },
    {
        id: 'cancellation-and-refunds',
        title: 'Cancellation and refunds',
        content: (
            <>
                <p>
                    You can cancel your subscription at any time. Cancellation stops future renewals, and your plan
                    stays active until the end of the billing period you have already paid for.
                </p>
                <p>
                    Refunds are handled under our <Link href="/refund">Refund Policy</Link>, which forms part of
                    these Terms.
                </p>
            </>
        ),
    },
    {
        id: 'your-responsibilities',
        title: 'Your responsibilities towards your callers',
        content: (
            <>
                <p>
                    You decide how the Service is used with your phone line, so you are responsible for using it
                    lawfully. In particular:
                </p>
                <ul>
                    <li>
                        <strong>Call recording and AI disclosure.</strong> Calls are recorded, transcribed and handled
                        by an AI. Where the law requires it, you must tell your callers that their call may be recorded
                        and is handled by an AI assistant, and obtain any consent required. Some US states (for
                        example California and Pennsylvania) require the consent of all parties to a call before it is
                        recorded, and other countries have similar rules. A short disclosure in your assistant&rsquo;s
                        greeting is usually the simplest way to do this.
                    </li>
                    <li>
                        <strong>Privacy notices.</strong> You are the controller of your callers&rsquo; personal data.
                        You must have a lawful basis for processing it and give your callers any privacy information
                        the law requires.
                    </li>
                    <li>
                        <strong>No emergency services.</strong> {LEGAL.brand} is not an emergency service and is not
                        connected to emergency numbers such as 911 or 112. You must not use it as a way for anyone to
                        reach emergency services or to handle urgent, life-threatening situations. Where callers might
                        have an emergency, configure your assistant to tell them to hang up and call the local
                        emergency number.
                    </li>
                    <li>
                        <strong>Specially regulated data.</strong> Unless we have signed a separate written agreement
                        covering it (such as a HIPAA Business Associate Agreement), you must not use the Service to
                        collect or store data that is subject to special legal requirements, such as protected health
                        information, payment card numbers or government ID numbers.
                    </li>
                    <li>
                        <strong>Your information.</strong> You are responsible for the business information you give
                        the assistant (opening hours, services, prices, policies and similar) being accurate and up to
                        date, and for reviewing your calls and appointments in the dashboard.
                    </li>
                    <li>
                        <strong>SMS.</strong> If you enable SMS confirmations, messages must relate to the
                        caller&rsquo;s call or appointment, and you are responsible for meeting any consent rules for
                        those messages.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'acceptable-use',
        title: 'Acceptable use',
        content: (
            <>
                <p>You must not use the Service, or allow anyone else to use it, to:</p>
                <ul>
                    <li>break any law or regulation, or help anyone else do so;</li>
                    <li>
                        make or send spam, robocalls, telemarketing or other unsolicited calls or messages, or break
                        telemarketing and messaging laws such as the US Telephone Consumer Protection Act (TCPA);
                    </li>
                    <li>
                        deceive, defraud, harass or threaten anyone, or impersonate another person or business;
                    </li>
                    <li>
                        configure the assistant to deny being an AI when a caller sincerely asks, or to give advice it
                        is not allowed to give (see the next section);
                    </li>
                    <li>collect personal data unlawfully or process it without a valid legal basis;</li>
                    <li>
                        interfere with, overload or try to gain unauthorized access to the Service, other accounts or
                        our providers&rsquo; systems, or reverse engineer the Service except where the law allows it;
                    </li>
                    <li>resell or sublicense the Service without our written permission.</li>
                </ul>
                <p>
                    We may investigate suspected misuse and suspend or terminate accounts that break these rules, as
                    described below.
                </p>
            </>
        ),
    },
    {
        id: 'ai-limitations',
        title: 'AI limitations and no professional advice',
        content: (
            <>
                <p>
                    The assistant uses artificial intelligence and can make mistakes. It may mishear or misunderstand
                    a caller, give incomplete or wrong information, fail to book an appointment or record details
                    incorrectly. Transcripts and summaries are generated automatically and may contain errors. You
                    should check important calls and appointments in your dashboard.
                </p>
                <p>
                    <strong>
                        The assistant does not give legal, medical, financial or other professional advice, and you
                        must not configure it to do so.
                    </strong>{' '}
                    If you are a law firm, clinic or other professional practice, the assistant should only answer
                    general questions about your business, take messages and book appointments or consultations.
                    Nothing the assistant says creates a professional relationship (such as an attorney-client or
                    doctor-patient relationship) between your business or {LEGAL.brand} and a caller.
                </p>
            </>
        ),
    },
    {
        id: 'availability',
        title: 'Availability, changes and suspension',
        content: (
            <>
                <p>
                    We work to keep the Service available around the clock, but we do not guarantee that it will be
                    uninterrupted or error-free. It depends on telephone networks and third-party providers outside
                    our control, and we may need to carry out maintenance. We may improve, change or remove features
                    over time; if a change significantly reduces the Service you pay for, we will tell you in advance.
                </p>
                <p>We may suspend or limit the Service, with notice where reasonably possible, if:</p>
                <ul>
                    <li>a payment fails or an invoice is overdue;</li>
                    <li>
                        your minute balance reaches zero (your AI receptionist pauses until you add minutes or your
                        plan renews);
                    </li>
                    <li>you break these Terms, including the acceptable use rules;</li>
                    <li>
                        it is needed to protect the Service, our providers, your callers or other customers, or to
                        comply with the law or a request from a telecom provider or authority.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'your-data',
        title: 'Your data',
        content: (
            <>
                <p>
                    You keep all rights to the content and data you and your callers provide through the Service,
                    including business information, call recordings, transcripts, summaries and appointment
                    details (&ldquo;Customer Data&rdquo;). You give us permission to host, process and transmit
                    Customer Data only as needed to provide, secure and support the Service for you.
                </p>
                <p>
                    For your callers&rsquo; personal data, you are the controller and we act as your processor. Our{' '}
                    <Link href="/privacy">Privacy Policy</Link> explains how we handle personal data. If you need a
                    data processing agreement, contact us through <ContactLink />.
                </p>
            </>
        ),
    },
    {
        id: 'intellectual-property',
        title: 'Intellectual property',
        content: (
            <>
                <p>
                    {LEGAL.brand} and its licensors own the Service, including the software, the dashboard, the
                    website, the {LEGAL.brand} name and logo, and all related intellectual property. While your
                    subscription is active, we give you a limited, non-exclusive, non-transferable right to use the
                    Service for your business under these Terms. We reserve all rights not expressly granted.
                </p>
                <p>
                    If you send us feedback or suggestions, we may use them to improve the Service without any
                    obligation to you.
                </p>
            </>
        ),
    },
    {
        id: 'liability',
        title: 'Disclaimers and limitation of liability',
        content: (
            <>
                <p>
                    Except as expressly stated in these Terms, the Service is provided &ldquo;as is&rdquo; and
                    &ldquo;as available&rdquo;, and we make no other warranties, including implied warranties of
                    merchantability, fitness for a particular purpose or non-infringement, to the extent the law
                    allows.
                </p>
                <p>To the maximum extent permitted by law:</p>
                <ul>
                    <li>
                        we are not liable for indirect, incidental, special or consequential losses, or for loss of
                        profits, revenue, business, bookings, goodwill or data, including losses caused by missed,
                        dropped or mishandled calls or by mistakes made by the AI assistant;
                    </li>
                    <li>
                        our total liability for all claims relating to the Service is limited to the amount you paid
                        for the Service in the 12 months before the event giving rise to the claim.
                    </li>
                </ul>
                <p>
                    Nothing in these Terms limits liability that cannot be limited by law, such as liability for
                    fraud or for death or personal injury caused by negligence.
                </p>
            </>
        ),
    },
    {
        id: 'indemnity',
        title: 'Indemnity',
        content: (
            <p>
                You agree to defend and indemnify {SELLER_NAME} against claims, fines and reasonable costs arising
                from your use of the Service in breach of these Terms or the law, including failing to give required
                notices or obtain required consents from your callers, or breaking telemarketing or messaging rules.
            </p>
        ),
    },
    {
        id: 'termination',
        title: 'Term and termination',
        content: (
            <>
                <p>
                    These Terms apply for as long as you use the Service. You can cancel your subscription at any
                    time, and you can ask us to close your account by messaging us through <ContactLink />.
                </p>
                <p>
                    We may terminate your account if you seriously or repeatedly break these Terms, if you do not pay,
                    or if we stop offering the Service, in which case we will give you reasonable notice and refund
                    any prepaid amount for the period after termination.
                </p>
                <p>
                    When your account closes, your access to the dashboard ends and your data is deleted as described
                    in our <Link href="/privacy#retention">Privacy Policy</Link>. If you need a copy of your data,
                    contact us before closing your account. Sections that by their nature should survive termination
                    (such as payment obligations, intellectual property, limitation of liability and indemnity)
                    continue to apply.
                </p>
            </>
        ),
    },
    {
        id: 'changes',
        title: 'Changes to these Terms',
        content: (
            <p>
                We may update these Terms from time to time. We will post the new version on this page and update
                the &ldquo;Last updated&rdquo; date. If a change is material, we will notify you by email or in your
                dashboard at least 30 days before it takes effect. If you keep using the Service after the change
                takes effect, you accept the updated Terms; if you do not agree, you can cancel before then.
            </p>
        ),
    },
    {
        id: 'governing-law',
        title: 'Governing law and disputes',
        content: (
            <>
                <p>
                    These Terms are governed by the laws of {LEGAL.governingLaw}, and the courts of{' '}
                    {LEGAL.governingLaw} have jurisdiction over any dispute arising from them, unless mandatory law
                    where you are established says otherwise.
                </p>
                <p>
                    Before starting any formal proceedings, please contact us through <ContactLink /> so we can try to
                    resolve the issue informally.
                </p>
            </>
        ),
    },
    {
        id: 'general',
        title: 'General',
        content: (
            <ul>
                <li>
                    These Terms, together with the Privacy Policy, the Refund Policy and any order form or invoice
                    from us, are the entire agreement between you and us about the Service.
                </li>
                <li>
                    If any part of these Terms is found unenforceable, the rest remains in effect.
                </li>
                <li>If we do not enforce a right straight away, we do not give it up.</li>
                <li>
                    You may not transfer your rights under these Terms without our consent. We may transfer them as
                    part of a merger, acquisition or sale of our business.
                </li>
                <li>
                    We are not responsible for delays or failures caused by events outside our reasonable control,
                    such as outages of telephone networks or third-party providers.
                </li>
            </ul>
        ),
    },
    {
        id: 'contact',
        title: 'Contact',
        content: (
            <p>
                Questions about these Terms or a payment? Send us a message through <ContactLink />.
            </p>
        ),
    },
];

export default function TermsPage() {
    return (
        <LegalPage
            title="Terms of Service"
            currentPath="/terms"
            intro={
                <p>
                    These terms explain the rules for using {LEGAL.brand}: what you get, how billing works, and what
                    you are responsible for when an AI answers your business calls.
                </p>
            }
            sections={sections}
        />
    );
}
