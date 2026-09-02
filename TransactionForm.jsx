import React, { useState } from "react";
import {
  FIELD_GROUPS,
  EMPTY_TRANSACTION,
} from "./frontend_field_config.js";

function TransactionForm({ onSubmit, submitting }) {
  const [form, setForm] = useState(EMPTY_TRANSACTION);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    const payload = {
      ...form,
      Age: Number(form.Age),
      Transaction_Amount: Number(form.Transaction_Amount),
      Account_Balance: Number(form.Account_Balance),
    };

    onSubmit(payload);
  }

  function renderField(field) {
    const value = form[field.name] ?? "";

    return (
      <div className="field" key={field.name}>
        <label htmlFor={field.name}>
          {field.label}

          {field.required && (
            <span className="required">*</span>
          )}
        </label>

        {field.type === "select" ? (
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={handleChange}
          >
            {field.options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        ) : (
          <input
            id={field.name}
            name={field.name}
            type={field.type || "text"}
            value={value}
            onChange={handleChange}
            placeholder={field.placeholder || ""}
            step={
              field.type === "number"
                ? "any"
                : undefined
            }
          />
        )}
      </div>
    );
  }

  return (
    <form
      className="transaction-form"
      onSubmit={handleSubmit}
    >
      {FIELD_GROUPS.map((group, index) => (
        <div className="form-section" key={group.title}>
          <div className="form-section-header">
            <span className="form-number">
              {String(index + 1).padStart(2, "0")}
            </span>

            <div>
              <h3>{group.title}</h3>

              {group.description && (
                <p>{group.description}</p>
              )}
            </div>
          </div>

          <div className="form-grid">
            {group.fields.map(renderField)}
          </div>
        </div>
      ))}

      <button
        type="submit"
        className="analyze-button"
        disabled={submitting}
      >
        <span>
          {submitting
            ? "ANALYZING TRANSACTION..."
            : "RUN INTELLIGENCE ANALYSIS"}
        </span>

        <span className="button-arrow">
          →
        </span>
      </button>

      <div className="form-note">
        <span>◆</span>
        Analysis uses the configured predictive model
        and historical transaction-location intelligence.
      </div>
    </form>
  );
}

export default TransactionForm;