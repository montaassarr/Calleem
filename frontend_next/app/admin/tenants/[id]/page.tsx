"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    ArrowLeft,
    Users,
    Calendar,
    MessageSquare,
    Phone,
    Mail,
    Building2,
    Activity,
    Loader2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function TenantDetailsPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const router = useRouter();
    const queryClient = useQueryClient();

    // Fetch tenant details
    const { data: tenants, isLoading: loadingTenant } = useQuery({
        queryKey: ["tenants"],
        queryFn: () => adminApi.getTenants(),
    });

    const tenant = tenants?.find((t: any) => t.id === id);

    // Fetch users for this tenant
    const { data: allUsers, isLoading: loadingUsers } = useQuery({
        queryKey: ["users"],
        queryFn: () => adminApi.getUsers(),
    });

    const tenantUsers = allUsers?.filter((u: any) => u.tenant_id === id) || [];

    // Fetch appointments for this tenant
    const { data: appointments } = useQuery({
        queryKey: ["appointments", id],
        queryFn: () => adminApi.getAppointments(),
    });

    const tenantAppointments = appointments?.filter((a: any) => a.tenant_id === id) || [];

    // Fetch conversations for this tenant
    const { data: conversations } = useQuery({
        queryKey: ["conversations", id],
        queryFn: () => adminApi.getConversations(),
    });

    const tenantConversations = conversations?.filter((c: any) => c.tenant_id === id) || [];

    // Update status mutation
    const updateStatusMutation = useMutation({
        mutationFn: ({ status }: { status: string }) =>
            adminApi.updateTenant(id, { status }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tenants"] });
            toast.success("Tenant status updated");
        },
        onError: () => {
            toast.error("Failed to update status");
        },
    });

    if (loadingTenant) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="space-y-6">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">Tenant Not Found</h1>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">{tenant.name}</h1>
                        <p className="text-muted-foreground">Tenant Details & Management</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    {tenant.status === "active" ? (
                        <Button
                            variant="destructive"
                            onClick={() => updateStatusMutation.mutate({ status: "suspended" })}
                            disabled={updateStatusMutation.isPending}
                        >
                            Suspend Tenant
                        </Button>
                    ) : (
                        <Button
                            variant="default"
                            onClick={() => updateStatusMutation.mutate({ status: "active" })}
                            disabled={updateStatusMutation.isPending}
                        >
                            Activate Tenant
                        </Button>
                    )}
                </div>
            </div>

            {/* Tenant Info Card */}
            <Card>
                <CardHeader>
                    <CardTitle>Tenant Information</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4 md:grid-cols-2">
                    <div className="flex items-center gap-3">
                        <Building2 className="h-5 w-5 text-muted-foreground" />
                        <div>
                            <p className="text-sm text-muted-foreground">Business Name</p>
                            <p className="font-medium">{tenant.name}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Mail className="h-5 w-5 text-muted-foreground" />
                        <div>
                            <p className="text-sm text-muted-foreground">Contact Email</p>
                            <p className="font-medium">{tenant.email || "N/A"}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Activity className="h-5 w-5 text-muted-foreground" />
                        <div>
                            <p className="text-sm text-muted-foreground">Status</p>
                            <Badge variant={tenant.status === "active" ? "default" : "destructive"}>
                                {tenant.status}
                            </Badge>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Phone className="h-5 w-5 text-muted-foreground" />
                        <div>
                            <p className="text-sm text-muted-foreground">Plan</p>
                            <Badge variant="outline" className="capitalize">
                                {tenant.plan || "Free"}
                            </Badge>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenantUsers.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Appointments</CardTitle>
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenantAppointments.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Conversations</CardTitle>
                        <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenantConversations.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
                        <Phone className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenant.total_calls || 0}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Users Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Users</CardTitle>
                </CardHeader>
                <CardContent>
                    {loadingUsers ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                    ) : tenantUsers.length === 0 ? (
                        <p className="text-center text-muted-foreground py-8">No users found</p>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Username</TableHead>
                                    <TableHead>Role</TableHead>
                                    <TableHead>Status</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {tenantUsers.map((user: any) => (
                                    <TableRow key={user.id}>
                                        <TableCell className="font-medium">{user.full_name}</TableCell>
                                        <TableCell>{user.email}</TableCell>
                                        <TableCell>{user.username}</TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="capitalize">
                                                {user.role}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={user.active ? "default" : "secondary"}>
                                                {user.active ? "Active" : "Inactive"}
                                            </Badge>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
