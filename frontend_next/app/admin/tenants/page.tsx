"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Search, Building2, Activity, CheckCircle2, XCircle, Trash2, Eye } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

interface Tenant {
    id: string;
    name: string;
    email?: string;
    plan: string;
    status: string;
    created_at: string;
    total_calls?: number;
    total_minutes?: number;
    settings?: {
        business_name?: string;
        phone?: string;
    };
}

export default function TenantsAdminPage() {
    const [search, setSearch] = useState("");
    const [tenantToDelete, setTenantToDelete] = useState<Tenant | null>(null);
    const queryClient = useQueryClient();

    // Fetch all tenants
    const { data: tenants = [], isLoading, refetch } = useQuery<Tenant[]>({
        queryKey: ["admin-tenants"],
        queryFn: async (): Promise<Tenant[]> => {
            const response = await adminApi.getTenants(0, 100);
            return (Array.isArray(response) ? response : response.items).map((tenant) => tenant as unknown as Tenant);
        },
    });

    // Delete tenant mutation
    const deleteMutation = useMutation({
        mutationFn: async (tenantId: string) => {
            await adminApi.deleteTenant(tenantId);
        },
        onSuccess: () => {
            toast.success("Tenant deleted successfully");
            queryClient.invalidateQueries({ queryKey: ["admin-tenants"] });
            setTenantToDelete(null);
        },
        onError: (error: any) => {
            toast.error(error.message || "Failed to delete tenant");
        },
    });

    // Filter by search
    const filteredTenants = tenants.filter((tenant) => {
        const searchLower = search.toLowerCase();
        return (
            tenant.name?.toLowerCase().includes(searchLower) ||
            tenant.email?.toLowerCase().includes(searchLower) ||
            tenant.settings?.business_name?.toLowerCase().includes(searchLower)
        );
    });

    // Calculate stats
    const totalTenants = tenants.length;
    const activeTenants = tenants.filter((t) => t.status === "active").length;
    const totalCalls = tenants.reduce((sum, t) => sum + (t.total_calls || 0), 0);
    const totalMinutes = tenants.reduce((sum, t) => sum + (t.total_minutes || 0), 0);

    const handleDelete = (tenant: Tenant) => {
        setTenantToDelete(tenant);
    };

    const confirmDelete = () => {
        if (tenantToDelete) {
            deleteMutation.mutate(tenantToDelete.id);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading tenants...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">Tenant Management</h1>
                <p className="text-muted-foreground">
                    Manage all tenant accounts and their data
                </p>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Tenants</CardTitle>
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalTenants}</div>
                        <p className="text-xs text-muted-foreground">All registered tenants</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Tenants</CardTitle>
                        <Activity className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">{activeTenants}</div>
                        <p className="text-xs text-muted-foreground">Currently active</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
                        <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">{totalCalls}</div>
                        <p className="text-xs text-muted-foreground">Across all tenants</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Minutes</CardTitle>
                        <Activity className="h-4 w-4 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-purple-600">
                            {totalMinutes.toFixed(0)}
                        </div>
                        <p className="text-xs text-muted-foreground">Call time used</p>
                    </CardContent>
                </Card>
            </div>

            {/* Search and Actions */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>All Tenants ({filteredTenants.length})</CardTitle>
                        <div className="flex gap-2">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search tenants..."
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="pl-10 w-[300px]"
                                />
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Business Name</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Plan</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Calls</TableHead>
                                    <TableHead>Minutes</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredTenants.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={8} className="text-center text-muted-foreground">
                                            No tenants found
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    filteredTenants.map((tenant) => (
                                        <TableRow key={tenant.id}>
                                            <TableCell className="font-medium">
                                                {tenant.settings?.business_name || tenant.name}
                                            </TableCell>
                                            <TableCell>{tenant.email}</TableCell>
                                            <TableCell>
                                                <Badge variant={tenant.plan === "pro" ? "default" : "secondary"}>
                                                    {tenant.plan || "free"}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                {tenant.status === "active" ? (
                                                    <Badge variant="default" className="bg-green-600">
                                                        <CheckCircle2 className="w-3 h-3 mr-1" />
                                                        Active
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="secondary">
                                                        <XCircle className="w-3 h-3 mr-1" />
                                                        Inactive
                                                    </Badge>
                                                )}
                                            </TableCell>
                                            <TableCell>{tenant.total_calls || 0}</TableCell>
                                            <TableCell>{(tenant.total_minutes || 0).toFixed(1)}</TableCell>
                                            <TableCell>
                                                {tenant.created_at
                                                    ? format(new Date(tenant.created_at), "MMM d, yyyy")
                                                    : "N/A"}
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <div className="flex justify-end gap-2">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => window.location.href = `/admin/tenants/${tenant.id}`}
                                                    >
                                                        <Eye className="w-4 h-4" />
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleDelete(tenant)}
                                                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={!!tenantToDelete} onOpenChange={() => setTenantToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will permanently delete the tenant <strong>{tenantToDelete?.name}</strong> and all
                            associated data including:
                            <ul className="mt-2 ml-4 list-disc text-sm">
                                <li>All users under this tenant</li>
                                <li>All appointments</li>
                                <li>All services</li>
                                <li>All conversations</li>
                                <li>Business configuration</li>
                            </ul>
                            <p className="mt-2 font-semibold text-red-600">This action cannot be undone!</p>
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={confirmDelete}
                            className="bg-red-600 hover:bg-red-700"
                            disabled={deleteMutation.isPending}
                        >
                            {deleteMutation.isPending ? "Deleting..." : "Delete Tenant"}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
