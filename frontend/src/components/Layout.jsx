import { NavLink, Outlet, useNavigate, Navigate } from "react-router-dom";
import { logout, isAuthenticated } from "../services/auth";
import "./Layout.css";

function Layout() {
    const navigate = useNavigate();
    if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
    }


    function handleLogout() {
        logout();
        navigate("/login");
    }

    return (
        <div className="app-layout">
            <aside className="sidebar">
                <h2>Sales CRM</h2>

                <nav>
                    <NavLink to="/dashboard">Dashboard</NavLink>
                    <NavLink to="/leads">Leads</NavLink>
                    <NavLink to="/customers">Customers</NavLink>
                    <NavLink to="/deals">Deals</NavLink>
                    <NavLink to="/activities">Activities</NavLink>
                </nav>

                <button onClick={handleLogout}>
                    Logout
                </button>
            </aside>

            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}

export default Layout;