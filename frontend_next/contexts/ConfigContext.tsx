"use client";

import React, { createContext, useContext } from 'react';
import { useConfig as useConfigHook } from '@/hooks/use-config';
import { BusinessConfig } from '@/lib/api/business-config';
import { useAuth } from './AuthContext';

interface ConfigContextType {
    config: BusinessConfig | undefined;
    isLoading: boolean;
    error: Error | null;
    refreshConfig: () => Promise<any>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { user, isAuthenticated, isLoading: authLoading } = useAuth();
    
    // CRITICAL: Use tenant_id from the authenticated user to ensure each tenant has their own config cache
    // This prevents config data from being shared between different tenants in React Query's cache
    // Without this, all tenants would share the same 'default' cache key and see each other's data
    const tenantId = user?.tenant_id || 'default';
    
    // Only fetch config if user is authenticated
    const { config, isLoading, error, refetch } = useConfigHook(tenantId, isAuthenticated);

    return (
        <ConfigContext.Provider value={{ config, isLoading: isLoading || authLoading, error, refreshConfig: refetch }}>
            {children}
        </ConfigContext.Provider>
    );
};

export const useConfig = () => {
    const context = useContext(ConfigContext);
    if (context === undefined) {
        throw new Error('useConfig must be used within a ConfigProvider');
    }
    return context;
};
