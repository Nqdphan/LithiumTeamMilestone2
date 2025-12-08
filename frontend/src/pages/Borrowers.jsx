import { useState } from 'react';
import { createBorrower } from '../api';
import './Borrowers.css';

function Borrowers() {
  const [formData, setFormData] = useState({
    ssn: '',
    name: '',
    address: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const result = await createBorrower(formData);
      setMessage(`Borrower created successfully! Card ID: ${result.card_id}`);
      setFormData({
        ssn: '',
        name: '',
        address: '',
        phone: '',
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating borrower');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="borrowers">
      <h1>Add Borrower</h1>

      <form onSubmit={handleSubmit} className="borrower-form">
        <div className="form-group">
          <label htmlFor="ssn">SSN *</label>
          <input
            type="text"
            id="ssn"
            name="ssn"
            value={formData.ssn}
            onChange={handleChange}
            required
            placeholder="123-45-6789"
          />
        </div>

        <div className="form-group">
          <label htmlFor="name">Full Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="John Doe"
          />
        </div>

        <div className="form-group">
          <label htmlFor="address">Address *</label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            required
            placeholder="123 Main St, City, State"
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone *</label>
          <input
            type="text"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            required
            placeholder="(555) 123-4567"
          />
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Creating...' : 'Create Borrower'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {message && <div className="success-message">{message}</div>}
    </div>
  );
}

export default Borrowers;



