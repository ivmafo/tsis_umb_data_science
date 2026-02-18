import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface MainLayoutProps {
    children: ReactNode;
    currentView: string;
    onNavigate: (view: string) => void;
}

export const MainLayout = ({ children, currentView, onNavigate }: MainLayoutProps) => {
    return (
        <div className="min-h-screen bg-slate-50 flex">
            <Sidebar currentView={currentView} onSelect={onNavigate} />
            <main className="flex-1 ml-72 p-8 transition-all duration-300">
                <div className="max-w-[1600px] mx-auto animate-fade-in">
                    {children}
                </div>
            </main>
        </div>
    );
};
