import { Outlet, Link } from "react-router-dom";
import logo from '../logo.svg';
import "./Layout.css"

const Layout = () => {
    return (
        <>
            <nav>
                <ul>
                    <li>
                        <img src={logo} />
                    </li>
                    <li>
                        <Link to="/">Home</Link>
                    </li>
                    <li>
                        <Link to="/explore">Explore</Link>
                    </li>
                    <li>
                        <Link to="/about">About</Link>
                    </li>
                </ul>
            </nav>

            <Outlet />
        </>
    )
};

export default Layout;
