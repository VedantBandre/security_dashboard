import React, { useEffect, useState, useCallback } from 'react';
import { fetchEvents, fetchStats } from '../api';
import EventTable from '../components/EventTable';
import StatCard from '../components/StatCard';

export default function Dashboard() {
    const [events, setEvents] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastRefresh, setLastRefresh] = useState(null);

    const load = useCallback(async () => {
        try{
            const [evts, st] = await Promise.all([fetchEvents(), fetchStats()]);
            setEvents(evts);
            setStats(st);
            setLastRefresh(new Date());
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
                <h1>Event Dashboard</h1>
                {lastRefresh && (
                    <span className="refresh-note">
                        Last refresh: {lastRefresh.toLocaleTimeString()}
                    </span>
                )}
                <button className="btn" onClick={load}>Refresh</button>
            </div>

            {error && <div className="error-banner">! {error} !</div>}

            <div className="stats-row">
                <StatCard label="Total Events" value={stats?.total} variant="default" />
                <StatCard label="Successful Logins" value={stats?.succeeded} variant="ok" />
                <StatCard label="Failed Logins" value={stats?.failed} variant="fail" />
                <StatCard label="Suspicious IPs" value={stats?.suspicious} variant="alert" />
            </div>

            <EventTable events={events} loading={loading} />
        </section>
    );
}