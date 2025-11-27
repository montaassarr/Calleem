"use client";

import React, { useEffect, useState } from 'react';
import { DataTable } from '@/components/admin/DataTable';
import { CrudModal } from '@/components/admin/CrudModal';
import { DeleteDialog } from '@/components/admin/DeleteDialog';
import { adminApi, Service } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';

export default function ServicesPage() {
    const [services, setServices] = useState<Service[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [pageSize] = useState(10);

    // Modal states
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [selectedService, setSelectedService] = useState<Service | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        duration_minutes: 30,
        price: 0,
        active: true
    });

    const { toast } = useToast();

    const fetchServices = async () => {
        try {
            setLoading(true);
            const data = await adminApi.getServices((page - 1) * pageSize, pageSize);

            if (Array.isArray(data)) {
                setServices(data);
                setTotal(data.length);
            } else {
                setServices(data.items || []);
                setTotal(data.total || 0);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch services",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchServices();
    }, [page]);

    const handleAdd = () => {
        setSelectedService(null);
        setFormData({
            name: '',
            description: '',
            duration_minutes: 30,
            price: 0,
            active: true
        });
        setIsModalOpen(true);
    };

    const handleEdit = (service: Service) => {
        setSelectedService(service);
        setFormData({
            name: service.name,
            description: service.description || '',
            duration_minutes: service.duration_minutes,
            price: service.price || 0,
            active: service.active
        });
        setIsModalOpen(true);
    };

    const handleDeleteClick = (service: Service) => {
        setSelectedService(service);
        setIsDeleteOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setIsSubmitting(true);
            if (selectedService) {
                await adminApi.updateService(selectedService.id, formData);
                toast({ title: "Success", description: "Service updated successfully" });
            } else {
                await adminApi.createService(formData);
                toast({ title: "Success", description: "Service created successfully" });
            }
            setIsModalOpen(false);
            fetchServices();
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
        if (!selectedService) return;
        try {
            setIsSubmitting(true);
            await adminApi.deleteService(selectedService.id);
            toast({ title: "Success", description: "Service deleted successfully" });
            setIsDeleteOpen(false);
            fetchServices();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete service",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const columns = [
        { key: 'name', label: 'Service Name' },
        {
            key: 'duration_minutes',
            label: 'Duration',
            render: (mins: number) => `${mins} min`
        },
        {
            key: 'price',
            label: 'Price',
            render: (price: number) => `$${price}`
        },
        {
            key: 'active',
            label: 'Status',
            render: (active: boolean) => (
                <Badge variant={active ? 'default' : 'secondary'}>
                    {active ? 'Active' : 'Inactive'}
                </Badge>
            )
        }
    ];

    return (
        <div className="p-6">
            <DataTable
                title="Services"
                columns={columns}
                data={services}
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
                title={selectedService ? "Edit Service" : "New Service"}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Service Name</Label>
                        <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="duration">Duration (minutes)</Label>
                            <Input
                                id="duration"
                                type="number"
                                value={formData.duration_minutes}
                                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="price">Price ($)</Label>
                            <Input
                                id="price"
                                type="number"
                                step="0.01"
                                value={formData.price}
                                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                            />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                            id="description"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        />
                    </div>
                    <div className="flex items-center space-x-2">
                        <Switch
                            id="active"
                            checked={formData.active}
                            onCheckedChange={(checked) => setFormData({ ...formData, active: checked })}
                        />
                        <Label htmlFor="active">Active Service</Label>
                    </div>
                    <div className="flex justify-end space-x-2 pt-4">
                        <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                        <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting ? "Saving..." : "Save Service"}
                        </Button>
                    </div>
                </form>
            </CrudModal>

            <DeleteDialog
                open={isDeleteOpen}
                onOpenChange={setIsDeleteOpen}
                onConfirm={handleDeleteConfirm}
                title="Delete Service"
                description="Are you sure you want to delete this service?"
                isLoading={isSubmitting}
            />
        </div>
    );
}
