import { useState, useEffect } from 'react';
import { getOrCreateVisitorId } from '@/lib/utils/visitor';

export function useVisitorId() {
    const [visitorId, setVisitorId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        getOrCreateVisitorId()
            .then(id => {
                setVisitorId(id);
                setLoading(false);
            })
            .catch(error => {
                console.error('Failed to get visitor ID:', error);
                setLoading(false);
            });
    }, []);
    
    return { visitorId, loading };
}
