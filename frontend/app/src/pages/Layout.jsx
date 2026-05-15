import { useState } from "react";
import { Outlet, NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";
import logo from "../assets/logo.svg";
import ErrorBoundary from "../common/ErrorBoundary";

const navLinks = [
    { to: "/", label: "Home" },
    { to: "/explore", label: "Explore" },
    { to: "/about", label: "About" },
];

const linkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors ${
        isActive
            ? "text-accent-purple border-b-2 border-accent-purple pb-0.5"
            : "text-text-secondary hover:text-text-primary"
    }`;

const Layout = () => {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <>
            <a className="skip-link" href="#main">
                Skip to content
            </a>
            <nav
                className="sticky top-0 z-50 flex h-14 items-center justify-between border-b border-surface-600/50 bg-surface-800 px-4 md:px-8"
                aria-label="Primary"
            >
                <NavLink to="/" className="shrink-0" aria-label="Wikipedia Knowledge Explorer home">
                    <img src={logo} alt="" className="h-8" />
                </NavLink>

                {/* Desktop links */}
                <ul className="hidden md:flex items-center gap-6">
                    {navLinks.map(({ to, label }) => (
                        <li key={to}>
                            <NavLink to={to} end={to === "/"} className={linkClass}>
                                {label}
                            </NavLink>
                        </li>
                    ))}
                </ul>

                {/* Mobile hamburger */}
                <button
                    className="md:hidden text-text-secondary hover:text-text-primary"
                    onClick={() => setMenuOpen((prev) => !prev)}
                    aria-label={menuOpen ? "Close menu" : "Open menu"}
                    aria-expanded={menuOpen}
                    aria-controls="mobile-nav"
                >
                    {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
            </nav>

            {/* Mobile dropdown */}
            {menuOpen && (
                <div
                    id="mobile-nav"
                    className="md:hidden border-b border-surface-600/50 bg-surface-800 px-4 pb-3"
                >
                    <ul className="flex flex-col gap-2">
                        {navLinks.map(({ to, label }) => (
                            <li key={to}>
                                <NavLink
                                    to={to}
                                    end={to === "/"}
                                    className={linkClass}
                                    onClick={() => setMenuOpen(false)}
                                >
                                    {label}
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <main
                id="main"
                tabIndex={-1}
                className="mx-auto w-full max-w-6xl px-4 py-8 md:px-8 focus:outline-none"
            >
                <ErrorBoundary>
                    <Outlet />
                </ErrorBoundary>
            </main>
        </>
    );
};

export default Layout;
