import { CallDetailPage } from "@/components/calls/CallDetailPage";

export default function DashboardCallDetailPage({ params }: { params: { callId: string } }) {
    const callId = String(params?.callId ?? "").trim();
    return <CallDetailPage callId={callId} backHref="/dashboard/calls" backLabel="Back to calls" />;
}