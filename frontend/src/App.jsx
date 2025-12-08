import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import SearchBooks from "./pages/SearchBooks";
import Borrowers from "./pages/Borrowers";
import Loans from "./pages/Loans";
import Fines from "./pages/Fines";
import "./App.css";

function Navigation() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? "active" : "";
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <h1 className="nav-title">Library Management System</h1>
        <ul className="nav-links">
          <li>
            <Link to="/" className={isActive("/")}>
              Search Books
            </Link>
          </li>
          <li>
            <Link to="/borrowers" className={isActive("/borrowers")}>
              Borrowers
            </Link>
          </li>
          <li>
            <Link to="/loans" className={isActive("/loans")}>
              Loans
            </Link>
          </li>
          <li>
            <Link to="/fines" className={isActive("/fines")}>
              Fines
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<SearchBooks />} />
            <Route path="/borrowers" element={<Borrowers />} />
            <Route path="/loans" element={<Loans />} />
            <Route path="/fines" element={<Fines />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
