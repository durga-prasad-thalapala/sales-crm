
import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";
import { getAccessToken } from "../services/auth";
import "./Activities.css";

const EMPTY_FORM = {
    deal: "",
    type: "TASK",
    title: "",
    description: "",
    due_date: "",
    completed: false,
};

function Activities() {
    const [activities, setActivities] = useState([]);
    const [deals, setDeals] = useState([]);
    const [search, setSearch] = useState("");
    const [type, setType] = useState("");
    const [completed, setCompleted] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editingActivity, setEditingActivity] = useState(null);
    const [formData, setFormData] = useState(EMPTY_FORM);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    async function loadDeals() {
        try {
            const data = await apiRequest("/deals/", {
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
            });
            setDeals(data.results || []);
        } catch (err) {
            setError(`Unable to load deals: ${err.message}`);
        }
    }

    async function loadActivities() {
        try {
            setLoading(true);
            setError("");

            const params = new URLSearchParams();
            if (search.trim()) params.append("search", search.trim());
            if (type) params.append("type", type);
            if (completed !== "") params.append("completed", completed);

            const query = params.toString();
            const data = await apiRequest(
                `/activities/${query ? `?${query}` : ""}`,
                {
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                }
            );

            setActivities(data.results || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadDeals();
        loadActivities();
    }, []);

    function handleInputChange(event) {
        const { name, value, type: inputType, checked } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: inputType === "checkbox" ? checked : value,
        }));
    }

    function openCreateForm() {
        setEditingActivity(null);
        setFormData(EMPTY_FORM);
        setFormError("");
        setShowForm(true);
    }

    function openEditForm(activity) {
        setEditingActivity(activity);
        setFormData({
            deal: String(activity.deal),
            type: activity.type,
            title: activity.title,
            description: activity.description || "",
            due_date: activity.due_date
                ? activity.due_date.slice(0, 16)
                : "",
            completed: activity.completed,
        });
        setFormError("");
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingActivity(null);
        setFormError("");
    }

    async function handleSubmit(event) {
        event.preventDefault();

        try {
            setFormError("");

            const payload = {
                ...formData,
                deal: Number(formData.deal),
                due_date: formData.due_date
                    ? new Date(formData.due_date).toISOString()
                    : null,
            };

            const endpoint = editingActivity
                ? `/activities/${editingActivity.id}/`
                : "/activities/";

            await apiRequest(endpoint, {
                method: editingActivity ? "PATCH" : "POST",
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
                body: JSON.stringify(payload),
            });

            closeForm();
            await loadActivities();
        } catch (err) {
            setFormError(err.message);
        }
    }

    async function toggleCompleted(activity) {
        try {
            await apiRequest(`/activities/${activity.id}/`, {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
                body: JSON.stringify({
                    completed: !activity.completed,
                }),
            });

            await loadActivities();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleDelete(activityId) {
        if (!window.confirm("Are you sure you want to delete this activity?")) {
            return;
        }

        try {
            await apiRequest(`/activities/${activityId}/`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${getAccessToken()}`,
                },
            });

            await loadActivities();
        } catch (err) {
            setError(err.message);
        }
    }

    function handleSearch(event) {
        event.preventDefault();
        loadActivities();
    }

    function getDealTitle(dealId) {
        const deal = deals.find((item) => item.id === dealId);
        return deal ? deal.title : `Deal #${dealId}`;
    }

    return (
        <div className="activities-page">
            <div className="activities-header">
                <h1>Activities</h1>
                <button
                    className="add-activity-button"
                    onClick={showForm ? closeForm : openCreateForm}
                >
                    {showForm ? "Close Form" : "+ Add Activity"}
                </button>
            </div>

            {showForm && (
                <div className="activity-form-card">
                    <h2>
                        {editingActivity ? "Edit Activity" : "Add New Activity"}
                    </h2>

                    {formError && <p className="form-error">{formError}</p>}

                    <form onSubmit={handleSubmit}>
                        <div className="activity-form-grid">
                            <select
                                name="deal"
                                value={formData.deal}
                                onChange={handleInputChange}
                                required
                            >
                                <option value="">Select Deal</option>
                                {deals.map((deal) => (
                                    <option key={deal.id} value={deal.id}>
                                        {deal.title}
                                    </option>
                                ))}
                            </select>

                            <select
                                name="type"
                                value={formData.type}
                                onChange={handleInputChange}
                                required
                            >
                                <option value="CALL">Call</option>
                                <option value="EMAIL">Email</option>
                                <option value="MEETING">Meeting</option>
                                <option value="NOTE">Note</option>
                                <option value="FOLLOW_UP">Follow-up</option>
                                <option value="TASK">Task</option>
                            </select>

                            <input
                                name="title"
                                placeholder="Activity title"
                                value={formData.title}
                                onChange={handleInputChange}
                                required
                            />

                            <input
                                name="due_date"
                                type="datetime-local"
                                value={formData.due_date}
                                onChange={handleInputChange}
                            />
                        </div>

                        <textarea
                            name="description"
                            placeholder="Description"
                            value={formData.description}
                            onChange={handleInputChange}
                        />

                        <label className="activity-completed-field">
                            <input
                                type="checkbox"
                                name="completed"
                                checked={formData.completed}
                                onChange={handleInputChange}
                            />
                            Completed
                        </label>

                        <button type="submit" className="save-activity-button">
                            {editingActivity ? "Update Activity" : "Save Activity"}
                        </button>
                    </form>
                </div>
            )}

            <div className="activity-filters">
                <form onSubmit={handleSearch}>
                    <input
                        placeholder="Search activities..."
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />
                    <button type="submit">Search</button>
                </form>

                <select
                    value={type}
                    onChange={(event) => setType(event.target.value)}
                >
                    <option value="">All Types</option>
                    <option value="CALL">Call</option>
                    <option value="EMAIL">Email</option>
                    <option value="MEETING">Meeting</option>
                    <option value="NOTE">Note</option>
                    <option value="FOLLOW_UP">Follow-up</option>
                    <option value="TASK">Task</option>
                </select>

                <select
                    value={completed}
                    onChange={(event) => setCompleted(event.target.value)}
                >
                    <option value="">All Statuses</option>
                    <option value="false">Pending</option>
                    <option value="true">Completed</option>
                </select>

                <button type="button" onClick={loadActivities}>
                    Apply Filters
                </button>
            </div>

            {loading && <p>Loading activities...</p>}
            {error && <p className="form-error">{error}</p>}

            {!loading && !error && (
                activities.length === 0 ? (
                    <p>No activities found.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Deal</th>
                                <th>Type</th>
                                <th>Due Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {activities.map((activity) => (
                                <tr key={activity.id}>
                                    <td>{activity.title}</td>
                                    <td>{getDealTitle(activity.deal)}</td>
                                    <td>{activity.type}</td>
                                    <td>
                                        {activity.due_date
                                            ? new Date(activity.due_date).toLocaleString()
                                            : "—"}
                                    </td>
                                    <td>
                                        {activity.completed ? "Completed" : "Pending"}
                                    </td>
                                    <td>
                                        <button
                                            onClick={() => toggleCompleted(activity)}
                                        >
                                            {activity.completed
                                                ? "Mark Pending"
                                                : "Complete"}
                                        </button>
                                        <button
                                            onClick={() => openEditForm(activity)}
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDelete(activity.id)}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )
            )}
        </div>
    );
}

export default Activities;
