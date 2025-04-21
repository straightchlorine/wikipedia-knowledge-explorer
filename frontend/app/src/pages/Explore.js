import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { Search } from "lucide-react";
import "./Explore.css"
import LoadingDots from "../common/LoadingDots"
import ErrorTag from "../common/ErrorTag"

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const SearchBar = () => {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState(null);

    const handleSearch = (e) => {
        e.preventDefault();
        setSubmittedQuery(query);
    };

    return (
        <div>
            <div className="search-container">
                <form onSubmit={handleSearch} className="search-form" onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        handleSearch(e);
                    }
                }}
                >
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
            {submittedQuery != null && <DataComponent query={submittedQuery} />}
        </div>
    );
};

const DataComponent = ({ query }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleRedirect = () => {
        navigate(`/visualize?query=${query}`);
    };


    useEffect(() => {
        const fetchData = async () => {
            console.log(`Fetching ${API_BASE_URL}/articles/clusters?query=${query}"`);
            try {
                const response = await fetch(`${API_BASE_URL}/articles/?query=${encodeURIComponent(query)}"`);
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
    }, [query]);

    if (loading) return <LoadingDots />;
    if (error) return <ErrorTag error={error} />;

    return (
        <div>
            <h2>Results</h2>
            <h3 onClick={handleRedirect}>Visualize</h3>
            <div className="result-list">
                {data.articles.map((item, index) => <div key={index}><p>{item}</p></div>)}
            </div>
        </div>
    );
};

const Explore = () => {
    return (
        <>
            <h1>Explore articles</h1>
            <SearchBar />
        </>
    );
};

export default Explore;
