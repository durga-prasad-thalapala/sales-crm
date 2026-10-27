import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import { getAccessToken } from "../services/auth";
import "./Leads.css";

function Leads() {
    const [leads, setLeads] = useState([]);
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [source, setSource] = useState("");

    const [showForm, setShowForm] = useState(false);
    const [editingLead, setEditingLead] = useState(null);

    const [formData, setFormData] = useState({
        name: "",
        company: "",
        email: "",
        phone: "",
        source: "WEBSITE",
        status: "NEW",
        notes: "",
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    async function loadLeads() {
        try {
            setLoading(true);
            setError("");

            const params = new URLSearchParams();

            if (search) params.append("search", search);
            if (status) params.append("status", status);
            if (source) params.append("source", source);

            const query = params.toString();

            const data = await apiRequest(
                `/leads/${query ? `?${query}` : ""}`,
                {
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                }
            );

            setLeads(data.results);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadLeads();
    }, [status, source]);

    function handleSearch(event) {
        event.preventDefault();
        loadLeads();
    }

    function handleInputChange(event) {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    function openCreateForm() {
        setEditingLead(null);

        setFormData({
            name: "",
            company: "",
            email: "",
            phone: "",
            source: "WEBSITE",
            status: "NEW",
            notes: "",
        });

        setFormError("");
        setShowForm(true);
    }

    function openEditForm(lead) {
        setEditingLead(lead);

        setFormData({
            name: lead.name,
            company: lead.company,
            email: lead.email,
            phone: lead.phone,
            source: lead.source,
            status: lead.status,
            notes: lead.notes || "",
        });

        setFormError("");
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingLead(null);
        setFormError("");
    }

    async function handleSubmit(event) {
        event.preventDefault();

        try {
            setFormError("");

            if (editingLead) {
                await apiRequest(`/leads/${editingLead.id}/`, {
                    method: "PATCH",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                    body: JSON.stringify(formData),
                });
            } else {
                await apiRequest("/leads/", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                    body: JSON.stringify(formData),
                });
            }

            closeForm();
            await loadLeads();
        } catch (error) {
            setFormError(error.message);
        }
    }

    async function handleDelete(leadId) {
        const confirmed = window.confirm(
            "Are you sure you want to delete this lead?"
        );

        if (!confirmed) {
            return;
        }

        try {
            await apiRequest(`/leads/${leadId}/`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
            });

            await loadLeads();
        } catch (error) {
            setError(error.message);
        }
    }

    return (
        <div className="leads-page">
            <div className="leads-header">
                <h1>Leads</h1>

                <button
                    className="add-lead-button"
                    onClick={showForm ? closeForm : openCreateForm}
                >
                    {showForm
                        ? "Close Form"
                        : "+ Add Lead"}
                </button>
            </div>

            {showForm && (
                <div className="lead-form-card">
                    <h2>
                        {editingLead
                            ? "Edit Lead"
                            : "Add New Lead"}
                    </h2>

                    {formError && (
                        <p className="form-error">
                            {formError}
                        </p>
                    )}

                    <form onSubmit={handleSubmit}>
                        <div className="form-grid">
                            <input
                                name="name"
                                placeholder="Name"
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                            />

                            <input
                                name="company"
                                placeholder="Company"
                                value={formData.company}
                                onChange={handleInputChange}
                                required
                            />

                            <input
                                type="email"
                                name="email"
                                placeholder="Email"
                                value={formData.email}
                                onChange={handleInputChange}
                                required
                            />

                            <input
                                name="phone"
                                placeholder="Phone"
                                value={formData.phone}
                                onChange={handleInputChange}
                                required
                            />

                            <select
                                name="source"
                                value={formData.source}
                                onChange={handleInputChange}
                            >
                                <option value="WEBSITE">
                                    Website
                                </option>
                                <option value="REFERRAL">
                                    Referral
                                </option>
                                <option value="LINKEDIN">
                                    LinkedIn
                                </option>
                                <option value="EMAIL">
                                    Email
                                </option>
                                <option value="COLD_CALL">
                                    Cold Call
                                </option>
                                <option value="OTHER">
                                    Other
                                </option>
                            </select>

                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleInputChange}
                            >
                                <option value="NEW">
                                    New
                                </option>
                                <option value="CONTACTED">
                                    Contacted
                                </option>
                                <option value="QUALIFIED">
                                    Qualified
                                </option>
                                <option value="CONVERTED">
                                    Converted
                                </option>
                                <option value="LOST">
                                    Lost
                                </option>
                            </select>
                        </div>

                        <textarea
                            name="notes"
                            placeholder="Notes"
                            value={formData.notes}
                            onChange={handleInputChange}
                        />

                        <button
                            type="submit"
                            className="save-lead-button"
                        >
                            {editingLead
                                ? "Update Lead"
                                : "Save Lead"}
                        </button>
                    </form>
                </div>
            )}

            <div className="lead-filters">
                <form onSubmit={handleSearch}>
                    <input
                        type="text"
                        placeholder="Search leads..."
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />

                    <button type="submit">
                        Search
                    </button>
                </form>

                <select
                    value={status}
                    onChange={(event) =>
                        setStatus(event.target.value)
                    }
                >
                    <option value="">
                        All Statuses
                    </option>
                    <option value="NEW">New</option>
                    <option value="CONTACTED">
                        Contacted
                    </option>
                    <option value="QUALIFIED">
                        Qualified
                    </option>
                    <option value="CONVERTED">
                        Converted
                    </option>
                    <option value="LOST">Lost</option>
                </select>

                <select
                    value={source}
                    onChange={(event) =>
                        setSource(event.target.value)
                    }
                >
                    <option value="">
                        All Sources
                    </option>
                    <option value="WEBSITE">
                        Website
                    </option>
                    <option value="REFERRAL">
                        Referral
                    </option>
                    <option value="LINKEDIN">
                        LinkedIn
                    </option>
                    <option value="EMAIL">
                        Email
                    </option>
                    <option value="COLD_CALL">
                        Cold Call
                    </option>
                    <option value="OTHER">
                        Other
                    </option>
                </select>
            </div>

            {loading && <p>Loading leads...</p>}

            {error && <p>{error}</p>}

            {!loading && !error && (
                <>
                    {leads.length === 0 ? (
                        <p>No leads found.</p>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Company</th>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th>Source</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {leads.map((lead) => (
                                    <tr key={lead.id}>
                                        <td>{lead.name}</td>
                                        <td>{lead.company}</td>
                                        <td>{lead.email}</td>
                                        <td>{lead.status}</td>
                                        <td>{lead.source}</td>
                                        <td>
                                            <button
                                                onClick={() =>
                                                    openEditForm(lead)
                                                }
                                            >
                                                Edit
                                            </button>

                                            <button
                                                onClick={() =>
                                                    handleDelete(
                                                        lead.id
                                                    )
                                                }
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </>
            )}
        </div>
    );
}

export default Leads;