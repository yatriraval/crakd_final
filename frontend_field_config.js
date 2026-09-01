// Field configuration for the transaction intake form.

export const FIELD_GROUPS = [
  {
    title: "Customer",
    fields: [
      {
        name: "Gender",
        label: "Gender",
        type: "select",
        options: ["Male", "Female", "Other"],
      },
      {
        name: "Age",
        label: "Age",
        type: "number",
      },
      {
        name: "State",
        label: "State",
        type: "text",
      },
      {
        name: "City",
        label: "City",
        type: "text",
      },
      {
        name: "Bank_Branch",
        label: "Bank branch",
        type: "text",
      },
      {
        name: "Account_Type",
        label: "Account type",
        type: "select",
        options: ["Savings", "Business", "Current"],
      },
    ],
  },

  {
    title: "Transaction",
    fields: [
      {
        name: "Transaction_Date",
        label: "Date",
        type: "date",
      },
      {
        name: "Transaction_Time",
        label: "Time",
        type: "time",
      },
      {
        name: "Transaction_Amount",
        label: "Amount (₹)",
        type: "number",
        step: "0.01",
      },
      {
        name: "Transaction_Type",
        label: "Transaction type",
        type: "select",
        options: [
          "Transfer",
          "Bill Payment",
          "Withdrawal",
          "Deposit",
          "Purchase",
        ],
      },
      {
        name: "Merchant_Category",
        label: "Merchant category",
        type: "text",
      },
      {
        name: "Account_Balance",
        label: "Account balance (₹)",
        type: "number",
        step: "0.01",
      },
    ],
  },

  {
    title: "Device & location",
    fields: [
      {
        name: "Transaction_Device",
        label: "Transaction device",
        type: "text",
      },
      {
        name: "Transaction_Location",
        label: "Transaction location",
        type: "text",
        placeholder: "City, State",
      },
      {
        name: "Device_Type",
        label: "Device type",
        type: "select",
        options: ["Mobile", "Desktop", "POS", "ATM"],
      },
    ],
  },
];

export const EMPTY_TRANSACTION = {
  Gender: "Male",
  Age: "26",
  State: "Delhi",
  City: "New Delhi",
  Bank_Branch: "New Delhi Branch",
  Account_Type: "Savings",

  Transaction_Date: new Date().toISOString().split("T")[0],
  Transaction_Time: "02:47",

  Transaction_Amount: "48500",
  Transaction_Type: "Withdrawal",
  Merchant_Category: "Electronics",
  Account_Balance: "51200",

  Transaction_Device: "ATM",
  Transaction_Location: "New Delhi, Delhi",
  Device_Type: "ATM",
};