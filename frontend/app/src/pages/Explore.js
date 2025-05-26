import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { Search } from "lucide-react";
import "./Explore.css"
import LoadingDots from "../common/LoadingDots"
import ErrorTag from "../common/ErrorTag"

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const SearchBar = () => {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState(null);
    const [settings, setSettings] = useState({ resultCount: 5 });


    const handleSearch = (e) => {
        e.preventDefault();
        setSubmittedQuery(query);
    };
    return (
        <div className="search-bar-container">
            <AdditionalSearchSettings
                settings={settings}
                setSettings={setSettings}
            />
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
            {submittedQuery != null && <DataComponent query={submittedQuery} settings={settings} />}
        </div>
    );
};

export const AdditionalSearchSettings = ({ settings, setSettings }) => {
    return (
        <div className="settings">
            <h4>Settings</h4>
            <div className="settings-group">
                <label>Result count: </label>
                <input
                    type="number"
                    value={settings.resultCount}
                    onChange={(e) => {
                        const newValue = Number(e.target.value);
                        setSettings(prev => ({
                            ...prev,
                            resultCount: newValue
                        }));
                    }}
                />
            </div>
        </div>
    );
};

export const Article = ({ index, title, open }) => {
    return (
        <div key={index}>
            <p>{title}</p>
            <p className="button-summary arrow" onClick={open}>Summary</p>
        </div>
    );
};

export const PopUp = ({ closePopup }) => {

    return (
        <div className="popup-overlay" onClick={closePopup}>
            <div className="popup-content" onClick={(e) => e.stopPropagation()}>
                <h3>This is a popup!</h3>
                <p>You can add anything here — text, forms, etc.</p>
                <div className="x-button" onClick={closePopup}>X</div>
            </div>
        </div>
    )
};

export const DataComponent = ({ query, settings }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showPopup, setShowPopup] = useState(false);
    const openPopup = () => setShowPopup(true);
    const closePopup = () => setShowPopup(false);

    const navigate = useNavigate();
    const handleRedirect = () => {
        navigate(`/visualize?query=${query}&max_results=${settings.resultCount}`);
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/articles/?query=${encodeURIComponent(query)}&max_results=${settings.resultCount}`);
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
    }, [query, settings]);

    if (loading) return <LoadingDots />;
    if (error) return <ErrorTag error={error} />;

    return (
        <>
            <div className="result-list-title">
                <h2>Found articles</h2>
                <div className="button-div node-style" onClick={handleRedirect}>Visualize</div>
            </div>
            <div className="result-list">
                {data.articles.map((item, index) => <Article index={index} title={item} open={openPopup} />)}
            </div>
            {showPopup && <PopUp closePopup={closePopup} />}
        </>
    );
};

const Explore = () => {
    return (
        <>
            <SearchBar />
        </>
    );
};

export default Explore;
