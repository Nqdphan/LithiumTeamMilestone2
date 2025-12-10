import { useState, useEffect } from "react";
import { updateFines, getFinesSummary, payFines } from "../api";
import "./Fines.css";

function Fines() {
  const [fines, setFines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [paying, setPaying] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [unpaidOnly, setUnpaidOnly] = useState(true);
  const [cardIdFilter, setCardIdFilter] = useState("");
  const [nameFilter, setNameFilter] = useState("");

  const loadFines = async (overrideCardId = null, overrideName = null) => {
    setLoading(true);
    setError(null);
    try {
      const cardId =
        overrideCardId !== null ? overrideCardId : cardIdFilter.trim() || null;
      const name =
        overrideName !== null ? overrideName : nameFilter.trim() || null;
      const results = await getFinesSummary(unpaidOnly, cardId, name);
      setFines(results);
      if (results.length === 0) {
        setMessage("No fines found");
      } else {
        setMessage(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Error loading fines");
      setFines([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFines();
  }, [unpaidOnly]);

  const handleSearch = () => {
    loadFines();
  };

  const handleClearFilters = () => {
    setCardIdFilter("");
    setNameFilter("");
    loadFines("", "");
  };

  const handleUpdateFines = async () => {
    setUpdating(true);
    setError(null);
    setMessage(null);
    try {
      const result = await updateFines();
      setMessage(
        `Fines updated! Inserted: ${result.inserted}, Updated: ${result.updated}`
      );
      // Reload fines after update
      await loadFines();
    } catch (err) {
      setError(err.response?.data?.detail || "Error updating fines");
    } finally {
      setUpdating(false);
    }
  };

  const handlePayFines = async (cardId) => {
    if (!window.confirm(`Pay all fines for borrower ${cardId}?`)) {
      return;
    }

    setPaying(cardId);
    setError(null);
    setMessage(null);
    try {
      const result = await payFines(cardId);
      setMessage(
        `Successfully paid fines for borrower ${cardId}! Rows updated: ${result.rows_updated}`
      );
      // Reload fines after payment
      await loadFines();
    } catch (err) {
      setError(err.response?.data?.detail || "Error paying fines");
    } finally {
      setPaying(null);
    }
  };

  return (
    <div className="fines">
      <h1>Fines Management</h1>

      <div className="search-section">
        <div className="search-inputs">
          <div className="search-input-group">
            <label htmlFor="cardIdSearch">Borrower ID:</label>
            <input
              id="cardIdSearch"
              type="text"
              placeholder="Search by Borrower ID"
              value={cardIdFilter}
              onChange={(e) => setCardIdFilter(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
            />
          </div>
          <div className="search-input-group">
            <label htmlFor="nameSearch">Borrower Name:</label>
            <input
              id="nameSearch"
              type="text"
              placeholder="Search by Borrower Name"
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
            />
          </div>
          <div className="search-buttons">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="search-button"
            >
              {loading ? "Searching..." : "Search"}
            </button>
            <button
              onClick={handleClearFilters}
              disabled={loading}
              className="clear-button"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      <div className="fines-controls">
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={unpaidOnly}
              onChange={(e) => setUnpaidOnly(e.target.checked)}
            />
            Show unpaid fines only
          </label>
        </div>
        <button
          onClick={handleUpdateFines}
          disabled={updating}
          className="update-button"
        >
          {updating ? "Updating..." : "Refresh Fines"}
        </button>
        <button
          onClick={loadFines}
          disabled={loading}
          className="refresh-button"
        >
          {loading ? "Loading..." : "Refresh List"}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {message && <div className="success-message">{message}</div>}

      {fines.length > 0 && (
        <div className="fines-table-container">
          <table className="fines-table">
            <thead>
              <tr>
                <th>Card ID</th>
                <th>Borrower Name</th>
                <th>Total Fine Amount</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {fines.map((fine) => (
                <tr key={fine.card_id}>
                  <td>{fine.card_id}</td>
                  <td>{fine.borrower_name}</td>
                  <td>${fine.total_fine_amt.toFixed(2)}</td>
                  <td>
                    <button
                      onClick={() => handlePayFines(fine.card_id)}
                      disabled={paying === fine.card_id || unpaidOnly === false}
                      className="pay-button"
                    >
                      {paying === fine.card_id ? "Processing..." : "Pay All"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {fines.length === 0 && !loading && !error && (
        <div className="no-fines">No fines found</div>
      )}
    </div>
  );
}

export default Fines;
