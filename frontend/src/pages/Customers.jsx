import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import { getAccessToken } from "../services/auth";
import "./Customers.css";

function Customers() {
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState("");

    const [showForm, setShowForm] = useState(false);
    const [editingCustomer, setEditingCustomer] = useState(null);

    const [formData, setFormData] = useState({
        name: "",
        company: "",
        email: "",
        phone: "",
        address: "",
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    async function loadCustomers() {
        try {
            setLoading(true);
            setError("");

            const params = new URLSearchParams();

            if (search) {
                params.append("search", search);
            }

            const query = params.toString();

            const data = await apiRequest(
                `/customers/${query ? `?${query}` : ""}`,
                {
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                }
            );

            setCustomers(data.results);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadCustomers();
    }, []);

    function handleSearch(event) {
        event.preventDefault();
        loadCustomers();
    }

    function handleInputChange(event) {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    function openCreateForm() {
        setEditingCustomer(null);

        setFormData({
            name: "",
            company: "",
            email: "",
            phone: "",
            address: "",
        });

        setFormError("");
        setShowForm(true);
    }

    function openEditForm(customer) {
        setEditingCustomer(customer);

        setFormData({
            name: customer.name,
            company: customer.company,
            email: customer.email,
            phone: customer.phone,
            address: customer.address || "",
        });

        setFormError("");
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingCustomer(null);
        setFormError("");
    }

    async function handleSubmit(event) {
        event.preventDefault();

        try {
            setFormError("");

            if (editingCustomer) {
                await apiRequest(
                    `/customers/${editingCustomer.id}/`,
                    {
                        method: "PATCH",
                        headers: {
                            Authorization: `Bearer ${getAccessToken()}`,
                        },
                        body: JSON.stringify(formData),
                    }
                );
            } else {
                await apiRequest("/customers/", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                    body: JSON.stringify(formData),
                });
            }

            closeForm();
            await loadCustomers();

        } catch (error) {
            setFormError(error.message);
        }
    }

    async function handleDelete(customer) {
        const confirmed = window.confirm(
            `Are you sure you want to delete ${customer.name}?`
        );

        if (!confirmed) {
            return;
        }

        try {
            setError("");

            await apiRequest(
                `/customers/${customer.id}/`,
                {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                }
            );

            await loadCustomers();

        } catch (error) {
            setError(error.message);
        }
    }

    return (
        <div className="customers-page">

            <div className="customers-header">
                <h1>Customers</h1>

                <button
                    className="add-customer-button"
                    onClick={
                        showForm
                            ? closeForm
                            : openCreateForm
                    }
                >
                    {showForm
                        ? "Close Form"
                        : "+ Add Customer"}
                </button>
            </div>

            {showForm && (
                <div className="customer-form-card">

                    <h2>
                        {editingCustomer
                            ? "Edit Customer"
                            : "Add New Customer"}
                    </h2>

                    {formError && (
                        <p className="form-error">
                            {formError}
                        </p>
                    )}

                    <form onSubmit={handleSubmit}>

                        <div className="customer-form-grid">

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

                        </div>

                        <textarea
                            name="address"
                            placeholder="Address"
                            value={formData.address}
                            onChange={handleInputChange}
                        />

                        <button
                            type="submit"
                            className="save-customer-button"
                        >
                            {editingCustomer
                                ? "Update Customer"
                                : "Save Customer"}
                        </button>

                    </form>
                </div>
            )}

            <div className="customer-search">

                <form onSubmit={handleSearch}>

                    <input
                        type="text"
                        placeholder="Search customers..."
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />

                    <button type="submit">
                        Search
                    </button>

                </form>

            </div>

            {loading && (
                <p>Loading customers...</p>
            )}

            {error && (
                <p className="form-error">
                    {error}
                </p>
            )}

            {!loading && !error && (
                <>
                    {customers.length === 0 ? (
                        <p>No customers found.</p>
                    ) : (
                        <table>

                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Company</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>

                                {customers.map((customer) => (
                                    <tr key={customer.id}>

                                        <td>
                                            {customer.name}
                                        </td>

                                        <td>
                                            {customer.company}
                                        </td>

                                        <td>
                                            {customer.email}
                                        </td>

                                        <td>
                                            {customer.phone}
                                        </td>

                                        <td className="customer-actions">

                                            <button
                                                className="edit-button"
                                                onClick={() =>
                                                    openEditForm(customer)
                                                }
                                            >
                                                Edit
                                            </button>

                                            <button
                                                className="delete-button"
                                                onClick={() =>
                                                    handleDelete(customer)
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

export default Customers;