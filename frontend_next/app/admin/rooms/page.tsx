"use client";

import React, { useEffect, useState } from 'react';
import { livekitApi, type LiveKitRoom, type LiveKitParticipant, type LiveKitStatus } from '@/lib/api/livekit';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { 
  Video, 
  Users, 
  Plus, 
  Trash2, 
  RefreshCw, 
  CheckCircle2, 
  XCircle,
  Clock,
  Eye,
  Server,
  Wifi,
  UserMinus
} from 'lucide-react';
import { toast } from 'sonner';

export default function LiveKitRoomsPage() {
  const [rooms, setRooms] = useState<LiveKitRoom[]>([]);
  const [status, setStatus] = useState<LiveKitStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState<LiveKitRoom | null>(null);
  const [participants, setParticipants] = useState<LiveKitParticipant[]>([]);
  const [participantsDialogOpen, setParticipantsDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  
  // Form state
  const [newRoomName, setNewRoomName] = useState('');
  const [emptyTimeout, setEmptyTimeout] = useState(600);
  const [maxParticipants, setMaxParticipants] = useState(20);

  const fetchStatus = async () => {
    try {
      const data = await livekitApi.getStatus();
      setStatus(data);
    } catch (error: any) {
      console.error('Failed to fetch status:', error);
    }
  };

  const fetchRooms = async () => {
    try {
      setLoading(true);
      const data = await livekitApi.listAllRooms();
      setRooms(data);
    } catch (error: any) {
      console.error('Failed to fetch rooms:', error);
      toast.error(error.message || 'Failed to fetch rooms');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchRooms();
  }, []);

  const handleCreateRoom = async () => {
    if (!newRoomName.trim()) {
      toast.error('Room name is required');
      return;
    }

    try {
      setCreating(true);
      await livekitApi.createRoom({
        room_name: newRoomName,
        empty_timeout: emptyTimeout,
        max_participants: maxParticipants,
      });
      toast.success(`Room "${newRoomName}" created successfully`);
      setNewRoomName('');
      setCreateDialogOpen(false);
      fetchRooms();
    } catch (error: any) {
      toast.error(error.message || 'Failed to create room');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteRoom = async (roomName: string) => {
    try {
      await livekitApi.deleteRoom(roomName);
      toast.success(`Room deleted successfully`);
      fetchRooms();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete room');
    }
  };

  const handleViewParticipants = async (room: LiveKitRoom) => {
    setSelectedRoom(room);
    setParticipantsDialogOpen(true);
    try {
      const data = await livekitApi.listParticipants(room.name);
      setParticipants(data);
    } catch (error: any) {
      toast.error(error.message || 'Failed to fetch participants');
      setParticipants([]);
    }
  };

  const handleRemoveParticipant = async (identity: string) => {
    if (!selectedRoom) return;
    try {
      await livekitApi.removeParticipant(selectedRoom.name, identity);
      toast.success(`Participant "${identity}" removed`);
      const data = await livekitApi.listParticipants(selectedRoom.name);
      setParticipants(data);
    } catch (error: any) {
      toast.error(error.message || 'Failed to remove participant');
    }
  };

  const formatTimestamp = (timestamp?: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };

  const extractTenantId = (roomName: string) => {
    if (roomName.startsWith('tenant_')) {
      const parts = roomName.split('_');
      return parts[1] || 'Unknown';
    }
    if (roomName.startsWith('preview-')) {
      const parts = roomName.split('-');
      return parts[1] || 'Unknown';
    }
    return 'N/A';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">LiveKit Rooms</h1>
          <p className="text-muted-foreground mt-1">
            Manage active voice rooms and participants
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchRooms} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Room
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Room</DialogTitle>
                <DialogDescription>
                  Create a new LiveKit room for voice calls.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="roomName">Room Name</Label>
                  <Input
                    id="roomName"
                    placeholder="e.g., meeting-1"
                    value={newRoomName}
                    onChange={(e) => setNewRoomName(e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="emptyTimeout">Empty Timeout (seconds)</Label>
                  <Input
                    id="emptyTimeout"
                    type="number"
                    min={60}
                    max={86400}
                    value={emptyTimeout}
                    onChange={(e) => setEmptyTimeout(parseInt(e.target.value))}
                  />
                  <p className="text-xs text-muted-foreground">
                    Room will be deleted after this many seconds of being empty
                  </p>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="maxParticipants">Max Participants</Label>
                  <Input
                    id="maxParticipants"
                    type="number"
                    min={2}
                    max={100}
                    value={maxParticipants}
                    onChange={(e) => setMaxParticipants(parseInt(e.target.value))}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateRoom} disabled={creating}>
                  {creating ? 'Creating...' : 'Create Room'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Status Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Server className="w-5 h-5" />
            LiveKit Server Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              {status?.configured ? (
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500" />
              )}
              <span className="font-medium">
                {status?.configured ? 'Connected' : 'Not Configured'}
              </span>
            </div>
            {status?.server_url && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Wifi className="w-4 h-4" />
                <span className="text-sm font-mono">{status.server_url}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-muted-foreground">
              <Video className="w-4 h-4" />
              <span className="text-sm">Agent: {status?.agent_name || 'N/A'}</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="w-4 h-4" />
              <span className="text-sm">Queue: {status?.agent_queue || 'N/A'}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rooms Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active Rooms ({rooms.length})</CardTitle>
          <CardDescription>
            All active voice rooms across all tenants
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : rooms.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Video className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No active rooms</p>
              <p className="text-sm">Rooms will appear here when voice calls are active</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Room Name</TableHead>
                  <TableHead>Tenant ID</TableHead>
                  <TableHead>Participants</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Timeout</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rooms.map((room) => (
                  <TableRow key={room.sid || room.name}>
                    <TableCell className="font-mono text-sm">
                      {room.name}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {extractTenantId(room.name)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={room.num_participants > 0 ? 'default' : 'secondary'}>
                        {room.num_participants} / {room.max_participants}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatTimestamp(room.created_at)}
                    </TableCell>
                    <TableCell>
                      <span className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        {room.empty_timeout}s
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewParticipants(room)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="sm" className="text-destructive">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete Room?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This will disconnect all participants and delete the room.
                                This action cannot be undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() => handleDeleteRoom(room.name)}
                                className="bg-destructive text-destructive-foreground"
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Participants Dialog */}
      <Dialog open={participantsDialogOpen} onOpenChange={setParticipantsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Room Participants</DialogTitle>
            <DialogDescription>
              {selectedRoom?.name}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {participants.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No participants in this room</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Identity</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>State</TableHead>
                    <TableHead>Publisher</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {participants.map((p) => (
                    <TableRow key={p.sid || p.identity}>
                      <TableCell className="font-mono text-sm">
                        {p.identity}
                      </TableCell>
                      <TableCell>{p.name || 'N/A'}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{p.state || 'unknown'}</Badge>
                      </TableCell>
                      <TableCell>
                        {p.is_publisher ? (
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-muted-foreground" />
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          onClick={() => handleRemoveParticipant(p.identity)}
                        >
                          <UserMinus className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
