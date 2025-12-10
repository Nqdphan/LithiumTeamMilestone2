import { useState } from "react";
import { searchBooks, checkoutBook } from "../api";
import "./SearchBooks.css";

function SearchBooks() {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Selection state
  const [selectedBooks, setSelectedBooks] = useState(new Set());

  // Modal state
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [cardNo, setCardNo] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState(null);
  const [checkoutResults, setCheckoutResults] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);
    setSelectedBooks(new Set()); // Clear selection on new search
    try {
      const results = await searchBooks(query);
      setBooks(results);
      // Empty result set is a valid, successful response - not an error
    } catch (err) {
      setError(err.response?.data?.detail || "Error searching books");
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle checkbox selection
  const handleBookSelect = (isbn) => {
    const newSelected = new Set(selectedBooks);
    if (newSelected.has(isbn)) {
      newSelected.delete(isbn);
    } else {
      newSelected.add(isbn);
    }
    setSelectedBooks(newSelected);
  };

  // Handle select all checkbox
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      // Only select books that are not already checked out
      const availableIsbns = new Set(
        books.filter((book) => !book.checked_out).map((book) => book.isbn)
      );
      setSelectedBooks(availableIsbns);
    } else {
      setSelectedBooks(new Set());
    }
  };

  // Validate Card_no format (ID######)
  const validateCardNo = (cardNo) => {
    const cardNoRegex = /^ID\d{6}$/;
    return cardNoRegex.test(cardNo);
  };

  // Open checkout modal
  const handleCheckoutClick = () => {
    if (selectedBooks.size === 0) return;
    setShowCheckoutModal(true);
    setCardNo("");
    setCheckoutError(null);
    setCheckoutResults(null);
  };

  // Close checkout modal
  const handleCloseModal = () => {
    setShowCheckoutModal(false);
    setCardNo("");
    setCheckoutError(null);
    setCheckoutResults(null);
  };

  // Handle checkout confirmation
  const handleCheckoutConfirm = async () => {
    if (!cardNo.trim()) {
      setCheckoutError("Card No is required");
      return;
    }

    const trimmedCardNo = cardNo.trim().toUpperCase();
    if (!validateCardNo(trimmedCardNo)) {
      setCheckoutError("Card No must be in format ID###### (e.g., ID000123)");
      return;
    }

    setCheckoutLoading(true);
    setCheckoutError(null);
    setCheckoutResults(null);

    const selectedIsbns = Array.from(selectedBooks);
    const results = {
      success: [],
      failed: [],
    };

    // Checkout each selected book
    for (const isbn of selectedIsbns) {
      try {
        const result = await checkoutBook(isbn, trimmedCardNo);
        results.success.push({ isbn, result });
      } catch (err) {
        const errorMessage =
          err.response?.data?.detail || "Error checking out book";
        results.failed.push({ isbn, error: errorMessage });
      }
    }

    setCheckoutLoading(false);
    setCheckoutResults(results);

    // Update books state for successfully checked out books
    if (results.success.length > 0) {
      const successfulIsbns = new Set(results.success.map(({ isbn }) => isbn));
      setBooks((prevBooks) =>
        prevBooks.map((book) =>
          successfulIsbns.has(book.isbn)
            ? {
                ...book,
                checked_out: true,
                borrower_id: trimmedCardNo,
              }
            : book
        )
      );

      // Remove successfully checked out books from selection
      setSelectedBooks((prevSelected) => {
        const newSelected = new Set(prevSelected);
        successfulIsbns.forEach((isbn) => newSelected.delete(isbn));
        return newSelected;
      });
    }

    // If all succeeded, close modal after a short delay to show success message
    if (results.failed.length === 0) {
      setTimeout(() => {
        handleCloseModal();
      }, 2000);
    }
  };

  return (
    <div className="search-books">
      <h1>Search Books</h1>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by ISBN, title, or author..."
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-button">
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {hasSearched && !loading && books.length === 0 && !error && (
        <div
          style={{
            padding: "20px",
            textAlign: "center",
            color: "#aaa",
            fontSize: "18px",
            marginTop: "20px",
          }}
        >
          No books found matching your search criteria.
        </div>
      )}

      {books.length > 0 && (
        <div className="books-table-container">
          <div className="checkout-actions">
            <button
              onClick={handleCheckoutClick}
              disabled={selectedBooks.size === 0}
              className="checkout-selected-button"
            >
              Check Out Selected ({selectedBooks.size})
            </button>
          </div>
          <table className="books-table">
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    checked={
                      books.filter((book) => !book.checked_out).length > 0 &&
                      selectedBooks.size ===
                        books.filter((book) => !book.checked_out).length
                    }
                    onChange={handleSelectAll}
                    aria-label="Select all available books"
                  />
                </th>
                <th>ISBN</th>
                <th>Title</th>
                <th>Authors</th>
                <th>Checked Out?</th>
                <th>Borrower ID</th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => {
                const isSelected = selectedBooks.has(book.isbn);
                const isCheckedOut = book.checked_out;
                return (
                  <tr
                    key={book.isbn}
                    className={isSelected ? "selected-row" : ""}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleBookSelect(book.isbn)}
                        disabled={isCheckedOut}
                        aria-label={`Select ${book.title}`}
                      />
                    </td>
                    <td>{book.isbn}</td>
                    <td>{book.title}</td>
                    <td>{book.authors || "N/A"}</td>
                    <td>{isCheckedOut ? "Yes" : "No"}</td>
                    <td>{book.borrower_id || "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Checkout Modal */}
      {showCheckoutModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Check Out Selected Books</h2>
              <button
                className="modal-close-button"
                onClick={handleCloseModal}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-info">
                Checking out {selectedBooks.size} book
                {selectedBooks.size !== 1 ? "s" : ""}
              </p>
              <div className="form-group">
                <label htmlFor="card-no-input">Borrower Card No *</label>
                <input
                  id="card-no-input"
                  type="text"
                  value={cardNo}
                  onChange={(e) => setCardNo(e.target.value.toUpperCase())}
                  placeholder="ID000123"
                  maxLength={8}
                  disabled={checkoutLoading}
                  className="card-no-input"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !checkoutLoading) {
                      handleCheckoutConfirm();
                    }
                  }}
                />
                <small className="input-hint">
                  Format: ID###### (e.g., ID000123)
                </small>
              </div>

              {checkoutError && (
                <div className="error-message">{checkoutError}</div>
              )}

              {checkoutResults && (
                <div className="checkout-results">
                  {checkoutResults.success.length > 0 && (
                    <div className="success-message">
                      <strong>Successfully checked out:</strong>
                      <ul>
                        {checkoutResults.success.map(({ isbn }) => (
                          <li key={isbn}>{isbn}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {checkoutResults.failed.length > 0 && (
                    <div className="error-message">
                      <strong>Failed to check out:</strong>
                      <ul>
                        {checkoutResults.failed.map(({ isbn, error }) => (
                          <li key={isbn}>
                            <strong>{isbn}:</strong> {error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button
                onClick={handleCloseModal}
                disabled={checkoutLoading}
                className="modal-button modal-button-cancel"
              >
                Cancel
              </button>
              <button
                onClick={handleCheckoutConfirm}
                disabled={checkoutLoading || !cardNo.trim()}
                className="modal-button modal-button-confirm"
              >
                {checkoutLoading ? "Processing..." : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchBooks;
