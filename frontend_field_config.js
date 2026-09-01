// Field config shared by TransactionForm. Kept separate from the
// component so the field list stays a single source of truth that
// mirrors backend.py's TransactionRequest model exactly - add a field
// to that Pydantic model, add it here, and the form picks it up.

export const FIELD_GROUPS = [
  {
    title: "Customer",
    fields: [
      { name: "Gender", label: "Gender", type: "select", options: ["Male", "Female", "Other"] },
      { name: "Age", label: "Age", type: "number" },
      { name: "State", label: "State", type: "text" },
      { name: "City", label: "City", type: "text" },
      { name: "Bank_Branch", label: "Bank branch", type: "text" },
      { name: "Account_Type", label: "Account type", type: "select", options: ["Savings", "Business", "Current"] },
    ],
  },
  {
    title: "Transaction",
    fields: [
      { name: "Transaction_Date", label: "Date", type: "date-dmy", placeholder: "DD-MM-YYYY" },
      { name: "Transaction_Time", label: "Time", type: "time" },
      { name: "Transaction_Amount", label: "Amount (₹)", type: "number", step: "0.01" },
      {
        name: "Transaction_Type",
        label: "Transaction type",
        type: "select",
        options: ["Transfer", "Bill Payment", "Withdrawal", "Deposit", "Purchase"],
      },
      { name: "Merchant_Category", label: "Merchant category", type: "text" },
      { name: "Account_Balance", label: "Account balance (₹)", type: "number", step: "0.01" },
    ],
  },
  {
    title: "Device & location",
    fields: [
      { name: "Transaction_Device", label: "Transaction device", type: "text" },
      { name: "Transaction_Location", label: "Transaction location", type: "text", placeholder: "City, State" },
      { name: "Device_Type", label: "Device type", type: "select", options: ["Mobile", "Desktop", "POS", "ATM"] },
    ],
  },
];

export const EMPTY_TRANSACTION = FIELD_GROUPS.flatMap((g) => g.fields).reduce(
  (acc, f) => ({ ...acc, [f.name]: "" }),
  {}
);
