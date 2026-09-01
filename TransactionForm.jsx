import { useState } from "react";

import {
  FIELD_GROUPS,
  EMPTY_TRANSACTION,
} from "./frontend_field_config.js";

function Field({ field, value, onChange }) {
  const base =
    "w-full rounded-lg border border-panelLine bg-ink px-3 py-2.5 text-sm text-paper outline-none transition placeholder:text-muted/50 focus:border-signal focus:ring-1 focus:ring-signal/30";

  if (field.type === "select") {
    return (
      <select
        className={base}
        value={value}
        onChange={(e) => onChange(field.name, e.target.value)}
        required
      >
        <option value="" disabled>
          Select…
        </option>

        {field.options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    );
  }

  return (
    <input
      className={base}
      type={field.type === "date-dmy" ? "text" : field.type}
      step={field.step}
      placeholder={field.placeholder}
      value={value}
      onChange={(e) => onChange(field.name, e.target.value)}
      required
    />
  );
}

export default function TransactionForm({ onSubmit, submitting }) {
  const [values, setValues] = useState({
    ...EMPTY_TRANSACTION,
  });

  function handleChange(name, val) {
    setValues((prev) => ({
      ...prev,
      [name]: val,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    const payload = {
      ...values,

      Age: Number(values.Age),
      Transaction_Amount: Number(values.Transaction_Amount),
      Account_Balance: Number(values.Account_Balance),
    };

    onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">

      {FIELD_GROUPS.map((group) => (
        <fieldset
          key={group.title}
          className="rounded-xl border border-panelLine bg-panel/40 p-5"
        >

          <legend className="px-2">
            <span className="rounded-md border border-signal/20 bg-signal/10 px-2.5 py-1 font-data text-[10px] uppercase tracking-[0.2em] text-signal">
              {group.title}
            </span>
          </legend>

          <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">

            {group.fields.map((field) => (
              <label
                key={field.name}
                className="block text-xs font-medium text-muted"
              >
                <span className="mb-1.5 block">
                  {field.label}
                </span>

                <Field
                  field={field}
                  value={values[field.name]}
                  onChange={handleChange}
                />
              </label>
            ))}

          </div>
        </fieldset>
      ))}

      <button
        type="submit"
        disabled={submitting}
        className="group flex w-full items-center justify-center gap-3 rounded-lg bg-signal px-5 py-3.5 font-semibold text-ink shadow-lg shadow-signal/10 transition hover:-translate-y-0.5 hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
      >
        {submitting ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink/30 border-t-ink" />
            Screening transaction…
          </>
        ) : (
          <>
            Screen transaction
            <span className="transition-transform group-hover:translate-x-1">
              →
            </span>
          </>
        )}
      </button>

      <p className="text-center text-[11px] text-muted">
        Analysis uses the trained fraud detection model and historical
        fraud-location intelligence.
      </p>

    </form>
  );
}