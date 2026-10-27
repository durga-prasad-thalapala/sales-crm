
import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import { getAccessToken } from "../services/auth";
import "./Deals.css";

function Deals() {
    const [deals, setDeals] = useState([]);
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState("");
    const [stage, setStage] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editingDeal, setEditingDeal] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    const emptyForm = {
        customer: "",
        title: "",
        description: "",
        amount: "",
        stage: "NEW",
        expected_close_date: "",
    };

    const [formData, setFormData] = useState(emptyForm);

    async function loadCustomers() {
        try {
            const data = await apiRequest("/customers/", {
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
            });

            setCustomers(data.results || data);
        } catch (error) {
            setError(`Unable to load customers: ${error.message}`);
        }
    }

    async function loadDeals() {
        try {
            setLoading(true);
            setError("");

            const params = new URLSearchParams();
            if (search) params.append("search", search);
            if (stage) params.append("stage", stage);

            const query = params.toString();
            const data = await apiRequest(
                `/deals/${query ? `?${query}` : ""}`,
                {
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                }
            );

            setDeals(data.results || []);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadCustomers();
        loadDeals();
    }, [stage]);

    function handleInputChange(event) {
        const { name, value } = event.target;
        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    function openCreateForm() {
        setEditingDeal(null);
        setFormData(emptyForm);
        setFormError("");
        setShowForm(true);
    }

    function openEditForm(deal) {
        setEditingDeal(deal);
        setFormData({
            customer: String(deal.customer),
            title: deal.title,
            description: deal.description || "",
            amount: deal.amount,
            stage: deal.stage,
            expected_close_date: deal.expected_close_date || "",
        });
        setFormError("");
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingDeal(null);
        setFormError("");
    }

    async function handleSubmit(event) {
        event.preventDefault();

        try {
            setFormError("");

            const payload = {
                ...formData,
                customer: Number(formData.customer),
                amount: Number(formData.amount),
                expected_close_date: formData.expected_close_date || null,
            };

            if (editingDeal) {
                await apiRequest(`/deals/${editingDeal.id}/`, {
                    method: "PATCH",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                    body: JSON.stringify(payload),
                });
            } else {
                await apiRequest("/deals/", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                    body: JSON.stringify(payload),
                });
            }

            closeForm();
            await loadDeals();
        } catch (error) {
            setFormError(error.message);
        }
    }

    async function handleDelete(dealId) {
        if (!window.confirm("Are you sure you want to delete this deal?")) {
            return;
        }

        try {
            await apiRequest(`/deals/${dealId}/`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
            });

            await loadDeals();
        } catch (error) {
            setError(error.message);
        }
    }

    function handleSearch(event) {
        event.preventDefault();
        loadDeals();
    }

    return (
        <div className="deals-page">
            <div className="deals-header">
                <h1>Deals</h1>
                <button
                    className="add-deal-button"
                    onClick={showForm ? closeForm : openCreateForm}
                >
                    {showForm ? "Close Form" : "+ Add Deal"}
                </button>
            </div>

            {showForm && (
                <div className="deal-form-card">
                    <h2>{editingDeal ? "Edit Deal" : "Add New Deal"}</h2>

                    {formError && <p className="form-error">{formError}</p>}

                    <form onSubmit={handleSubmit}>
                        <div className="deal-form-grid">
                            <select
                                name="customer"
                                value={formData.customer}
                                onChange={handleInputChange}
                                required
                            >
                                <option value="">Select Customer</option>
                                {customers.map((customer) => (
                                    <option key={customer.id} value={customer.id}>
                                        {customer.name}
                                    </option>
                                ))}
                            </select>

                            <input
                                name="title"
                                placeholder="Deal title"
                                value={formData.title}
                                onChange={handleInputChange}
                                required
                            />

                            <input
                                name="amount"
                                type="number"
                                min="0"
                                step="0.01"
                                placeholder="Amount"
                                value={formData.amount}
                                onChange={handleInputChange}
                                required
                            />

                            <select
                                name="stage"
                                value={formData.stage}
                                onChange={handleInputChange}
                            >
                                <option value="NEW">New</option>
                                <option value="CONTACTED">Contacted</option>
                                <option value="QUALIFIED">Qualified</option>
                                <option value="PROPOSAL">Proposal</option>
                                <option value="NEGOTIATION">Negotiation</option>
                                <option value="WON">Won</option>
                                <option value="LOST">Lost</option>
                            </select>

                            <input
                                name="expected_close_date"
                                type="date"
                                value={formData.expected_close_date}
                                onChange={handleInputChange}
                            />
                        </div>

                        <textarea
                            name="description"
                            placeholder="Description"
                            value={formData.description}
                            onChange={handleInputChange}
                        />

                        <button type="submit" className="save-deal-button">
                            {editingDeal ? "Update Deal" : "Save Deal"}
                        </button>
                    </form>
                </div>
            )}

            <div className="deal-filters">
                <form onSubmit={handleSearch}>
                    <input
                        placeholder="Search deals..."
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />
                    <button type="submit">Search</button>
                </form>

                <select
                    value={stage}
                    onChange={(event) => setStage(event.target.value)}
                >
                    <option value="">All Stages</option>
                    <option value="NEW">New</option>
                    <option value="CONTACTED">Contacted</option>
                    <option value="QUALIFIED">Qualified</option>
                    <option value="PROPOSAL">Proposal</option>
                    <option value="NEGOTIATION">Negotiation</option>
                    <option value="WON">Won</option>
                    <option value="LOST">Lost</option>
                </select>
            </div>

            {loading && <p>Loading deals...</p>}
            {error && <p className="form-error">{error}</p>}

            {!loading && !error && (
                deals.length === 0 ? (
                    <p>No deals found.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Customer</th>
                                <th>Amount</th>
                                <th>Stage</th>
                                <th>Expected Close</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {deals.map((deal) => {
                                const customer = customers.find(
                                    (item) => item.id === deal.customer
                                );

                                return (
                                    <tr key={deal.id}>
                                        <td>{deal.title}</td>
                                        <td>{customer?.name || `Customer #${deal.customer}`}</td>
                                        <td>₹{deal.amount}</td>
                                        <td>{deal.stage}</td>
                                        <td>{deal.expected_close_date || "—"}</td>
                                        <td>
                                            <button onClick={() => openEditForm(deal)}>
                                                Edit
                                            </button>
                                            <button onClick={() => handleDelete(deal.id)}>
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )
            )}
        </div>
    );
}

export default Deals;
