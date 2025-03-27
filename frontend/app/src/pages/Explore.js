import React, { useState, useEffect } from "react";
import { Search } from "lucide-react";
import "./Explore.css"

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const SearchBar = () => {
    const [query, setQuery] = useState("");

    const handleSearch = (e) => {
        e.preventDefault();
        alert(`Searching for: ${query}`);
    };

    return (
        <div className="search-container">
            <form onSubmit={handleSearch} className="search-form">
                <Search className="search-icon" />
                <input
                    type="text"
                    placeholder="Search..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="search-input"
                />
            </form>
        </div>
    );
};

const DataComponent = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/articles/clusters?query=Python"`);
                if (!response.ok) throw new Error("Failed to fetch data");
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <p>Loading...</p>;

    if (error) return <p>Error: {error}</p>;

    return (
        <div>
            <h2>Fetched Data</h2>
            <ul>
                {JSON.stringify(data)}
            </ul>
        </div>
    );
};

const Explore = () => {
    console.log(API_BASE_URL);
    return (
        <>
            <h1>Explore articles</h1>
            <SearchBar />
            <DataComponent />
        </>
    );
};

export default Explore;
