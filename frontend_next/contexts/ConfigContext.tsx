"use client";

import React, { createContext, useContext } from 'react';
import { useConfig as useConfigHook } from '@/hooks/use-config';
import { BusinessConfig } from '@/lib/api/business-config';

interface ConfigContextType {
    config: BusinessConfig | undefined;
    isLoading: boolean;
    error: Error | null;
    refreshConfig: () => Promise<any>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { config, isLoading, error, refetch } = useConfigHook();

    return (
        <ConfigContext.Provider value={{ config, isLoading, error, refreshConfig: refetch }}>
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
