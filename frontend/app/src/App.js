import './App.css';
import { Routes, Route } from "react-router-dom";
import Layout from "./pages/Layout";
import Home from "./pages/Home";
import Explore from "./pages/Explore";
import About from "./pages/About";
import NoPage from "./pages/NoPage";
import Visualize from "./pages/Visualize";

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<Home />} />
                <Route path="explore" element={<Explore />} />
                <Route path="about" element={<About />} />
                <Route path="visualize" element={<Visualize />} />
                <Route path="*" element={<NoPage />} />
            </Route>
        </Routes>
    );
}

export default App;
