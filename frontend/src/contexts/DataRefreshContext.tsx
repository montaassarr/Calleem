/**
 * Global Data Refresh Context
 * 
 * Provides centralized mechanism to trigger data refetches across all pages
 * Prevents stale data and ensures real-time synchronization
 */

import React, { createContext, useContext, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface DataRefreshContextType {
  refreshAll: () => void;
  refreshAppointments: () => void;
  refreshConversations: () => void;
  refreshServices: () => void;
  refreshDashboard: () => void;
}

const DataRefreshContext = createContext<DataRefreshContextType | undefined>(undefined);

export const DataRefreshProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient();

  const refreshAppointments = useCallback(() => {
    console.log('🔄 Refreshing appointments data...');
    queryClient.invalidateQueries({ queryKey: ['appointments'] });
  }, [queryClient]);

  const refreshConversations = useCallback(() => {
    console.log('🔄 Refreshing conversations data...');
    queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }, [queryClient]);

  const refreshServices = useCallback(() => {
    console.log('🔄 Refreshing services data...');
    queryClient.invalidateQueries({ queryKey: ['services'] });
  }, [queryClient]);

  const refreshDashboard = useCallback(() => {
    console.log('🔄 Refreshing dashboard data...');
    queryClient.invalidateQueries({ queryKey: ['appointments'] });
    queryClient.invalidateQueries({ queryKey: ['conversations'] });
    queryClient.invalidateQueries({ queryKey: ['services'] });
    queryClient.invalidateQueries({ queryKey: ['webhook-status'] });
  }, [queryClient]);

  const refreshAll = useCallback(() => {
    console.log('🔄 Refreshing ALL data...');
    queryClient.invalidateQueries(); // Invalidate ALL queries
  }, [queryClient]);

  const value = {
    refreshAll,
    refreshAppointments,
    refreshConversations,
    refreshServices,
    refreshDashboard,
  };

  return (
    <DataRefreshContext.Provider value={value}>
      {children}
    </DataRefreshContext.Provider>
  );
};

export const useDataRefresh = () => {
  const context = useContext(DataRefreshContext);
  if (context === undefined) {
    throw new Error('useDataRefresh must be used within DataRefreshProvider');
  }
  return context;
};
