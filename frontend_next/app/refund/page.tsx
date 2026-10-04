import type { Metadata } from 'next';
import Link from 'next/link';
import LegalPage, { ContactLink, type LegalSection } from '@/components/legal/LegalPage';
import { LEGAL, SELLER_NAME } from '@/lib/legal';

export const metadata: Metadata = {
    title: 'Refund Policy',
    description: `When and how you can get a refund for ${LEGAL.brand} subscriptions and prepaid minute top-ups, and how cancellation works.`,
    alternates: { canonical: '/refund' },
};

const sections: LegalSection[] = [
    {
        id: 'summary',
        title: 'Summary',
        content: (
            <ul>
                <li>
                    <strong>New subscriptions:</strong> full refund within 14 days of your first payment if you have
                    used less than 30 minutes of calls.
                </li>
                <li>
                    <strong>Prepaid top-ups:</strong> unused top-up minutes are refundable within 14 days of
                    purchase.
                </li>
                <li>
                    <strong>Used minutes</strong> are not refundable.
                </li>
                <li>
                    <strong>Cancel any time:</strong> cancelling stops future renewals, and your plan stays active
                    until the end of the period you have paid for.
                </li>
            </ul>
        ),
    },
    {
        id: 'who',
        title: 'Who handles your order',
        content: (
            <p>
                You buy from {SELLER_NAME}. Card payments made through our checkout are processed by Stripe, and
                customers invoiced directly pay us by bank transfer. In both cases we handle refund requests
                ourselves, under the rules below.
            </p>
        ),
    },
    {
        id: 'new-subscriptions',
        title: 'New subscriptions',
        content: (
            <>
                <p>
                    If you subscribe to a {LEGAL.brand} plan for the first time, you can ask for a{' '}
                    <strong>full refund within 14 days of your first payment</strong>, as long as the Service has not
                    been substantially used. In practice, this means your AI receptionist has handled less than 30
                    minutes of calls in total.
                </p>
                <p>
                    If you have used 30 minutes or more, the first payment is not refundable, but you can cancel at any
                    time so that you are not charged again.
                </p>
            </>
        ),
    },
    {
        id: 'renewals',
        title: 'Renewals',
        content: (
            <p>
                Subscriptions renew automatically each month. Renewal payments are not refundable once the new
                billing period has started, except where this policy says otherwise (see{' '}
                <a href="#billing-errors">Billing errors and service problems</a>) or where the law requires it. To
                avoid a renewal charge, cancel before your renewal date.
            </p>
        ),
    },
    {
        id: 'top-ups',
        title: 'Prepaid minute top-ups',
        content: (
            <>
                <p>
                    Unused minutes from a prepaid top-up are refundable <strong>within 14 days of purchase</strong>. If
                    you have used part of a top-up, we refund the minutes still unused, calculated at the price you
                    paid per minute for that top-up.
                </p>
                <p>After 14 days, top-up purchases are not refundable.</p>
            </>
        ),
    },
    {
        id: 'used-minutes',
        title: 'Minutes already used',
        content: (
            <p>
                Minutes are deducted per call and billed per second. Once minutes have been used to handle calls,
                they are not refundable, because the calls have already been processed by us and our telephony and
                AI providers.
            </p>
        ),
    },
    {
        id: 'cancellation',
        title: 'Cancelling your subscription',
        content: (
            <>
                <p>
                    You can cancel at any time from the Billing page of your dashboard (Manage subscription), or by
                    messaging us through <ContactLink />.
                </p>
                <ul>
                    <li>Cancellation stops all future renewals.</li>
                    <li>
                        Your plan stays active, with its remaining minutes, until the end of the billing period you have
                        already paid for.
                    </li>
                    <li>
                        Cancelling does not by itself trigger a refund for the current period, unless you are within the
                        14-day refund window described above.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'billing-errors',
        title: 'Billing errors and service problems',
        content: (
            <p>
                If you were charged twice, charged the wrong amount, or charged after you cancelled, we will refund the
                incorrect charge in full. If the Service was unavailable for a significant period because of a problem
                on our side, contact us and we will offer a fair refund or credit. These rules do not affect any
                rights you have under the law of your country.
            </p>
        ),
    },
    {
        id: 'how-to-request',
        title: 'How to request a refund',
        content: (
            <>
                <ol>
                    <li>
                        <strong>Card payments through our checkout:</strong> send us a message through{' '}
                        <ContactLink />; approved refunds go back to the card you paid with.
                    </li>
                    <li>
                        <strong>Customers invoiced directly by {LEGAL.brand}:</strong> send us a message through{' '}
                        <ContactLink />.
                    </li>
                </ol>
                <p>
                    Please include the email address on your account, your order or invoice number, and a short reason
                    for the request.
                </p>
            </>
        ),
    },
    {
        id: 'timeline',
        title: 'Timeline',
        content: (
            <>
                <p>
                    We aim to reply to refund requests within 3 business days. Approved refunds are sent to the
                    original payment method, and usually appear within 5 to 10 business days, depending on your bank
                    or card provider.
                </p>
                <p>
                    When a refund is issued, the related minutes are removed from your balance, and for a subscription
                    refund the plan ends.
                </p>
            </>
        ),
    },
    {
        id: 'contact',
        title: 'Questions',
        content: (
            <p>
                If you have a question about a charge, please contact us through <ContactLink />{' '}
                before opening a dispute with your bank, so we can resolve it quickly. See also our{' '}
                <Link href="/terms">Terms of Service</Link> and <Link href="/privacy">Privacy Policy</Link>.
            </p>
        ),
    },
];

export default function RefundPage() {
    return (
        <LegalPage
            title="Refund Policy"
            currentPath="/refund"
            intro={
                <p>
                    A simple, fair policy for {LEGAL.brand} subscriptions and prepaid minute top-ups.
                </p>
            }
            sections={sections}
        />
    );
}
