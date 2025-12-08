import { useState } from 'react';
import { searchBooks } from '../api';
import './SearchBooks.css';

function SearchBooks() {
  const [query, setQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const results = await searchBooks(query);
      setBooks(results);
      if (results.length === 0) {
        setError('No books found matching your search');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error searching books');
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
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

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
                  <td>{book.authors || 'N/A'}</td>
                  <td>{book.checked_out ? 'Yes' : 'No'}</td>
                  <td>{book.borrower_id || '-'}</td>
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



