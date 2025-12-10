import { useState } from "react";
import { checkoutBook, getOpenLoans, checkinBook } from "../api";
import "./Loans.css";

function Loans() {
  const [activeTab, setActiveTab] = useState("checkout");

  // Checkout state
  const [checkoutIsbn, setCheckoutIsbn] = useState("");
  const [checkoutCardId, setCheckoutCardId] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutMessage, setCheckoutMessage] = useState(null);
  const [checkoutError, setCheckoutError] = useState(null);

  // Checkin state
  const [openLoans, setOpenLoans] = useState([]);
  const [loanFilters, setLoanFilters] = useState({
    isbn: "",
    card_id: "",
    name_query: "",
  });
  const [loansLoading, setLoansLoading] = useState(false);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [checkinMessage, setCheckinMessage] = useState(null);
  const [checkinError, setCheckinError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleCheckout = async (e) => {
    e.preventDefault();
    setCheckoutLoading(true);
    setCheckoutError(null);
    setCheckoutMessage(null);

    try {
      const result = await checkoutBook(checkoutIsbn, checkoutCardId);
      setCheckoutMessage(
        `Book checked out successfully! Loan ID: ${result.loan_id}, Due Date: ${result.due_date}`
      );
      setCheckoutIsbn("");
      setCheckoutCardId("");
    } catch (err) {
      setCheckoutError(err.response?.data?.detail || "Error checking out book");
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleSearchLoans = async () => {
    setLoansLoading(true);
    setCheckinError(null);
    setHasSearched(true);
    try {
      const filters = {};
      if (loanFilters.isbn) filters.isbn = loanFilters.isbn;
      if (loanFilters.card_id) filters.card_id = loanFilters.card_id;
      if (loanFilters.name_query) filters.name_query = loanFilters.name_query;

      const results = await getOpenLoans(filters);
      setOpenLoans(results);
      // Empty result set is a valid, successful response - not an error
    } catch (err) {
      setCheckinError(err.response?.data?.detail || "Error fetching loans");
      setOpenLoans([]);
    } finally {
      setLoansLoading(false);
    }
  };

  const handleCheckin = async (loanId) => {
    if (!window.confirm(`Are you sure you want to check in loan ${loanId}?`)) {
      return;
    }

    setCheckinLoading(true);
    setCheckinError(null);
    setCheckinMessage(null);

    try {
      const result = await checkinBook(loanId);
      setCheckinMessage(
        `Book checked in successfully! Loan ID: ${result.loan_id}`
      );
      // Refresh the loans list
      handleSearchLoans();
    } catch (err) {
      setCheckinError(err.response?.data?.detail || "Error checking in book");
    } finally {
      setCheckinLoading(false);
    }
  };

  return (
    <div className="loans">
      <h1>Loans Management</h1>

      <div className="tabs">
        <button
          className={activeTab === "checkout" ? "active" : ""}
          onClick={() => setActiveTab("checkout")}
        >
          Checkout Book
        </button>
        <button
          className={activeTab === "checkin" ? "active" : ""}
          onClick={() => setActiveTab("checkin")}
        >
          Check-in Book
        </button>
      </div>

      {activeTab === "checkout" && (
        <div className="checkout-section">
          <h2>Checkout Book</h2>
          <form onSubmit={handleCheckout} className="checkout-form">
            <div className="form-group">
              <label htmlFor="checkout-isbn">ISBN *</label>
              <input
                type="text"
                id="checkout-isbn"
                value={checkoutIsbn}
                onChange={(e) => setCheckoutIsbn(e.target.value)}
                required
                placeholder="Enter ISBN"
              />
            </div>
            <div className="form-group">
              <label htmlFor="checkout-card-id">Borrower Card ID *</label>
              <input
                type="text"
                id="checkout-card-id"
                value={checkoutCardId}
                onChange={(e) => setCheckoutCardId(e.target.value)}
                required
                placeholder="Enter Card ID"
              />
            </div>
            <button
              type="submit"
              disabled={checkoutLoading}
              className="submit-button"
            >
              {checkoutLoading ? "Processing..." : "Checkout"}
            </button>
          </form>
          {checkoutError && (
            <div className="error-message">{checkoutError}</div>
          )}
          {checkoutMessage && (
            <div className="success-message">{checkoutMessage}</div>
          )}
        </div>
      )}

      {activeTab === "checkin" && (
        <div className="checkin-section">
          <h2>Check-in Book</h2>

          <div className="loan-filters">
            <div className="form-group">
              <label htmlFor="filter-isbn">Filter by ISBN</label>
              <input
                type="text"
                id="filter-isbn"
                value={loanFilters.isbn}
                onChange={(e) =>
                  setLoanFilters({ ...loanFilters, isbn: e.target.value })
                }
                placeholder="ISBN"
              />
            </div>
            <div className="form-group">
              <label htmlFor="filter-card-id">Filter by Card ID</label>
              <input
                type="text"
                id="filter-card-id"
                value={loanFilters.card_id}
                onChange={(e) =>
                  setLoanFilters({ ...loanFilters, card_id: e.target.value })
                }
                placeholder="Card ID"
              />
            </div>
            <div className="form-group">
              <label htmlFor="filter-name">Filter by Borrower Name</label>
              <input
                type="text"
                id="filter-name"
                value={loanFilters.name_query}
                onChange={(e) =>
                  setLoanFilters({ ...loanFilters, name_query: e.target.value })
                }
                placeholder="Borrower name"
              />
            </div>
            <button
              type="button"
              onClick={handleSearchLoans}
              disabled={loansLoading}
              className="search-button"
            >
              {loansLoading ? "Searching..." : "Search Loans"}
            </button>
          </div>

          {checkinError && <div className="error-message">{checkinError}</div>}
          {checkinMessage && (
            <div className="success-message">{checkinMessage}</div>
          )}
          {hasSearched &&
            !loansLoading &&
            openLoans.length === 0 &&
            !checkinError && (
              <div
                style={{
                  padding: "20px",
                  textAlign: "center",
                  color: "#aaa",
                  fontSize: "18px",
                  marginTop: "20px",
                }}
              >
                No open loans found matching your search criteria.
              </div>
            )}

          {openLoans.length > 0 && (
            <div className="loans-table-container">
              <table className="loans-table">
                <thead>
                  <tr>
                    <th>Loan ID</th>
                    <th>ISBN</th>
                    <th>Title</th>
                    <th>Card ID</th>
                    <th>Borrower Name</th>
                    <th>Date Out</th>
                    <th>Due Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {openLoans.map((loan) => (
                    <tr key={loan.loan_id}>
                      <td>{loan.loan_id}</td>
                      <td>{loan.isbn}</td>
                      <td>{loan.title}</td>
                      <td>{loan.card_id}</td>
                      <td>{loan.borrower_name}</td>
                      <td>{loan.date_out}</td>
                      <td>{loan.due_date}</td>
                      <td>
                        <button
                          onClick={() => handleCheckin(loan.loan_id)}
                          disabled={checkinLoading}
                          className="checkin-button"
                        >
                          Check In
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Loans;
