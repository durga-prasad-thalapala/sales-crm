
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Customers from "./pages/Customers";
import Deals from "./pages/Deals";
import Activities from "./pages/Activities";
import Layout from "./components/Layout";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Login */}
                <Route path="/login" element={<Login />} />

                {/* CRM Layout */}
                <Route element={<Layout />}>
                    <Route
                        path="/dashboard"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/leads"
                        element={<Leads />}
                    />

                    <Route
                        path="/customers"
                        element={<Customers />}
                    />

                    <Route
                        path="/deals"
                        element={<Deals />}
                    />

                    <Route
                        path="/activities"
                        element={<Activities />}
                    />
                </Route>

                {/* Unknown routes */}
                <Route
                    path="*"
                    element={<Navigate to="/login" replace />}
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
