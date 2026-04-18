import { redirect } from "next/navigation";

export default function ConversationDetailRedirectPage({ params }: { params: { id: string } }) {
    const id = String(params?.id ?? "").trim();
    if (!id || id === "undefined" || id === "null") {
        redirect("/dashboard/calls");
    }
    redirect(`/dashboard/calls/${id}`);
}
