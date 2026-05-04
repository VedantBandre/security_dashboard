import React, { useEffect, useState, useCallback } from 'react';
import { fetchSuspicious } from '../api';
import EventTable from '../components/EventTable';

export default function SuspiciousPage() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const load = useCallback(async () => {
        try {
            const data = await fetchSuspicious();
            setEvents(data);
            setError(null);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, []);
    
    useEffect(() => {
        load();
        const id = setInterval(load, 5000);
        return () => clearInterval(id);
    }, [load]);
    
    return (
        <section className="page">
            <div className="page-header">
                <h1>! Suspicious Activity !</h1>
                <button className="btn" onClick={load}>Refresh</button>
            </div>

            {error && <div className="error-banner">! {error} !</div>}

            {!loading && events.length === 0 && (
                <div className="empty all-clear">No suspicious activity detected</div>
            )}

            <EventTable events={events} loading={loading} />
        </section>
    );
}