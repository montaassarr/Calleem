"use client";

import React, { useEffect, useState } from 'react';
import { DataTable } from '@/components/admin/DataTable';
import { CrudModal } from '@/components/admin/CrudModal';
import { DeleteDialog } from '@/components/admin/DeleteDialog';
import { adminApi, User } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';

export default function UsersPage() {
    const { user: currentUser } = useAuth();
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [pageSize] = useState(10);

    // Modal states
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: 'staff',
        tenant_id: currentUser?.tenant_id || '',
        permissions: '',
        active: true
    });

    const { toast } = useToast();

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const data = await adminApi.getUsers((page - 1) * pageSize, pageSize);
            // Handle different response formats (list or paginated object)
            if (Array.isArray(data)) {
                setUsers(data);
                setTotal(data.length); // If API doesn't return total, assume list length
            } else {
                setUsers(data.items || []);
                setTotal(data.total || 0);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch users",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [page]);

    const handleAdd = () => {
        setSelectedUser(null);
        setFormData({
            username: '',
            email: '',
            password: '',
            full_name: '',
            role: 'staff',
            tenant_id: currentUser?.tenant_id || '',
            permissions: '',
            active: true
        });
        setIsModalOpen(true);
    };

    const handleEdit = (user: User) => {
        setSelectedUser(user);
        setFormData({
            username: user.username,
            email: user.email,
            password: '', // Don't show password
            full_name: (user as any).full_name || '',
            role: user.role,
            tenant_id: user.tenant_id || currentUser?.tenant_id || '',
            permissions: user.permissions ? user.permissions.join(', ') : '',
            active: user.active
        });
        setIsModalOpen(true);
    };

    const handleDeleteClick = (user: User) => {
        setSelectedUser(user);
        setIsDeleteOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setIsSubmitting(true);
            if (selectedUser) {
                // Update
                const updateData: any = {
                    ...formData,
                    permissions: formData.permissions ? formData.permissions.split(',').map(p => p.trim()) : []
                };
                if (!updateData.password) delete updateData.password;
                await adminApi.updateUser(selectedUser.id, updateData);
                toast({ title: "Success", description: "User updated successfully" });
            } else {
                // Create
                await adminApi.createUser({
                    ...formData,
                    permissions: formData.permissions ? formData.permissions.split(',').map(p => p.trim()) : []
                });
                toast({ title: "Success", description: "User created successfully" });
            }
            setIsModalOpen(false);
            fetchUsers();
        } catch (error: any) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Operation failed",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteConfirm = async () => {
        if (!selectedUser) return;
        try {
            setIsSubmitting(true);
            await adminApi.deleteUser(selectedUser.id);
            toast({ title: "Success", description: "User deleted successfully" });
            setIsDeleteOpen(false);
            fetchUsers();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete user",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleImpersonate = async (user: User) => {
        try {
            const response = await adminApi.impersonateUser(user.id);
            // Store the new token
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('tenant_id', user.tenant_id || '');
            localStorage.setItem('impersonating', 'true');
            localStorage.setItem('original_admin', 'true');

            toast({
                title: "Impersonation Started",
                description: `Now viewing as ${user.username}. Redirecting to dashboard...`
            });

            // Redirect to tenant dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } catch (error: any) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to impersonate user",
                variant: "destructive"
            });
        }
    };

    const columns = [
        { key: 'username', label: 'Username' },
        { key: 'email', label: 'Email' },
        {
            key: 'role',
            label: 'Role',
            render: (role: string) => (
                <Badge variant={role === 'owner' || role === 'admin' ? 'default' : 'secondary'}>
                    {role}
                </Badge>
            )
        },
        {
            key: 'active',
            label: 'Status',
            render: (active: boolean) => (
                <Badge variant={active ? 'outline' : 'destructive'} className={active ? "text-green-600 border-green-600" : ""}>
                    {active ? 'Active' : 'Inactive'}
                </Badge>
            )
        },
        {
            key: 'created_at',
            label: 'Created At',
            render: (date: string) => new Date(date).toLocaleDateString()
        },
        {
            key: 'actions',
            label: 'Actions',
            render: (_: any, user: User) => (
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleImpersonate(user)}
                >
                    Impersonate
                </Button>
            )
        }
    ];

    return (
        <div className="p-6">
            <DataTable
                title="Users Management"
                columns={columns}
                data={users}
                total={total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onAdd={handleAdd}
                onEdit={handleEdit}
                onDelete={handleDeleteClick}
                isLoading={loading}
            />

            <CrudModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                title={selectedUser ? "Edit User" : "Add New User"}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                required
                                disabled={!!selectedUser} // Username usually immutable
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="full_name">Full Name</Label>
                            <Input
                                id="full_name"
                                value={formData.full_name}
                                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="role">Role</Label>
                            <Select
                                value={formData.role}
                                onValueChange={(value) => setFormData({ ...formData, role: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select role" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="owner">Owner</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                    <SelectItem value="staff">Staff</SelectItem>
                                    <SelectItem value="viewer">Viewer</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        {/* Only show tenant_id field for super_admin */}
                        {currentUser?.role === 'super_admin' && (
                            <div className="space-y-2">
                                <Label htmlFor="tenant_id">Tenant ID</Label>
                                <Input
                                    id="tenant_id"
                                    value={formData.tenant_id}
                                    onChange={(e) => setFormData({ ...formData, tenant_id: e.target.value })}
                                    placeholder="Auto-assigned if empty"
                                />
                            </div>
                        )}
                        <div className="space-y-2 col-span-2">
                            <Label htmlFor="permissions">Permissions (comma separated)</Label>
                            <Input
                                id="permissions"
                                value={formData.permissions}
                                onChange={(e) => setFormData({ ...formData, permissions: e.target.value })}
                                placeholder="e.g. manage_users, view_reports"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password {selectedUser && "(Leave blank to keep current)"}</Label>
                            <Input
                                id="password"
                                type="password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                required={!selectedUser}
                            />
                        </div>
                        <div className="space-y-2 flex items-end pb-2">
                            <label className="flex items-center space-x-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.active}
                                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                                    className="h-4 w-4 rounded border-gray-300"
                                />
                                <span>Active Account</span>
                            </label>
                        </div>
                    </div>
                    <div className="flex justify-end space-x-2 pt-4">
                        <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                        <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting ? "Saving..." : "Save User"}
                        </Button>
                    </div>
                </form>
            </CrudModal>

            <DeleteDialog
                open={isDeleteOpen}
                onOpenChange={setIsDeleteOpen}
                onConfirm={handleDeleteConfirm}
                title="Delete User"
                description={`Are you sure you want to delete user ${selectedUser?.username}? This action cannot be undone.`}
                isLoading={isSubmitting}
            />
        </div>
    );
}
