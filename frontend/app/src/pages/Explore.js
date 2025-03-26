import { useState } from "react";
import { Search } from "lucide-react";
import "./Explore.css"

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

const Explore = () => {

    return (
        <>
            <h1>Explore articles</h1>
            <SearchBar />
        </>
    );
};

export default Explore;
