import { useState } from "react";
import { searchBooks } from "../api";
import "./SearchBooks.css";

function SearchBooks() {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);
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
          <table className="books-table">
            <thead>
              <tr>
                <th>ISBN</th>
                <th>Title</th>
                <th>Authors</th>
                <th>Checked Out?</th>
                <th>Borrower ID</th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => (
                <tr key={book.isbn}>
                  <td>{book.isbn}</td>
                  <td>{book.title}</td>
                  <td>{book.authors || "N/A"}</td>
                  <td>{book.checked_out ? "Yes" : "No"}</td>
                  <td>{book.borrower_id || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default SearchBooks;
