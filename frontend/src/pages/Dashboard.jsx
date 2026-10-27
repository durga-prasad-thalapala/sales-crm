import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import { getAccessToken } from "../services/auth";
import "./Dashboard.css";

function Dashboard() {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadDashboard() {
            try {
                const result = await apiRequest("/dashboard/", {
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                });

                setData(result);
            } catch (error) {
                setError(error.message);
            }
        }

        loadDashboard();
    }, []);

    if (error) {
        return <p>{error}</p>;
    }

    if (!data) {
        return <p>Loading dashboard...</p>;
    }

    return (
    <div className="dashboard">
        <h1>CRM Dashboard</h1>

        <div className="dashboard-section">
            <h2>Sales Overview</h2>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Leads</h3>
                    <p>{data.leads.total}</p>
                </div>

                <div className="stat-card">
                    <h3>Converted Leads</h3>
                    <p>{data.leads.converted}</p>
                </div>

                <div className="stat-card">
                    <h3>Total Customers</h3>
                    <p>{data.customers.total}</p>
                </div>

                <div className="stat-card">
                    <h3>Total Deals</h3>
                    <p>{data.deals.total}</p>
                </div>
            </div>
        </div>

        <div className="dashboard-section">
            <h2>Deal Pipeline</h2>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Open Deals</h3>
                    <p>{data.deals.open}</p>
                </div>

                <div className="stat-card">
                    <h3>Won Deals</h3>
                    <p>{data.deals.won}</p>
                </div>

                <div className="stat-card">
                    <h3>Lost Deals</h3>
                    <p>{data.deals.lost}</p>
                </div>

                <div className="stat-card">
                    <h3>Pipeline Value</h3>
                    <p>₹{data.deals.pipeline_value}</p>
                </div>
            </div>
        </div>

        <div className="dashboard-section">
            <h2>Activities</h2>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Activities</h3>
                    <p>{data.activities.total}</p>
                </div>

                <div className="stat-card">
                    <h3>Completed</h3>
                    <p>{data.activities.completed}</p>
                </div>

                <div className="stat-card">
                    <h3>Pending</h3>
                    <p>{data.activities.pending}</p>
                </div>
            </div>
        </div>
    </div>
    );
}

export default Dashboard;