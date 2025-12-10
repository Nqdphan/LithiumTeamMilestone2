import { useState } from "react";
import { createBorrower } from "../api";
import "./Borrowers.css";

/**
 * Format SSN input to 123-45-6789 format
 * @param {string} value - Raw input value
 * @returns {string} - Formatted SSN
 */
function formatSSN(value) {
  // Remove all non-numeric characters
  const numbers = value.replace(/\D/g, "");

  // Limit to 9 digits
  const limited = numbers.slice(0, 9);

  // Apply formatting: XXX-XX-XXXX
  if (limited.length <= 3) {
    return limited;
  } else if (limited.length <= 5) {
    return `${limited.slice(0, 3)}-${limited.slice(3)}`;
  } else {
    return `${limited.slice(0, 3)}-${limited.slice(3, 5)}-${limited.slice(5)}`;
  }
}

/**
 * Format phone input to (555) 123-4567 format
 * @param {string} value - Raw input value
 * @returns {string} - Formatted phone number
 */
function formatPhone(value) {
  // Remove all non-numeric characters
  const numbers = value.replace(/\D/g, "");

  // Limit to 10 digits
  const limited = numbers.slice(0, 10);

  // Apply formatting: (XXX) XXX-XXXX
  if (limited.length === 0) {
    return "";
  } else if (limited.length <= 3) {
    return `(${limited}`;
  } else if (limited.length <= 6) {
    return `(${limited.slice(0, 3)}) ${limited.slice(3)}`;
  } else {
    return `(${limited.slice(0, 3)}) ${limited.slice(3, 6)}-${limited.slice(
      6
    )}`;
  }
}

function Borrowers() {
  const [formData, setFormData] = useState({
    ssn: "",
    name: "",
    address: "",
    phone: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    let formattedValue = value;

    // Apply formatting based on field type
    if (name === "ssn") {
      formattedValue = formatSSN(value);
    } else if (name === "phone") {
      formattedValue = formatPhone(value);
    }

    setFormData({
      ...formData,
      [name]: formattedValue,
    });
  };

  const handleKeyDown = (e) => {
    // Handle backspace/delete for formatted fields
    const { name, value, selectionStart } = e.target;

    if ((name === "ssn" || name === "phone") && e.key === "Backspace") {
      const cursorPos = selectionStart;
      const charBeforeCursor = value[cursorPos - 1];

      // If deleting a formatting character, delete the digit before it too
      if (
        charBeforeCursor === "-" ||
        charBeforeCursor === " " ||
        charBeforeCursor === "(" ||
        charBeforeCursor === ")"
      ) {
        e.preventDefault();
        const newValue = value.slice(0, cursorPos - 2) + value.slice(cursorPos);
        const formattedValue =
          name === "ssn" ? formatSSN(newValue) : formatPhone(newValue);

        setFormData({
          ...formData,
          [name]: formattedValue,
        });

        // Set cursor position after formatting
        setTimeout(() => {
          const input = e.target;
          const newCursorPos = Math.max(0, cursorPos - 2);
          input.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);
      }
    }
  };

  const handlePaste = (e) => {
    // Handle paste for formatted fields
    const { name } = e.target;

    if (name === "ssn" || name === "phone") {
      e.preventDefault();
      const pastedText = (e.clipboardData || window.clipboardData).getData(
        "text"
      );

      // Remove formatting and apply our formatting
      const cleaned = pastedText.replace(/\D/g, "");
      const formattedValue =
        name === "ssn" ? formatSSN(cleaned) : formatPhone(cleaned);

      setFormData({
        ...formData,
        [name]: formattedValue,
      });
    }
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
        ssn: "",
        name: "",
        address: "",
        phone: "",
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Error creating borrower");
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
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            required
            placeholder="123-45-6789"
            maxLength={11}
            inputMode="numeric"
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
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            required
            placeholder="(555) 123-4567"
            maxLength={14}
            inputMode="numeric"
          />
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? "Creating..." : "Create Borrower"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {message && <div className="success-message">{message}</div>}
    </div>
  );
}

export default Borrowers;
