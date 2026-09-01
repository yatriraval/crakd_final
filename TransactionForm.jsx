import { useState } from "react";
import { FIELD_GROUPS, EMPTY_TRANSACTION } from "../frontend_field_config.js";

function Field({ field, value, onChange }) {
  const base =
    "w-full bg-ink border border-panelLine rounded-sm px-3 py-2 text-sm text-paper placeholder:text-muted/60 focus:outline-none focus:border-signal";

  if (field.type === "select") {
    return (
      <select className={base} value={value} onChange={(e) => onChange(field.name, e.target.value)} required>
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
  const [values, setValues] = useState(EMPTY_TRANSACTION);

  function handleChange(name, val) {
    setValues((prev) => ({ ...prev, [name]: val }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    // Cast numeric fields before sending — backend.py's TransactionRequest
    // expects Age/Transaction_Amount/Account_Balance as numbers, not strings.
    const payload = {
      ...values,
      Age: Number(values.Age),
      Transaction_Amount: Number(values.Transaction_Amount),
      Account_Balance: Number(values.Account_Balance),
    };
    onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {FIELD_GROUPS.map((group) => (
        <fieldset key={group.title} className="border border-panelLine rounded-sm p-4">
          <legend className="font-data text-xs text-signal px-1">{group.title}</legend>
          <div className="grid grid-cols-2 gap-3 mt-1">
            {group.fields.map((field) => (
              <label key={field.name} className="text-xs text-muted space-y-1 block">
                {field.label}
                <Field field={field} value={values[field.name]} onChange={handleChange} />
              </label>
            ))}
          </div>
        </fieldset>
      ))}

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-signal text-ink font-medium py-3 rounded-sm hover:brightness-110 disabled:opacity-50 transition"
      >
        {submitting ? "Screening transaction…" : "Screen transaction"}
      </button>
    </form>
  );
}
